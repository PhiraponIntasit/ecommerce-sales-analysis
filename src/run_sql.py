"""
Run every query in sql/ against the processed CSVs with DuckDB and print the results.

    python src/run_sql.py            # run all
    python src/run_sql.py 04 06      # run only files starting with 04 and 06
"""

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"


def main(prefixes: list[str]) -> None:
    con = duckdb.connect()
    # Paths inside the .sql files are relative to the project root.
    con.execute(f"SET file_search_path = '{ROOT.as_posix()}'")
    con.execute((SQL_DIR / "00_setup_views.sql").read_text())

    for path in sorted(SQL_DIR.glob("[0-9][0-9]_*.sql")):
        if path.name.startswith("00_") or (prefixes and not any(path.name.startswith(p) for p in prefixes)):
            continue
        print(f"\n=== {path.name} ===")
        statements = [s for s in path.read_text().split(";") if s.strip() and not all(
            ln.strip().startswith("--") or not ln.strip() for ln in s.splitlines())]
        for stmt in statements:
            print(con.sql(stmt).df().to_string(index=False))
            print()


if __name__ == "__main__":
    main(sys.argv[1:])
