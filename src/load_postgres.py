"""Load curated project tables into PostgreSQL."""
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv

from src.config import FEATURES_FILE, TRANSACTIONS_FILE


def sql_type(dtype) -> str:
    if pd.api.types.is_integer_dtype(dtype): return "BIGINT"
    if pd.api.types.is_float_dtype(dtype): return "DOUBLE PRECISION"
    if pd.api.types.is_bool_dtype(dtype): return "BOOLEAN"
    if pd.api.types.is_datetime64_any_dtype(dtype): return "TIMESTAMP"
    return "TEXT"


def load_frame(conn, frame: pd.DataFrame, table: str) -> None:
    columns = list(frame.columns)
    ddl = ", ".join(f'"{column}" {sql_type(frame[column].dtype)}' for column in columns)
    with conn.cursor() as cursor:
        cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
        cursor.execute(f'CREATE TABLE "{table}" ({ddl})')
        with cursor.copy(f'COPY "{table}" ({", ".join(columns)}) FROM STDIN') as copy:
            for row in frame.itertuples(index=False, name=None): copy.write_row(tuple(None if pd.isna(value) else value for value in row))
        cursor.execute(f'CREATE INDEX idx_{table}_customer ON "{table}" (customer_id)')


def main() -> None:
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url: raise EnvironmentError("DATABASE_URL is required; copy .env.example to .env.")
    with psycopg.connect(database_url) as conn:
        load_frame(conn, pd.read_parquet(TRANSACTIONS_FILE), "transactions")
        load_frame(conn, pd.read_parquet(FEATURES_FILE), "customer_features")
    print("Loaded transactions and customer_features into PostgreSQL.")


if __name__ == "__main__":
    main()
