"""Seed synthetic data and print SQLite query plan/timing snapshots.

Learning loop:
1) Capture a baseline query plan + latency.
2) Change one thing (usually an index).
3) Capture plan + latency again.
4) Keep the change only if it helps the target query.

What this script demonstrates:
- Baseline query profiling with `EXPLAIN QUERY PLAN` + avg/p95 timing.
- Before/after index experiment for exact-match lookup.
- Before/after index experiment for `LIKE 'prefix%'`, including collation caveats.

Typical usage:
- First pass (quick): `uv run python scripts/sqlite_profile_demo.py --commands 10000 --runs 7`
- More stable p95: `uv run python scripts/sqlite_profile_demo.py --commands 10000 --runs 30`
- Isolated DB: `--db "/tmp/cmdstash-profile-demo.db"`
- Baseline-only run: `--skip-index-experiment`
"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from pathlib import Path
import random
import sqlite3
import statistics
import time

from cmdstash.storage import open_connection


TAG_POOL: tuple[str, ...] = (
    "git",
    "docker",
    "python",
    "linux",
    "kubernetes",
    "networking",
    "files",
    "testing",
    "ci",
    "security",
)


def parse_args() -> Namespace:
    parser = ArgumentParser(
        description="Seed demo data, then print EXPLAIN QUERY PLAN and timings.",
        formatter_class=RawDescriptionHelpFormatter,
        epilog="""\
Learning loop to use with this script:
  1) Start with a baseline run and inspect plan/timing output.
  2) Focus on a target query pattern (exact lookup, tag join, LIKE prefix).
  3) Compare before/after index experiments in this script.
  4) Keep only indexes that materially improve your real query.

Output notes:
  - avg: arithmetic mean over measured runs
  - p95: 95th percentile; highlights tail latency
  - SCAN vs SEARCH: planner hint for full scan vs indexed lookup

Examples:
  uv run python scripts/sqlite_profile_demo.py --commands 10000 --runs 7
  uv run python scripts/sqlite_profile_demo.py --commands 10000 --runs 30
  uv run python scripts/sqlite_profile_demo.py --db "/tmp/cmdstash-demo.db" --commands 20000
  uv run python scripts/sqlite_profile_demo.py --skip-index-experiment
""",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Optional DB path override. Defaults to cmdstash data dir.",
    )
    parser.add_argument(
        "--commands",
        type=int,
        default=10_000,
        help="Number of synthetic commands to seed (default: 10000).",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Timing runs per query (default: 5).",
    )
    parser.add_argument(
        "--skip-index-experiment",
        action="store_true",
        help="Skip the before/after index comparison experiment.",
    )
    return parser.parse_args()


def _seed_demo_data(connection: sqlite3.Connection, command_count: int) -> None:
    """Insert deterministic synthetic rows if the commands table is empty."""
    existing_count = connection.execute("SELECT COUNT(*) FROM commands").fetchone()[0]
    if existing_count > 0:
        print(f"Skipping seed: database already has {existing_count} command rows.")
        return

    rng = random.Random(42)
    now = "2026-01-01T00:00:00Z"

    with connection:
        for tag in TAG_POOL:
            connection.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (tag,))

        tag_ids = {
            name: tag_id
            for tag_id, name in connection.execute("SELECT id, name FROM tags").fetchall()
        }

        for i in range(command_count):
            command_text = f"demo-command-{i} --flag {i % 10}"
            description = f"Demo description for command {i}."
            cursor = connection.execute(
                """
                INSERT INTO commands(command, description, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (command_text, description, now, now),
            )
            command_id = cursor.lastrowid

            chosen_tags = rng.sample(TAG_POOL, k=3)
            for tag_name in chosen_tags:
                connection.execute(
                    "INSERT INTO command_tags(command_id, tag_id) VALUES (?, ?)",
                    (command_id, tag_ids[tag_name]),
                )

            for position in range(2):
                connection.execute(
                    """
                    INSERT INTO command_examples(command_id, example, position)
                    VALUES (?, ?, ?)
                    """,
                    (command_id, f"{command_text} --example {position}", position),
                )

    print(f"Seeded {command_count} commands with tags/examples.")


def _print_query_plan(connection: sqlite3.Connection, sql: str, params: tuple[object, ...]) -> None:
    print("\nEXPLAIN QUERY PLAN:")
    plan_rows = connection.execute(f"EXPLAIN QUERY PLAN {sql}", params).fetchall()
    for row in plan_rows:
        print(f"  - {row[3]}")


