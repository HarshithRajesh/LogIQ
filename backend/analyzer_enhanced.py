#!/usr/bin/env python3
"""
Enhanced analyzer with mode support:
- Fresh: Clears logs table and starts fresh (for new demo runs)
- Continue: Analyzes existing logs (for resuming detection)
"""

import time
import psycopg2
import numpy as np
from collections import deque
import sys

# --- CONFIGURATION ---
WINDOW_SIZE = 10
CHECK_INTERVAL = 2
SIGMA_MULTIPLIER = 4
LEARNING_WINDOWS = 5   # Number of windows to learn baseline

history = deque(maxlen=WINDOW_SIZE)

def get_db_connection():
    try:
        return psycopg2.connect(
            host="localhost", database="logiq", user="admin", password="password"
        )
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def clear_tables():
    """Clear logs and anomalies tables for fresh demo run"""
    print("🧹 Clearing tables for fresh demo run...")
    conn = get_db_connection()
    if not conn:
        print("❌ Could not connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM anomalies;")
        cursor.execute("DELETE FROM logs;")
        # Try to clear known_templates if it exists
        try:
            cursor.execute("DELETE FROM known_templates;")
        except:
            pass  # Table might not exist, that's ok
        conn.commit()
        print("✅ Tables cleared successfully")
        return True
    except Exception as e:
        print(f"❌ Error clearing tables: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def analyze(mode="continue"):
    print("🧠 AI Analyzer Started.")
    
    if mode == "fresh":
        if not clear_tables():
            sys.exit(1)
    
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
    learning_phase = True
    baseline_established = False

    while True:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*), ARRAY_AGG(DISTINCT log_template) 
                FROM logs 
                WHERE received_at > NOW() - INTERVAL '2 seconds'
            """)
            row = cursor.fetchone()
            current_count = row[0]
            recent_templates = row[1] or []
            
            # 1. POPULATE PHASE (learning baseline for rate + normal templates)
            if learning_phase and len(history) < LEARNING_WINDOWS:
                # Skip empty windows
                if current_count == 0:
                    print(f"[Learning Phase] Waiting for logs... (No traffic yet)")
                    time.sleep(CHECK_INTERVAL)
                    continue

                # Record real traffic into baseline
                history.append(current_count)
                # During learning, treat all observed templates as "normal".
                for tpl in recent_templates:
                    if tpl is not None:
                        seen_templates.add(tpl)
                print(f"[Learning Phase] Data points: {len(history)}/{LEARNING_WINDOWS} | Current Traffic: {current_count} logs/s | Templates: {len(seen_templates)}")
                time.sleep(CHECK_INTERVAL)
                continue

            # Once learning is done, mark it
            if learning_phase and len(history) >= LEARNING_WINDOWS:
                learning_phase = False
                baseline_established = True
                mean = np.mean(history)
                std_dev = np.std(history)
                print(f"\n✅ BASELINE ESTABLISHED!")
                print(f"   Mean: {int(mean)} logs/s | StdDev: {std_dev:.2f}")
                print(f"   Known templates: {len(seen_templates)}")
                print(f"   🚀 Detection mode ACTIVE\n")
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
                
                print(f"\n{'='*70}")
                print(f"🚨 FREQUENCY ANOMALY DETECTED! 🚨")
                print(f"{'='*70}")
                print(f"   Actual Traffic:    {current_count} logs/s")
                print(f"   Expected Max:      {int(threshold)} logs/s")
                print(f"   Baseline Mean:     {int(mean)} logs/s")
                print(f"   Deviation:         {z_score:.2f}x Sigma")
                
                # Log to DB
                cursor.execute("""
                    INSERT INTO anomalies (log_count, description, deviation_score)
                    VALUES (%s, %s, %s)
                """, (current_count, f"[FREQUENCY] Spike: {current_count} logs/s (Threshold: {int(threshold)})", z_score))
                
                conn.commit()
                print("   ✅ Saved to database")
                print(f"{'='*70}\n")
                
                # Do not add spike to history for next check
            else:
                # Add normal readings to rolling history
                history.append(current_count)
                status = "✅ NORMAL" if current_count <= threshold else "⚠️ WARNING"
                print(f"[{status}] Traffic: {current_count:4d} logs/s | Threshold: {int(threshold):4d} | Baseline: {int(mean):4d}")

            # 4. DETECTION PHASE - PATTERN ANOMALIES (new templates)
            pattern_anomalies = []
            for tpl in recent_templates:
                if tpl not in seen_templates:
                    seen_templates.add(tpl)
                    pattern_anomalies.append(tpl)

            for tpl in pattern_anomalies:
                short_tpl = tpl if len(tpl) <= 180 else tpl[:177] + "..."
                print(f"\n{'='*70}")
                print(f"🧩 PATTERN ANOMALY DETECTED - NEW TEMPLATE!")
                print(f"{'='*70}")
                print(f"   Template: {short_tpl}")

                cursor.execute(
                    """
                    INSERT INTO anomalies (log_count, description, deviation_score)
                    VALUES (%s, %s, %s)
                    """,
                    (0, f"[PATTERN] New template: {short_tpl}", 0.0),
                )

            if pattern_anomalies:
                conn.commit()
                print(f"   ✅ Saved to database")
                print(f"{'='*70}\n")

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
    mode = sys.argv[1] if len(sys.argv) > 1 else "continue"
    
    if mode not in ["fresh", "continue"]:
        print("Usage: python analyzer_enhanced.py [fresh|continue]")
        print("  fresh:   Clear tables and start fresh demo run")
        print("  continue: Analyze existing logs (default)")
        sys.exit(1)
    
    analyze(mode)
