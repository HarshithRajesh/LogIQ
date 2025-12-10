import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql://admin:admin@localhost:5432/logiq"

# Analysis parameters
WINDOW_SIZE_SECONDS = 5
LOOKBACK_MINUTES = 2
SIGMA_MULTIPLIER = 4
NOISE_THRESHOLD = 10
SLEEP_INTERVAL = 2


class AnomalyDetector:
    """AI-powered anomaly detection using statistical analysis."""
    
    def __init__(self):
        """Initialize database connection."""
        self.engine = create_engine(DATABASE_URL)
        logger.info("🤖 AI Anomaly Detector initialized")
        logger.info(f"   Window: {WINDOW_SIZE_SECONDS}s | Lookback: {LOOKBACK_MINUTES}m | Threshold: {SIGMA_MULTIPLIER}-Sigma")
    
    def get_recent_logs(self):
        """Fetch logs from the last 2 minutes."""
        query = text("""
            SELECT 
                template_id,
                EXTRACT(EPOCH FROM timestamp) as epoch_time
            FROM logs
            WHERE timestamp >= NOW() - INTERVAL ':minutes minutes'
              AND template_id IS NOT NULL
            ORDER BY timestamp DESC
        """)
        
        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"minutes": LOOKBACK_MINUTES})
        
        return df
    
    def create_time_windows(self, df):
        """Group logs into 5-second windows."""
        if df.empty:
            return pd.DataFrame()
        
        # Floor timestamp to 5-second intervals: floor(epoch/5)*5
        df['window'] = (np.floor(df['epoch_time'] / WINDOW_SIZE_SECONDS) * WINDOW_SIZE_SECONDS).astype(int)
        
        # Convert window back to datetime for better readability
        df['window_time'] = pd.to_datetime(df['window'], unit='s')
        
        return df
    
    def calculate_statistics(self, df):
        """Calculate mean and standard deviation for each template ID."""
        if df.empty:
            return pd.DataFrame()
        
        # Group by template_id and window, count occurrences
        window_counts = df.groupby(['template_id', 'window']).size().reset_index(name='count')
        
        # Calculate statistics per template_id
        stats = window_counts.groupby('template_id').agg({
            'count': ['mean', 'std', 'max']
        }).reset_index()
        
        # Flatten column names
        stats.columns = ['template_id', 'mean', 'std', 'max_count']
        
        # Fill NaN std with 0 (happens when only one data point)
        stats['std'] = stats['std'].fillna(0)
        
        # Calculate 4-Sigma threshold
        stats['threshold'] = stats['mean'] + (SIGMA_MULTIPLIER * stats['std'])
        
        return stats
    
    def detect_anomalies(self, df, stats):
        """Detect anomalies based on statistical thresholds."""
        if df.empty or stats.empty:
            return []
        
        # Get current window (most recent 5-second interval)
        current_window = df['window'].max()
        current_logs = df[df['window'] == current_window]
        
        # Count logs per template in current window
        current_counts = current_logs.groupby('template_id').size().reset_index(name='current_count')
        
        # Merge with statistics
        analysis = current_counts.merge(stats, on='template_id', how='left')
        
        anomalies = []
        
        for _, row in analysis.iterrows():
            template_id = row['template_id']
            current_count = row['current_count']
            mean = row['mean']
            threshold = row['threshold']
            std = row['std']
            
            # Noise filter: Ignore if mean < 10
            if mean < NOISE_THRESHOLD:
                continue
            
            # Anomaly detection: Current count exceeds threshold
            if current_count > threshold:
                severity_score = (current_count - mean) / (std + 1e-6)  # Avoid division by zero
                
                anomaly = {
                    'template_id': template_id,
                    'window_start': pd.to_datetime(current_window, unit='s'),
                    'actual_count': int(current_count),
                    'expected_threshold': float(threshold),
                    'severity_score': float(severity_score),
                    'mean': float(mean),
                    'std': float(std)
                }
                
                anomalies.append(anomaly)
        
        return anomalies
    
    def insert_anomaly(self, anomaly):
        """Insert detected anomaly into the database."""
        query = text("""
            INSERT INTO anomalies 
            (timestamp, template_id, window_start, actual_count, expected_threshold, severity_score, details)
            VALUES 
            (NOW(), :template_id, :window_start, :actual_count, :expected_threshold, :severity_score, :details)
        """)
        
        details = f"Mean: {anomaly['mean']:.2f}, StdDev: {anomaly['std']:.2f}, Threshold: {anomaly['expected_threshold']:.2f}"
        
        with self.engine.connect() as conn:
            conn.execute(query, {
                'template_id': anomaly['template_id'],
                'window_start': anomaly['window_start'],
                'actual_count': anomaly['actual_count'],
                'expected_threshold': anomaly['expected_threshold'],
                'severity_score': anomaly['severity_score'],
                'details': details
            })
            conn.commit()
    
    def run(self):
        """Main detection loop."""
        logger.info("🚀 Starting anomaly detection loop...\n")
        
        iteration = 0
        
        while True:
            try:
                iteration += 1
                
                # Fetch recent logs
                df = self.get_recent_logs()
                
                if df.empty:
                    logger.debug(f"Iteration {iteration}: No recent logs found")
                    time.sleep(SLEEP_INTERVAL)
                    continue
                
                # Create time windows
                df = self.create_time_windows(df)
                
                # Calculate statistics
                stats = self.calculate_statistics(df)
                
                # Detect anomalies
                anomalies = self.detect_anomalies(df, stats)
                
                # Process detected anomalies
                if anomalies:
                    for anomaly in anomalies:
                        # Insert into database
                        self.insert_anomaly(anomaly)
                        
                        # Print alert to console
                        print("\n" + "="*70)
                        print("🚨 ANOMALY DETECTED")
                        print("="*70)
                        print(f"Template ID: {anomaly['template_id']}")
                        print(f"Window Start: {anomaly['window_start']}")
                        print(f"Actual Count: {anomaly['actual_count']}")
                        print(f"Expected (Mean): {anomaly['mean']:.2f}")
                        print(f"Threshold ({SIGMA_MULTIPLIER}-Sigma): {anomaly['expected_threshold']:.2f}")
                        print(f"Standard Deviation: {anomaly['std']:.2f}")
                        print(f"Severity Score: {anomaly['severity_score']:.2f}σ")
                        print(f"❗ Exceeded threshold by {anomaly['actual_count'] - anomaly['expected_threshold']:.2f} logs")
                        print("="*70 + "\n")
                else:
                    if iteration % 10 == 0:  # Print status every 10 iterations
                        logger.info(f"✅ Iteration {iteration}: No anomalies detected (monitoring {len(df)} logs)")
                
                # Sleep before next analysis
                time.sleep(SLEEP_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Anomaly detector stopped by user")
                break
            
            except Exception as e:
                logger.error(f"❌ Error in detection loop: {e}")
                time.sleep(SLEEP_INTERVAL)


def main():
    """Entry point for the anomaly detector."""
    print("\n" + "="*70)
    print("LogIQ - AI Anomaly Detector")
    print("="*70)
    print(f"Configuration:")
    print(f"  Window Size: {WINDOW_SIZE_SECONDS} seconds")
    print(f"  Lookback Period: {LOOKBACK_MINUTES} minutes")
    print(f"  Detection Threshold: {SIGMA_MULTIPLIER}-Sigma (Mean + {SIGMA_MULTIPLIER}×StdDev)")
    print(f"  Noise Filter: Ignore if Mean < {NOISE_THRESHOLD}")
    print(f"  Analysis Interval: {SLEEP_INTERVAL} seconds")
    print("="*70 + "\n")
    
    detector = AnomalyDetector()
    detector.run()


if __name__ == "__main__":
    main()