def _time_query(
    connection: sqlite3.Connection,
    *,
    label: str,
    sql: str,
    params: tuple[object, ...],
    runs: int,
) -> None:
    durations_ms: list[float] = []
    result_count = 0

    # Warm cache once before measurements.
    connection.execute(sql, params).fetchall()

    for _ in range(runs):
        start = time.perf_counter()
        rows = connection.execute(sql, params).fetchall()
        duration_ms = (time.perf_counter() - start) * 1000
        durations_ms.append(duration_ms)
        result_count = len(rows)

    avg_ms = statistics.mean(durations_ms)
    p95_ms = sorted(durations_ms)[max(0, int(runs * 0.95) - 1)]
    print(f"\n{label}")
    print(f"  rows: {result_count}")
    print(f"  avg:  {avg_ms:.2f} ms over {runs} runs")
    print(f"  p95:  {p95_ms:.2f} ms")


def _run_index_experiment(connection: sqlite3.Connection, *, runs: int) -> None:
    """Compare query plan and timing before/after adding an index."""
    query = """
    SELECT id, command_id, example
    FROM command_examples
    WHERE example = ?
    LIMIT 50
    """
    params = ("demo-command-99 --flag 9 --example 1",)
    index_name = "idx_demo_command_examples_example"
    create_index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON command_examples(example)"
    drop_index_sql = f"DROP INDEX IF EXISTS {index_name}"

    print("\n=== Index Experiment: command_examples(example) ===")
    print("Query pattern: exact match on command_examples.example")

    with connection:
        connection.execute(drop_index_sql)

    print("\nBefore index:")
    _print_query_plan(connection, query, params)
    _time_query(
        connection,
        label="Before index",
        sql=query,
        params=params,
        runs=runs,
    )

    with connection:
        connection.execute(create_index_sql)

    print("\nAfter index:")
    _print_query_plan(connection, query, params)
    _time_query(
        connection,
        label="After index",
        sql=query,
        params=params,
        runs=runs,
    )

    with connection:
        connection.execute(drop_index_sql)


def _run_like_prefix_experiment(connection: sqlite3.Connection, *, runs: int) -> None:
    """Show how a prefix LIKE query may or may not use an index."""
    query = """
    SELECT id, command
    FROM commands
    WHERE command LIKE ?
    LIMIT 50
    """
    params = ("demo-command-99%",)
    index_name = "idx_demo_commands_command_nocase"
    create_index_sql = (
        f"CREATE INDEX IF NOT EXISTS {index_name} ON commands(command COLLATE NOCASE)"
    )
    drop_index_sql = f"DROP INDEX IF EXISTS {index_name}"
    pragma_sql = "PRAGMA case_sensitive_like = OFF"

    print("\n=== LIKE Prefix Experiment: commands(command) ===")
    print("Query pattern: command LIKE 'demo-command-99%'")
    print("Note: LIKE index usage depends on collation + pattern + SQLite settings.")

    connection.execute(pragma_sql)
    with connection:
        connection.execute(drop_index_sql)

    print("\nBefore NOCASE index:")
    _print_query_plan(connection, query, params)
    _time_query(
        connection,
        label="Before NOCASE index",
        sql=query,
        params=params,
        runs=runs,
    )

    with connection:
        connection.execute(create_index_sql)

    print("\nAfter NOCASE index:")
    _print_query_plan(connection, query, params)
    _time_query(
        connection,
        label="After NOCASE index",
        sql=query,
        params=params,
        runs=runs,
    )

    with connection:
        connection.execute(drop_index_sql)


def main() -> None:
    args = parse_args()
    db_path = Path(args.db) if args.db is not None else None

    with open_connection(db_path) as connection:
        _seed_demo_data(connection, args.commands)

        query_by_tag = """
        SELECT c.id, c.command, c.description
        FROM commands AS c
        JOIN command_tags AS ct ON ct.command_id = c.id
        JOIN tags AS t ON t.id = ct.tag_id
        WHERE t.name = ?
        ORDER BY c.id DESC
        LIMIT 50
        """
        query_text_like = """
        SELECT id, command, description
        FROM commands
        WHERE command LIKE ?
        ORDER BY id DESC
        LIMIT 50
        """

        print(f"\nDatabase path: {db_path or '(default cmdstash path)'}")
        _print_query_plan(connection, query_by_tag, ("docker",))
        _time_query(
            connection,
            label="Query A: filter commands by tag name",
            sql=query_by_tag,
            params=("docker",),
            runs=args.runs,
        )

        _print_query_plan(connection, query_text_like, ("%demo-command-99%",))
        _time_query(
            connection,
            label="Query B: text lookup with LIKE",
            sql=query_text_like,
            params=("%demo-command-99%",),
            runs=args.runs,
        )

        if not args.skip_index_experiment:
            _run_index_experiment(connection, runs=args.runs)
            _run_like_prefix_experiment(connection, runs=args.runs)


if __name__ == "__main__":
    main()
