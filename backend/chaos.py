import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import sys
import time

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "admin",
    "password": "admin",
    "database": "logiq"
}

# Chaos injection parameters
CHAOS_COUNT = 2000
TEMPLATE_ID = "T-ATTACK"
SEVERITY = "ERROR"


def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"❌ Database connection error: {e}")
        sys.exit(1)


def inject_chaos():
    """Inject 2000 attack logs instantly to trigger anomaly detection."""
    
    print("\n" + "="*70)
    print("💥 LogIQ - Chaos Engineering Mode")
    print("="*70)
    print(f"🎯 Target: Inject {CHAOS_COUNT:,} attack logs instantly")
    print(f"🏷️  Template ID: {TEMPLATE_ID}")
    print(f"⚠️  Severity: {SEVERITY}")
    print("="*70 + "\n")
    
    conn = None
    
    try:
        print("🔌 Connecting to database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current timestamp
        current_time = datetime.now()
        
        print(f"⏰ Injection timestamp: {current_time}")
        print(f"🚀 Injecting chaos...")
        
        start_time = time.time()
        
        # Prepare chaos data
        chaos_logs = []
        for i in range(CHAOS_COUNT):
            chaos_logs.append((
                current_time,                                    # timestamp
                "chaos-service",                                 # service_name
                SEVERITY,                                        # severity
                TEMPLATE_ID,                                     # template_id
                "CHAOS ATTACK - Simulated DDoS Pattern",        # log_template
                [],                                              # parameters (empty list)
                f"CHAOS ATTACK #{i+1} - Database connection failed error 503"  # raw_message
            ))
        
        # Instant bulk injection using execute_values
        insert_query = """
            INSERT INTO logs 
            (timestamp, service_name, severity, template_id, log_template, parameters, raw_message)
            VALUES %s
        """
        
        execute_values(
            cursor,
            insert_query,
            chaos_logs,
            template="(%s, %s, %s, %s, %s, %s, %s)",
            page_size=1000
        )
        
        conn.commit()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ Chaos injection complete!")
        print(f"📊 Statistics:")
        print(f"   • Logs Injected: {CHAOS_COUNT:,}")
        print(f"   • Injection Time: {duration:.3f} seconds")
        print(f"   • Throughput: {CHAOS_COUNT/duration:.2f} logs/second")
        
        # Verify injection
        cursor.execute("""
            SELECT COUNT(*) 
            FROM logs 
            WHERE template_id = %s
        """, (TEMPLATE_ID,))
        
        total_chaos = cursor.fetchone()[0]
        print(f"   • Total '{TEMPLATE_ID}' logs in DB: {total_chaos:,}")
        
        print(f"\n🔥 CHAOS MODE ACTIVATED!")
        print(f"💡 The anomaly detector should trigger alerts within 2-5 seconds...")
        print(f"👀 Watch the analyzer.py console for 🚨 ANOMALY DETECTED alerts")
        
        print("\n" + "="*70)
        print("✅ Chaos Engineering Complete")
        print("="*70 + "\n")
        
        cursor.close()
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"\n❌ Database error during chaos injection: {e}")
        sys.exit(1)
    
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    
    finally:
        if conn:
            conn.close()


def main():
    """Main entry point."""
    print("\n⚠️  WARNING: This script will inject chaos into your system!")
    print("📢 Make sure the anomaly detector (analyzer.py) is running to see results.\n")
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        inject_chaos()
    else:
        print("\n🛑 Chaos injection cancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
