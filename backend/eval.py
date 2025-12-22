import time
import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "database": "logiq",
    "user": "admin",
    "password": "password",
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def main():
    """
    Lightweight evaluation helper for Objective 4.

    It prints:
      - Total logs ingested
      - Time span covered by logs (start/end, approximate end-to-end latency window)
      - Total anomalies, and split by Frequency vs Pattern
    """
    conn = get_conn()
    cur = conn.cursor()

    print("📊 LogIQ Evaluation Summary")

    # 1) Basic log stats
    cur.execute(
        """
        SELECT
          COUNT(*) AS total,
          MIN(received_at) AS first_ts,
          MAX(received_at) AS last_ts
        FROM logs
        """
    )
    total, first_ts, last_ts = cur.fetchone()
    print(f"\n🧾 Logs:")
    print(f"  Total logs ingested: {total}")
    if total > 0 and first_ts and last_ts:
        span = (last_ts - first_ts).total_seconds()
        print(f"  Time span (first -> last): {first_ts} -> {last_ts} (~{span:.1f}s)")

    # 2) Anomaly stats
    cur.execute("SELECT COUNT(*) FROM anomalies")
    anomalies_total = cur.fetchone()[0]
    print(f"\n🚨 Anomalies:")
    print(f"  Total anomalies recorded: {anomalies_total}")

    cur.execute(
        """
        SELECT
          CASE
            WHEN description LIKE '[FREQUENCY]%%' THEN 'Frequency'
            WHEN description LIKE '[PATTERN]%%' THEN 'Pattern'
            ELSE 'Other'
          END AS type,
          COUNT(*) AS cnt
        FROM anomalies
        GROUP BY 1
        ORDER BY 1
        """
    )
    rows = cur.fetchall()
    for t, c in rows:
        print(f"  {t:9}: {c}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\n⏱  Evaluation script runtime: {time.time() - start:.2f}s")


