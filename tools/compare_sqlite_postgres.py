#!/usr/bin/env python3
"""Compare table row counts (and users) between local SQLite and remote Postgres.

Usage:
  python tools/compare_sqlite_postgres.py --sqlite db.sqlite3 --pg "<DATABASE_URL>"

"""
import argparse
import sqlite3
import sys
from urllib.parse import urlparse

try:
    import psycopg
except Exception:
    print('psycopg not installed; please install psycopg or psycopg2-binary', file=sys.stderr)
    raise


def get_sqlite_tables(sqlite_path):
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'""")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return tables


def get_sqlite_count(sqlite_path, table):
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT(*) FROM \"{table}\"")
        return cur.fetchone()[0]
    except Exception as e:
        return None
    finally:
        conn.close()


def get_pg_count(pg_conn, table):
    try:
        with pg_conn.cursor() as cur:
            cur.execute(f'SELECT COUNT(*) FROM "{table}"')
            return cur.fetchone()[0]
    except Exception:
        return None


def compare(sqlite_path, pg_url):
    print('Using sqlite:', sqlite_path)
    print('Using pg url:', pg_url)

    tables = get_sqlite_tables(sqlite_path)
    print(f'Found {len(tables)} sqlite tables (showing first 200):')
    for t in tables[:200]:
        print(' -', t)

    # Connect to Postgres
    pg_conn = psycopg.connect(pg_url)

    mismatches = []
    print('\nTable counts comparison:')
    print(f"{'table':40} {'sqlite':>10} {'postgres':>10}  status")
    for table in tables:
        s_cnt = get_sqlite_count(sqlite_path, table)
        p_cnt = get_pg_count(pg_conn, table)
        status = 'OK' if s_cnt == p_cnt else 'MISMATCH' if p_cnt is not None else 'MISSING_IN_PG'
        print(f"{table:40} {str(s_cnt):>10} {str(p_cnt):>10}  {status}")
        if status != 'OK':
            mismatches.append((table, s_cnt, p_cnt))

    # Extra: compare users by username if both tables exist
    user_table_candidates = ['accounts_customuser', 'auth_user', 'users_user']
    user_table = None
    for cand in user_table_candidates:
        if cand in tables:
            user_table = cand
            break

    if user_table:
        print(f"\nComparing users from table: {user_table}")
        # sqlite usernames
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        try:
            cur.execute(f"SELECT username, email FROM \"{user_table}\"")
            sqlite_users = set((r[0], r[1]) for r in cur.fetchall())
        except Exception:
            sqlite_users = set()
        finally:
            conn.close()

        with pg_conn.cursor() as cur:
            try:
                cur.execute(f'SELECT username, email FROM "{user_table}"')
                pg_users = set((r[0], r[1]) for r in cur.fetchall())
            except Exception:
                pg_users = set()

        missing_in_pg = sqlite_users - pg_users
        extra_in_pg = pg_users - sqlite_users
        print(f"Total users in sqlite: {len(sqlite_users)}, in pg: {len(pg_users)}")
        print(f"Users missing in PG (showing up to 50):")
        for u in list(missing_in_pg)[:50]:
            print(' -', u)
        print(f"Users extra in PG (showing up to 50):")
        for u in list(extra_in_pg)[:50]:
            print(' -', u)

    else:
        print('\nNo user table found in sqlite tables list; skipping username compare')

    pg_conn.close()

    if mismatches:
        print('\nSummary: MISMATCHES found in tables:')
        for t, s, p in mismatches:
            print(f" - {t}: sqlite={s} pg={p}")
        return 2
    print('\nAll table counts match between sqlite and Postgres (where Postgres table existed).')
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sqlite', default='db.sqlite3')
    p.add_argument('--pg', required=True)
    args = p.parse_args()
    rc = compare(args.sqlite, args.pg)
    sys.exit(rc)


if __name__ == '__main__':
    main()
