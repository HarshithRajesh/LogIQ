import time
import psycopg2
import numpy as np
from collections import deque

# --- CONFIGURATION ---
WINDOW_SIZE = 10      
CHECK_INTERVAL = 2    
SIGMA_MULTIPLIER = 4  

history = deque(maxlen=WINDOW_SIZE)

def get_db_connection():
    try:
        return psycopg2.connect(
            host="localhost", database="logiq", user="admin", password="password"
        )
    except:
        return None

def analyze():
    print("🧠 AI Analyzer Started.")
    print("⏳ Waiting for data stream to build baseline...")
    
    conn = get_db_connection()
    while conn is None:
        print("Waiting for DB...")
        time.sleep(2)
        conn = get_db_connection()

    while True:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM logs WHERE received_at > NOW() - INTERVAL '2 seconds'")
            current_count = cursor.fetchone()[0]
            
            # 1. POPULATE PHASE
            if len(history) < 5:
                history.append(current_count)
                print(f"[Learning] Data points: {len(history)}/5 | Current Traffic: {current_count}")
                time.sleep(CHECK_INTERVAL)
                continue

            # 2. STATISTICS PHASE
            mean = np.mean(history)
            std_dev = np.std(history)
            effective_std = max(std_dev, 1.0, mean * 0.05)
            threshold = mean + (SIGMA_MULTIPLIER * effective_std)
            
            # 3. DETECTION PHASE
            if current_count > threshold:
                # FIX: Convert numpy types to standard Python floats
                z_score = float((current_count - mean) / effective_std)
                
                print(f"\n🚨 ANOMALY DETECTED! 🚨")
                print(f"   Actual Traffic: {current_count} logs/2s")
                print(f"   Expected Max:   {int(threshold)} logs/2s")
                print(f"   Deviation:      {z_score:.2f}x Sigma")
                
                # Log to DB
                cursor.execute("""
                    INSERT INTO anomalies (log_count, description, deviation_score)
                    VALUES (%s, %s, %s)
                """, (current_count, f"Spike: {current_count} (Limit: {int(threshold)})", z_score))
                
                conn.commit()
                print("   -> Saved to DB ✅")
                
                # Do not add anomaly to history
            else:
                history.append(current_count)
                print(f"[OK] Traffic: {current_count} | Threshold: {int(threshold)} | Baseline: {int(mean)}")

            cursor.close()
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"Error: {e}")
            # Try to reconnect if DB connection dropped
            try:
                conn.rollback() 
            except:
                conn = get_db_connection()

if __name__ == "__main__":
    analyze()
