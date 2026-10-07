"""Local account store for MadeIT Insights. Passwords are salted PBKDF2 hashes."""
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from datetime import datetime, timezone

from src.config import ROOT

AUTH_DB = ROOT / "data" / "madeit_insights_auth.sqlite3"
PBKDF2_ROUNDS = 600_000


def _connection() -> sqlite3.Connection:
    conn = sqlite3.connect(AUTH_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
        password_hash TEXT NOT NULL, created_at TEXT NOT NULL
    )""")
    return conn


def _hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${PBKDF2_ROUNDS}${salt.hex()}${digest.hex()}"


def _verify(password: str, stored: str) -> bool:
    algorithm, rounds, salt_hex, digest_hex = stored.split("$")
    if algorithm != "pbkdf2_sha256": return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds)).hex()
    return hmac.compare_digest(candidate, digest_hex)


def register(name: str, email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()
    if not name.strip(): return False, "Enter your name."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email): return False, "Enter a valid email address."
    if len(password) < 10: return False, "Use at least 10 characters for your password."
    try:
        with _connection() as conn:
            conn.execute("INSERT INTO users (email, name, password_hash, created_at) VALUES (?, ?, ?, ?)", (email, name.strip(), _hash(password), datetime.now(timezone.utc).isoformat()))
    except sqlite3.IntegrityError:
        return False, "An account already exists for this email."
    return True, "Account created. Please sign in."


def authenticate(email: str, password: str) -> dict | None:
    with _connection() as conn:
        row = conn.execute("SELECT id, email, name, password_hash FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    if not row or not _verify(password, row[3]): return None
    return {"id": row[0], "email": row[1], "name": row[2], "provider": "local"}
