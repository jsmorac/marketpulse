"""Auditoría del diccionario de tecnologías contra TODO el corpus de ofertas.

Analiza el texto completo de todas las ofertas capturadas (no solo las que
cayeron en 'other'), y cuenta palabras frecuentes que NO son alias conocidos
del seed. Esto detecta tecnologías mencionadas en ofertas que ya matchearon
algo más (ej. una oferta Python que también menciona 'Polars', invisible si
solo miráramos el bucket 'other').

Uso: docker compose run --rm dagster-webserver python -m analytics.other_bucket_report

No es parte del pipeline automático. Se corre manualmente para decidir qué
agregar a known_technologies.csv. Ver seguimiento.md para el contexto.
"""

from __future__ import annotations

import html
import re
from collections import Counter
from pathlib import Path

from db.connection import connect

MIN_WORD_LEN = 3
MIN_FREQUENCY = 3
TOP_N = 120

NOISE_WORDS_PATH = Path(__file__).parent / "noise_words.txt"

BASIC_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "you",
    "our",
    "are",
    "this",
    "that",
    "have",
    "will",
    "your",
    "from",
    "who",
    "what",
    "not",
    "all",
    "can",
    "has",
    "was",
    "were",
    "been",
    "would",
    "could",
    "should",
    "about",
    "into",
    "over",
    "than",
}

TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#]{1,}")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
SPAM_DISCLAIMER_PATTERN = re.compile(
    r"please mention the word.*?read this and see they.re human\.",
    re.IGNORECASE | re.DOTALL,
)


def load_noise_words() -> set[str]:
    if not NOISE_WORDS_PATH.exists():
        return set()
    lines = NOISE_WORDS_PATH.read_text(encoding="utf-8").splitlines()
    return {line.strip().lower() for line in lines if line.strip()}


def load_known_aliases(conn) -> set[str]:
    """Aliases ya reconocidos por el seed — se excluyen del conteo, no aportan nada nuevo."""
    with conn.cursor() as cur:
        cur.execute("select alias from analytics.known_technologies")
        return {row[0].lower() for row in cur.fetchall()}


def fetch_all_texts(conn) -> list[str]:
    """Texto completo de TODAS las ofertas capturadas, sin filtrar por kind."""
    texts: list[str] = []

    with conn.cursor() as cur:
        cur.execute(
            "select payload->>'title' as title, payload->>'description_html' as description "
            "from raw.himalayas_jobs"
        )
        for title, description in cur.fetchall():
            texts.append(f"{title or ''} {description or ''}")

        cur.execute(
            "select payload->>'position' as title, payload->>'description' as description "
            "from raw.remoteok_jobs"
        )
        for title, description in cur.fetchall():
            texts.append(f"{title or ''} {description or ''}")

        cur.execute("select payload->>'text' as body from raw.hackernews_jobs")
        for (body,) in cur.fetchall():
            texts.append(body or "")

    return texts


def looks_like_hash(word: str) -> bool:
    """Heurística: strings largos con mezcla rara de letras/números y pocas vocales
    suelen ser IDs de tracking, no palabras reales (ej. 'rmtq5ljezmc4xoduumtyy')."""
    if len(word) < 12:
        return False
    vowels = sum(1 for c in word if c in "aeiou")
    has_digits = any(c.isdigit() for c in word)
    return has_digits or (vowels / len(word)) < 0.2


def tokenize(text: str) -> list[str]:
    without_disclaimer = SPAM_DISCLAIMER_PATTERN.sub(" ", text)
    decoded = html.unescape(without_disclaimer)
    clean = HTML_TAG_PATTERN.sub(" ", decoded)
    tokens = [t.lower() for t in TOKEN_PATTERN.findall(clean)]
    return [t for t in tokens if not looks_like_hash(t)]


def main() -> None:
    noise_words = load_noise_words()

    with connect() as conn:
        known_aliases = load_known_aliases(conn)
        texts = fetch_all_texts(conn)

    stopwords = BASIC_STOPWORDS | noise_words | known_aliases

    print(f"Ofertas analizadas (todo el corpus): {len(texts)}")
    print(f"Aliases ya conocidos por el seed (excluidos del conteo): {len(known_aliases)}\n")

    counter: Counter[str] = Counter()
    for text in texts:
        for word in tokenize(text):
            if len(word) < MIN_WORD_LEN or word in stopwords or word.isdigit():
                continue
            counter[word] += 1

    print(f"Top {TOP_N} palabras NO reconocidas por el seed (frecuencia mínima {MIN_FREQUENCY}):\n")
    shown = 0
    for word, count in counter.most_common():
        if count < MIN_FREQUENCY:
            break
        print(f"  {count:4}  {word}")
        shown += 1
        if shown >= TOP_N:
            break

    if shown == 0:
        print("  (nada por encima del umbral — bajá MIN_FREQUENCY o revisá noise_words.txt)")


if __name__ == "__main__":
    main()
