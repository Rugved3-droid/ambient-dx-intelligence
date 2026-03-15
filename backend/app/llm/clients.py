"""LLM client singletons — OpenAI and Anthropic."""

from __future__ import annotations

import anthropic
import openai

from app.config import OPENAI_API_KEY, ANTHROPIC_API_KEY

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
