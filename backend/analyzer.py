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

    # In-memory set of templates we've already seen during the current run's
    # LEARNING phase. This makes pattern anomalies depend on the normal
    # baseline of THIS run (e.g., the normal portion of final_demo.log),
    # not on everything that ever existed in the DB.
    seen_templates = set()

    while True:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), ARRAY_AGG(DISTINCT log_template) FROM logs WHERE received_at > NOW() - INTERVAL '2 seconds'")
            row = cursor.fetchone()
            current_count = row[0]
            recent_templates = row[1] or []
            
            # 1. POPULATE PHASE (learning baseline for rate + normal templates)
            if len(history) < 5:
                history.append(current_count)
                # During learning, treat all observed templates as "normal".
                for tpl in recent_templates:
                    if tpl is not None:
                        seen_templates.add(tpl)
                print(f"[Learning] Data points: {len(history)}/5 | Current Traffic: {current_count} | Known templates: {len(seen_templates)}")
                time.sleep(CHECK_INTERVAL)
                continue

            # 2. STATISTICS PHASE
            mean = np.mean(history)
            std_dev = np.std(history)
            effective_std = max(std_dev, 1.0, mean * 0.05)
            threshold = mean + (SIGMA_MULTIPLIER * effective_std)
            
            # 3. DETECTION PHASE - FREQUENCY ANOMALIES (rate spikes)
            if current_count > threshold:
                # FIX: Convert numpy types to standard Python floats
                z_score = float((current_count - mean) / effective_std)
                
                print(f"\n🚨 ANOMALY DETECTED! 🚨")
                print(f"   Actual Traffic: {current_count} logs/s")
                print(f"   Expected Max:   {int(threshold)} logs/s")
                print(f"   Deviation:      {z_score:.2f}x Sigma")
                
                # Log to DB
                cursor.execute("""
                    INSERT INTO anomalies (log_count, description, deviation_score)
                    VALUES (%s, %s, %s)
                """, (current_count, f"[FREQUENCY] Spike: {current_count} (Limit: {int(threshold)})", z_score))
                
                conn.commit()
                print("   -> Saved to DB ✅")
                
                # Do not add anomaly to history
            else:
                history.append(current_count)
                print(f"[OK] Traffic: {current_count} | Threshold: {int(threshold)} | Baseline: {int(mean)}")

            # 4. DETECTION PHASE - PATTERN ANOMALIES (new templates)
            pattern_anomalies = []
            for tpl in recent_templates:
                if tpl not in seen_templates:
                    seen_templates.add(tpl)
                    pattern_anomalies.append(tpl)

            for tpl in pattern_anomalies:
                short_tpl = tpl if len(tpl) <= 180 else tpl[:177] + "..."
                print("\n🧩 NEW TEMPLATE DETECTED!")
                print(f"   Template: {short_tpl}")

                cursor.execute(
                    """
                    INSERT INTO anomalies (log_count, description, deviation_score)
                    VALUES (%s, %s, %s)
                    """,
                    (0, f"[PATTERN] New template observed: {short_tpl}", 0.0),
                )

            if pattern_anomalies:
                conn.commit()

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
