# db/connection.py
from __future__ import annotations

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def connect() -> psycopg.Connection:
    """Abre una conexión psycopg3 usando las variables DB_* del .env.

    El llamador es dueño de la transacción (commit / rollback / close).
    """
    load_dotenv(_PROJECT_ROOT / ".env", override=False)
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
