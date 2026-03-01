"""
PostgreSQL connection pool manager.
Used by auto_sync_service and other backend services when DATABASE_URL is set.
Falls back to raising a clear error if psycopg2 is not available.
"""
import os
import logging
from threading import Lock
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")
load_dotenv()

logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2 import pool as pg_pool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 not installed – PostgreSQL support unavailable. "
                   "Run: pip install psycopg2-binary")

_pool: "pg_pool.ThreadedConnectionPool | None" = None
_pool_lock = Lock()

DATABASE_URL = os.getenv("DATABASE_URL")


def _init_pool() -> "pg_pool.ThreadedConnectionPool":
    """Lazily initialise the connection pool (thread-safe)."""
    global _pool
    if _pool is not None:
        return _pool

    if not PSYCOPG2_AVAILABLE:
        raise RuntimeError("psycopg2-binary is required. Install it with: pip install psycopg2-binary")

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. Add it to backend/.env or Railway environment variables. "
            "Example: DATABASE_URL=postgresql://user:password@host:5432/dbname"
        )

    with _pool_lock:
        if _pool is None:
            _pool = pg_pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=DATABASE_URL,
            )
            logger.info("[PG] Connection pool initialised (min=1, max=10)")
    return _pool


def get_pg_connection() -> "psycopg2.extensions.connection":
    """
    Get a PostgreSQL connection from the pool.
    The connection is in autocommit=False mode (manual transaction control).
    Call release_pg_connection() when finished.
    """
    connection = _init_pool().getconn()
    # Ensure a clean state: not in a broken transaction from a previous use
    try:
        if connection.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
            connection.rollback()
    except Exception:
        pass
    connection.autocommit = False
    return connection


def release_pg_connection(conn, error: bool = False) -> None:
    """
    Return a connection to the pool.
    If *error* is True the connection will be reset before reuse.
    """
    if conn is None:
        return
    try:
        pool = _init_pool()
        pool.putconn(conn, close=error)
    except Exception as exc:
        logger.warning(f"[PG] Could not release connection to pool: {exc}")


def is_postgres() -> bool:
    """Return True when DATABASE_URL is configured and psycopg2 is available."""
    return PSYCOPG2_AVAILABLE and bool(DATABASE_URL)
