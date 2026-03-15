"""Centralized configuration — environment variables and CLI flags."""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

USE_CACHE = "--cached" in sys.argv or "--cache" in sys.argv
USE_IRIS = "--iris" in sys.argv

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

IRIS_HOST = os.getenv("IRIS_HOST", "localhost")
IRIS_PORT = int(os.getenv("IRIS_PORT", "1972"))
IRIS_NAMESPACE = os.getenv("IRIS_NAMESPACE", "USER")
IRIS_USERNAME = os.getenv("IRIS_USERNAME", "demo")
IRIS_PASSWORD = os.getenv("IRIS_PASSWORD", "demo")
