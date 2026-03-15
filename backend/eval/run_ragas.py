"""Ragas RAG evaluation — compares ChromaDB vs IRIS retrieval + Q&A quality.

Usage (from backend/):
    python -m eval.run_ragas                    # ChromaDB only
    python -m eval.run_ragas --iris             # ChromaDB + IRIS side-by-side
    python -m eval.run_ragas --retrieval-only   # skip LLM generation (cheaper)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd

_BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_DIR))

from eval.dataset import GOLDEN_DATASET

RESULTS_FILE = Path(__file__).resolve().parent / "results.json"


# ── Backend initialisation ─────────────────────────────────────────────

def _init_backend(use_iris: bool):
    from app.data.patient_manager import PatientDataManager
    from app.retrieval.engine import RAGEngine

    pm = PatientDataManager()
    pm.initialize(skip_chromadb=use_iris)
    return RAGEngine(pm, use_iris=use_iris)


# ── Sample collection ──────────────────────────────────────────────────

async def _collect_samples(
    rag,
    dataset: list[dict],
    retrieval_only: bool = False,
) -> list[dict]:
    """Run retrieval (+ optional generation) for every golden question."""
    samples: list[dict] = []
    for idx, entry in enumerate(dataset, 1):
        question = entry["question"]
        print(f"  [{idx}/{len(dataset)}] {question[:65]}")

        retrieved = rag.retrieve(
            question,
            n_results=12,
            categories=[
                "vitals", "labs", "medications", "allergies",
                "problems", "notes", "imaging", "history",
            ],
            include_safety=True,
        )
        contexts = [item["text"] for item in retrieved]

        if retrieval_only:
            response = ""
        else:
            from app.llm.answerer import quick_answer

            result = await quick_answer(question, retrieved)
            response = result.get("answer", "")

        samples.append(
            {
                "user_input": question,
                "retrieved_contexts": contexts,
                "response": response,
                "reference": entry["ground_truth"],
            }
        )
    return samples


# ── Ragas evaluation ───────────────────────────────────────────────────

def _evaluate(samples: list[dict], llm, retrieval_only: bool = False):
    from ragas import EvaluationDataset, evaluate
    from ragas.metrics import (
        Faithfulness,
        FactualCorrectness,
        LLMContextPrecisionWithReference,
        LLMContextRecall,
    )

    dataset = EvaluationDataset.from_list(samples)

    if retrieval_only:
        metrics = [LLMContextRecall(), LLMContextPrecisionWithReference()]
    else:
        metrics = [
            Faithfulness(),
            LLMContextRecall(),
            LLMContextPrecisionWithReference(),
            FactualCorrectness(),
        ]

    return evaluate(dataset=dataset, metrics=metrics, llm=llm)


# ── Score extraction helpers ───────────────────────────────────────────

_SKIP_COLS = frozenset(
    {
        "user_input",
        "retrieved_contexts",
        "response",
        "reference",
        "reference_contexts",
    }
)


def _extract(result):
    """Return (aggregate_dict, per_question_list, metric_names) from a Ragas result."""
    df = result.to_pandas()
    metric_cols = [
        c for c in df.columns if c not in _SKIP_COLS and df[c].dtype.kind == "f"
    ]
    aggregate = {col: round(float(df[col].mean()), 4) for col in metric_cols}

    per_question: list[dict] = []
    for _, row in df.iterrows():
        entry: dict = {"user_input": str(row.get("user_input", ""))}
        for col in metric_cols:
            val = row[col]
            entry[col] = round(float(val), 4) if pd.notna(val) else None
        per_question.append(entry)

    return aggregate, per_question, metric_cols


# ── Reporting ──────────────────────────────────────────────────────────

def _print_report(chromadb_agg, metric_cols, iris_agg=None):
    hdr = "\n" + "=" * 68 + "\n  RAGAS EVALUATION RESULTS\n" + "=" * 68

    if iris_agg is None:
        print(hdr)
        print(f"\n  {'Metric':<40} {'ChromaDB':>10}")
        print("  " + "-" * 52)
        for m in metric_cols:
            print(f"  {m:<40} {chromadb_agg[m]:>8.4f}")
    else:
        print(hdr)
        print(
            f"\n  {'Metric':<40} {'ChromaDB':>10} {'IRIS':>10} {'Delta':>10}"
        )
        print("  " + "-" * 72)
        for m in metric_cols:
            c_val = chromadb_agg[m]
            i_val = iris_agg.get(m, float("nan"))
            delta = c_val - i_val
            sign = "+" if delta >= 0 else ""
            print(
                f"  {m:<40} {c_val:>8.4f}   {i_val:>8.4f}   {sign}{delta:>7.4f}"
            )

    print("\n" + "=" * 68 + "\n")


def _save_results(
    chromadb_agg,
    chromadb_detail,
    iris_agg=None,
    iris_detail=None,
):
    def _default(obj):
        if hasattr(obj, "item"):
            return obj.item()
        if hasattr(obj, "__float__"):
            return float(obj)
        return str(obj)

    out: dict = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    out["chromadb"] = {"aggregate": chromadb_agg, "per_question": chromadb_detail}
    if iris_agg is not None:
        out["iris"] = {"aggregate": iris_agg, "per_question": iris_detail}

    with open(RESULTS_FILE, "w") as f:
        json.dump(out, f, indent=2, default=_default)
    print(f"Results saved to {RESULTS_FILE}\n")


# ── Main ───────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Ragas RAG evaluation for Ambient Dx Intelligence"
    )
    parser.add_argument(
        "--iris",
        action="store_true",
        help="Also evaluate the IRIS backend (requires Docker)",
    )
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Evaluate retrieval quality only — skip LLM generation (cheaper)",
    )
    args = parser.parse_args()

    from ragas.llms import llm_factory

    evaluator_llm = llm_factory("gpt-4o-mini")

    # ── ChromaDB ────────────────────────────────────────────────────
    print("\n[1] Initialising ChromaDB backend ...")
    chromadb_rag = _init_backend(use_iris=False)

    print("[2] Collecting samples (ChromaDB) ...")
    chromadb_samples = asyncio.run(
        _collect_samples(chromadb_rag, GOLDEN_DATASET, args.retrieval_only)
    )

    print("[3] Running Ragas evaluation (ChromaDB) ...")
    t0 = time.time()
    chromadb_result = _evaluate(
        chromadb_samples, evaluator_llm, args.retrieval_only
    )
    print(f"    Done in {time.time() - t0:.1f}s")

    chromadb_agg, chromadb_detail, metric_cols = _extract(chromadb_result)

    # ── IRIS (optional) ─────────────────────────────────────────────
    iris_agg = iris_detail = None
    if args.iris:
        try:
            print("\n[3b] Initialising IRIS backend ...")
            iris_rag = _init_backend(use_iris=True)

            print("[3c] Collecting samples (IRIS) ...")
            iris_samples = asyncio.run(
                _collect_samples(iris_rag, GOLDEN_DATASET, args.retrieval_only)
            )

            print("[3d] Running Ragas evaluation (IRIS) ...")
            t0 = time.time()
            iris_result = _evaluate(
                iris_samples, evaluator_llm, args.retrieval_only
            )
            print(f"     Done in {time.time() - t0:.1f}s")

            iris_agg, iris_detail, _ = _extract(iris_result)
        except Exception as exc:
            print(f"\n  WARNING: IRIS backend unavailable: {exc}")
            print("  Continuing with ChromaDB results only.\n")

    # ── Report ──────────────────────────────────────────────────────
    print("\n[4] Generating report ...")
    _print_report(chromadb_agg, metric_cols, iris_agg)
    _save_results(chromadb_agg, chromadb_detail, iris_agg, iris_detail)


if __name__ == "__main__":
    main()
