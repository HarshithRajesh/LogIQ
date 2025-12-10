import psycopg2
from datetime import datetime
import sys

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "admin",
    "password": "admin",
    "database": "logiq"
}


def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"❌ Database connection error: {e}")
        sys.exit(1)


def calculate_metrics():
    """Calculate and display benchmark metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("📊 LogIQ - System Benchmark Report")
    print("="*70 + "\n")
    
    try:
        # 1. Total Logs Processed
        cursor.execute("SELECT COUNT(*) FROM logs")
        total_logs = cursor.fetchone()[0]
        print(f"1️⃣  Total Logs Processed: {total_logs:,}")
        
        # 2. Total Time (Max Timestamp - Min Timestamp)
        cursor.execute("""
            SELECT 
                MIN(timestamp) as min_ts,
                MAX(timestamp) as max_ts,
                EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) as duration_seconds
            FROM logs
        """)
        result = cursor.fetchone()
        min_timestamp, max_timestamp, duration_seconds = result
        
        if min_timestamp and max_timestamp:
            print(f"2️⃣  Time Period:")
            print(f"     Start: {min_timestamp}")
            print(f"     End:   {max_timestamp}")
            print(f"     Duration: {duration_seconds:.2f} seconds ({duration_seconds/60:.2f} minutes)")
            
            # 3. Logs/Sec (Throughput)
            if duration_seconds > 0:
                throughput = total_logs / duration_seconds
                print(f"3️⃣  Throughput: {throughput:.2f} logs/second")
            else:
                print(f"3️⃣  Throughput: N/A (insufficient time data)")
        else:
            print(f"2️⃣  Time Period: N/A (no logs)")
            print(f"3️⃣  Throughput: N/A (no logs)")
        
        # 4. Unique Templates Found
        cursor.execute("""
            SELECT COUNT(DISTINCT template_id) 
            FROM logs 
            WHERE template_id IS NOT NULL
        """)
        unique_templates = cursor.fetchone()[0]
        print(f"4️⃣  Unique Templates Found: {unique_templates:,}")
        
        # Get top 5 templates by frequency
        cursor.execute("""
            SELECT template_id, log_template, COUNT(*) as count
            FROM logs
            WHERE template_id IS NOT NULL
            GROUP BY template_id, log_template
            ORDER BY count DESC
            LIMIT 5
        """)
        top_templates = cursor.fetchall()
        
        if top_templates:
            print(f"\n     📋 Top 5 Most Frequent Templates:")
            for i, (tid, template, count) in enumerate(top_templates, 1):
                template_short = (template[:60] + '...') if len(template) > 60 else template
                print(f"        {i}. {tid}: {count:,} occurrences")
                print(f"           {template_short}")
        
        # 5. Total Anomalies Detected
        cursor.execute("SELECT COUNT(*) FROM anomalies")
        total_anomalies = cursor.fetchone()[0]
        print(f"\n5️⃣  Total Anomalies Detected: {total_anomalies:,}")
        
        # Get anomaly details
        cursor.execute("""
            SELECT 
                template_id,
                COUNT(*) as anomaly_count,
                AVG(severity_score) as avg_severity,
                MAX(actual_count) as max_count
            FROM anomalies
            GROUP BY template_id
            ORDER BY anomaly_count DESC
        """)
        anomaly_details = cursor.fetchall()
        
        if anomaly_details:
            print(f"\n     🚨 Anomaly Breakdown by Template:")
            for tid, count, avg_severity, max_count in anomaly_details:
                print(f"        • {tid}: {count:,} anomalies (Avg Severity: {avg_severity:.2f}σ, Max Count: {max_count})")
        
        # Additional Statistics
        print(f"\n" + "="*70)
        print("📈 Additional Statistics")
        print("="*70)
        
        # Logs by severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM logs
            GROUP BY severity
            ORDER BY count DESC
        """)
        severity_stats = cursor.fetchall()
        
        print(f"\n🔍 Logs by Severity:")
        for severity, count in severity_stats:
            percentage = (count / total_logs * 100) if total_logs > 0 else 0
            print(f"     {severity:10s}: {count:8,} ({percentage:5.2f}%)")
        
        # Logs by service
        cursor.execute("""
            SELECT service_name, COUNT(*) as count
            FROM logs
            GROUP BY service_name
            ORDER BY count DESC
            LIMIT 5
        """)
        service_stats = cursor.fetchall()
        
        print(f"\n🏢 Top 5 Services by Log Volume:")
        for service, count in service_stats:
            percentage = (count / total_logs * 100) if total_logs > 0 else 0
            print(f"     {service:20s}: {count:8,} ({percentage:5.2f}%)")
        
        print(f"\n" + "="*70)
        print("✅ Benchmark Report Complete")
        print("="*70 + "\n")
        
    except psycopg2.Error as e:
        print(f"❌ Error calculating metrics: {e}")
    
    finally:
        cursor.close()
        conn.close()


def main():
    """Main entry point."""
    print(f"\n🔬 Running LogIQ Benchmark Analysis...")
    print(f"⏰ Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    calculate_metrics()


if __name__ == "__main__":
    main()
