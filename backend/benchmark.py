import psycopg2
import time

def benchmark():
    conn = psycopg2.connect(host="localhost", database="logiq", user="admin", password="password")
    cur = conn.cursor()
    
    print("📊 Running Post-Demo Benchmark...")
    
    # Check Total Logs
    cur.execute("SELECT COUNT(*) FROM logs")
    total = cur.fetchone()[0]
    
    # Check Anomalies
    cur.execute("SELECT COUNT(*) FROM anomalies")
    anomalies = cur.fetchone()[0]
    
    print(f"Total Logs Processed: {total}")
    print(f"Anomalies Detected:   {anomalies}")
    
    if total >= 32000 and anomalies > 0:
        print("\n✅ SUCCESS: System captured all traffic and detected the attack.")
    else:
        print("\n⚠️ WARNING: Something was missed.")

if __name__ == "__main__":
    benchmark()
