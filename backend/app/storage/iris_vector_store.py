"""IRIS-backed vector store for clinical note chunks.

Vector table + HNSW index patterns from: intersystems-community/FHIR-AI-Hackathon-Kit
Embedding model (all-MiniLM-L6-v2, 384-dim) from both InterSystems repos.
"""

from __future__ import annotations

from app.storage.iris_db import get_cursor

VECTOR_TABLE = "AmbientDx.NoteChunks"
VECTOR_DIM = 384
_model = None


def _get_model():
    """Lazy-load the sentence-transformers model (avoids import cost at startup)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print(f"  [IRIS-Vec] Loaded all-MiniLM-L6-v2 ({VECTOR_DIM}-dim)")
    return _model


def embed_text(text: str) -> list[float]:
    model = _get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return model.encode(texts, normalize_embeddings=True).tolist()


def create_vector_table():
    """Create the NoteChunks vector table with HNSW index (idempotent)."""
    with get_cursor() as cur:
        try:
            cur.execute(f"DROP TABLE {VECTOR_TABLE}")
        except Exception:
            pass
        cur.execute(f"""
            CREATE TABLE {VECTOR_TABLE} (
                chunk_id VARCHAR(255),
                patient_id VARCHAR(50),
                category VARCHAR(100),
                source VARCHAR(500),
                event_time VARCHAR(50),
                content VARCHAR(''),
                embedding VECTOR(DOUBLE, {VECTOR_DIM})
            )
        """)
        print(f"  [IRIS-Vec] Created {VECTOR_TABLE}")


def create_hnsw_index():
    """Create HNSW index after bulk insertion (faster than auto-indexing)."""
    with get_cursor() as cur:
        try:
            cur.execute("DROP INDEX NoteChunkIdx ON AmbientDx.NoteChunks")
        except Exception:
            pass
        cur.execute(
            f"CREATE INDEX NoteChunkIdx ON {VECTOR_TABLE} (embedding) "
            "AS HNSW(Distance='DotProduct')"
        )
        print("  [IRIS-Vec] Created HNSW index")


def upsert_chunks(chunks: list[dict], patient_id: str = "P001"):
    """Embed chunk texts and insert into IRIS vector table.

    Each chunk dict must have: id, text, category, source, timestamp
    Uses %NOINDEX for faster bulk insert, then builds HNSW index separately.
    """
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    sql = (
        f"INSERT %NOINDEX INTO {VECTOR_TABLE} "
        "(chunk_id, patient_id, category, source, event_time, content, embedding) "
        "VALUES (?, ?, ?, ?, ?, ?, TO_VECTOR(?))"
    )

    rows = []
    for chunk, emb in zip(chunks, embeddings):
        rows.append((
            chunk["id"],
            patient_id,
            chunk["category"],
            chunk["source"],
            chunk["timestamp"],
            chunk["text"],
            str(emb),
        ))

    with get_cursor() as cur:
        for row in rows:
            cur.execute(sql, list(row))

    create_hnsw_index()
    return len(rows)


def similarity_search(
    query_text: str,
    patient_id: str | None = None,
    categories: list[str] | None = None,
    top_k: int = 10,
) -> list[dict]:
    """Vector similarity search over NoteChunks.

    Returns list of evidence dicts matching RAGEngine format.
    """
    query_vec = embed_text(query_text)
    query_vec_str = str(query_vec)

    sql = (
        f"SELECT TOP ? chunk_id, patient_id, category, source, event_time, content "
        f"FROM {VECTOR_TABLE}"
    )
    params: list = [top_k]
    conditions = []

    if patient_id:
        conditions.append("patient_id = ?")
        params.append(patient_id)

    if categories:
        placeholders = ", ".join(["?" for _ in categories])
        conditions.append(f"category IN ({placeholders})")
        params.extend(categories)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY VECTOR_DOT_PRODUCT(embedding, TO_VECTOR(?, double)) DESC"
    params.append(query_vec_str)

    with get_cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    results = []
    for i, r in enumerate(rows):
        chunk_id, pid, category, source, event_time, content = r
        results.append({
            "text": content,
            "source": source,
            "category": category,
            "timestamp": event_time or "",
            "relevance_score": round(1.0 - (i * 0.05), 2),
        })
    return results


def get_chunk_count(patient_id: str | None = None) -> int:
    with get_cursor() as cur:
        if patient_id:
            cur.execute(
                f"SELECT COUNT(*) FROM {VECTOR_TABLE} WHERE patient_id = ?",
                [patient_id],
            )
        else:
            cur.execute(f"SELECT COUNT(*) FROM {VECTOR_TABLE}")
        return cur.fetchone()[0]
