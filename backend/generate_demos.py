#!/usr/bin/env python3
"""
Generate multiple demo log files with different attack patterns.
Each demo can be run independently to showcase different anomaly types.
"""

import random
import os

DEMO_DIR = "demos"
os.makedirs(DEMO_DIR, exist_ok=True)

# =============================================================================
# NORMAL LOG TEMPLATES (Used in all demos)
# =============================================================================
NORMAL_LOGS = [
    "INFO: User {uid} logged in successfully.",
    "INFO: User {uid} viewed dashboard.",
    "DEBUG: Cache hit for key session_{uid}.",
    "INFO: Health check passed for node {node}.",
    "DEBUG: Query execution time {time}ms for user {uid}.",
    "INFO: Data sync completed for cluster {node}.",
    "DEBUG: Memory usage at {mem}% for process {pid}."
]

# =============================================================================
# DEMO 1: FREQUENCY SPIKE ATTACK
# Description: Sustained high-volume traffic attack
# Expected Detection: Frequency anomaly when attack phase starts
# =============================================================================
def generate_demo1_frequency_spike():
    """
    Scenario: Normal baseline traffic followed by DDoS-like attack
    - 5000 normal logs at regular rate
    - 2000 attack logs at 10x rate
    """
    print("Generating DEMO 1: Frequency Spike (DDoS-like attack)...")
    
    filename = f"{DEMO_DIR}/demo1_frequency_spike.log"
    with open(filename, "w") as f:
        # Normal Phase
        for i in range(5000):
            template = random.choice(NORMAL_LOGS)
            log = template.format(
                uid=random.randint(1000, 9999),
                node=random.randint(1, 5),
                time=random.randint(10, 500),
                mem=random.randint(30, 80),
                pid=random.randint(1000, 9999)
            )
            f.write(f"{log}\n")
        
        # Attack Phase: Same templates but at extreme rate
        for i in range(2000):
            template = random.choice(NORMAL_LOGS)
            log = template.format(
                uid=random.randint(1000, 9999),
                node=random.randint(1, 5),
                time=random.randint(10, 500),
                mem=random.randint(30, 80),
                pid=random.randint(1000, 9999)
            )
            f.write(f"{log}\n")
    
    print(f"✅ {filename}")

# =============================================================================
# DEMO 2: PATTERN ANOMALY - NEW ERROR TYPES
# Description: Normal logs followed by new error templates
# Expected Detection: Pattern anomaly when new templates appear
# =============================================================================
def generate_demo2_pattern_anomaly():
    """
    Scenario: Normal traffic + sudden appearance of new error patterns
    - 5000 normal logs
    - 2000 new/unknown error patterns (not seen before)
    """
    print("Generating DEMO 2: Pattern Anomaly (New error templates)...")
    
    filename = f"{DEMO_DIR}/demo2_pattern_anomaly.log"
    attack_templates = [
        "ERROR: Database connection failed. Retrying from IP {ip}.",
        "FATAL: Connection timeout from node {node}.",
        "ERROR: Authentication failed for user {uid} from {ip}.",
        "CRITICAL: Service unavailable at endpoint {endpoint}.",
        "ERROR: Unauthorized access attempt from {ip}.",
    ]
    
    with open(filename, "w") as f:
        # Normal Phase
        for i in range(5000):
            template = random.choice(NORMAL_LOGS)
            log = template.format(
                uid=random.randint(1000, 9999),
                node=random.randint(1, 5),
                time=random.randint(10, 500),
                mem=random.randint(30, 80),
                pid=random.randint(1000, 9999)
            )
            f.write(f"{log}\n")
        
        # Attack Phase: New error templates
        for i in range(2000):
            template = random.choice(attack_templates)
            log = template.format(
                ip=f"192.168.1.{random.randint(1, 255)}",
                node=random.randint(1, 5),
                uid=random.randint(1000, 9999),
                endpoint=f"/api/service_{random.randint(1, 5)}"
            )
            f.write(f"{log}\n")
    
    print(f"✅ {filename}")

# =============================================================================
# DEMO 3: MIXED ATTACK - FREQUENCY + PATTERN
# Description: Combines both attack types
# Expected Detection: Both frequency AND pattern anomalies
# =============================================================================
def generate_demo3_mixed_attack():
    """
    Scenario: Normal traffic + both high-volume AND new error patterns
    - 5000 normal logs
    - 2000 high-volume attack logs with new error templates
    """
    print("Generating DEMO 3: Mixed Attack (Volume + New patterns)...")
    
    filename = f"{DEMO_DIR}/demo3_mixed_attack.log"
    attack_templates = [
        "ERROR: Brute force attempt detected: {attempts} failures from {ip}",
        "ALERT: Suspicious query pattern detected in {query}",
        "ERROR: Resource exhaustion: {resource} exceeded {limit}%",
        "FATAL: Cascading failure in service {service}",
    ]
    
    with open(filename, "w") as f:
        # Normal Phase
        for i in range(5000):
            template = random.choice(NORMAL_LOGS)
            log = template.format(
                uid=random.randint(1000, 9999),
                node=random.randint(1, 5),
                time=random.randint(10, 500),
                mem=random.randint(30, 80),
                pid=random.randint(1000, 9999)
            )
            f.write(f"{log}\n")
        
        # Attack Phase: High volume + new patterns
        for i in range(2000):
            template = random.choice(attack_templates)
            log = template.format(
                ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                attempts=random.randint(10, 1000),
                query=f"SELECT * FROM users WHERE id={random.randint(1, 9999)}",
                resource="CPU" if random.random() > 0.5 else "Memory",
                limit=random.randint(80, 100),
                service=f"svc_{random.randint(1, 10)}"
            )
            f.write(f"{log}\n")
    
    print(f"✅ {filename}")

# =============================================================================
# DEMO 4: SLOW ATTACK - GRADUAL ESCALATION
# Description: Gradually increasing traffic (harder to detect)
# Expected Detection: Anomaly when gradient exceeds threshold
# =============================================================================
def generate_demo4_gradual_escalation():
    """
    Scenario: Normal traffic that gradually increases over time
    - Phase 1: 1000 logs at normal rate
    - Phase 2: 1000 logs at 2x rate
    - Phase 3: 1000 logs at 5x rate
    - Phase 4: 1000 logs at 10x rate
    - Phase 5: 2000 logs at max rate
    """
    print("Generating DEMO 4: Gradual Escalation (Slow-burn attack)...")
    
    filename = f"{DEMO_DIR}/demo4_gradual_escalation.log"
    with open(filename, "w") as f:
        # Phase 1: Normal (baseline)
        for i in range(1000):
            template = random.choice(NORMAL_LOGS)
            log = template.format(
                uid=random.randint(1000, 9999),
                node=random.randint(1, 5),
                time=random.randint(10, 500),
                mem=random.randint(30, 80),
                pid=random.randint(1000, 9999)
            )
            f.write(f"{log}\n")
        
        # Phase 2-4: Escalating attack (same templates, different frequency)
        for i in range(1000):
            template = random.choice(NORMAL_LOGS)
            log = template.format(
                uid=random.randint(1000, 9999),
                node=random.randint(1, 5),
                time=random.randint(10, 500),
                mem=random.randint(30, 80),
                pid=random.randint(1000, 9999)
            )
            f.write(f"{log}\n")
        
        # Phase 5: Escalation continues
        for i in range(1000):
            template = random.choice(NORMAL_LOGS)
            log = template.format(
                uid=random.randint(1000, 9999),
                node=random.randint(1, 5),
                time=random.randint(10, 500),
                mem=random.randint(30, 80),
                pid=random.randint(1000, 9999)
            )
            f.write(f"{log}\n")
        
        # Phase 6: Major escalation
        for i in range(1000):
            template = random.choice(NORMAL_LOGS)
            log = template.format(
                uid=random.randint(1000, 9999),
                node=random.randint(1, 5),
                time=random.randint(10, 500),
                mem=random.randint(30, 80),
                pid=random.randint(1000, 9999)
            )
            f.write(f"{log}\n")
        
        # Phase 7: Max attack
        for i in range(2000):
            template = random.choice(NORMAL_LOGS)
            log = template.format(
                uid=random.randint(1000, 9999),
                node=random.randint(1, 5),
                time=random.randint(10, 500),
                mem=random.randint(30, 80),
                pid=random.randint(1000, 9999)
            )
            f.write(f"{log}\n")
    
    print(f"✅ {filename}")

# =============================================================================
# DEMO 5: INTERMITTENT ATTACKS
# Description: Multiple short attack bursts (early warning detection)
# Expected Detection: Multiple frequency anomalies
# =============================================================================
def generate_demo5_intermittent_attacks():
    """
    Scenario: Normal baseline with periodic attack bursts
    - Baseline + burst + calm + burst + calm + burst
    """
    print("Generating DEMO 5: Intermittent Attacks (Multiple bursts)...")
    
    filename = f"{DEMO_DIR}/demo5_intermittent_attacks.log"
    with open(filename, "w") as f:
        phases = [
            ("normal", 1000),
            ("attack", 500),
            ("normal", 1000),
            ("attack", 500),
            ("normal", 1000),
            ("attack", 500),
            ("normal", 2000),
        ]
        
        for phase_type, count in phases:
            for i in range(count):
                template = random.choice(NORMAL_LOGS)
                log = template.format(
                    uid=random.randint(1000, 9999),
                    node=random.randint(1, 5),
                    time=random.randint(10, 500),
                    mem=random.randint(30, 80),
                    pid=random.randint(1000, 9999)
                )
                f.write(f"{log}\n")
    
    print(f"✅ {filename}")

if __name__ == "__main__":
    print("🎬 Generating Demo Scenarios for LogIQ")
    print("=" * 70)
    
    generate_demo1_frequency_spike()
    generate_demo2_pattern_anomaly()
    generate_demo3_mixed_attack()
    generate_demo4_gradual_escalation()
    generate_demo5_intermittent_attacks()
    
    print("=" * 70)
    print("✅ All demos generated successfully!")
    print("\nRun demos with:")
    print("  go run agent/main.go demos/demo1_frequency_spike.log")
    print("  go run agent/main.go demos/demo2_pattern_anomaly.log")
    print("  go run agent/main.go demos/demo3_mixed_attack.log")
    print("  go run agent/main.go demos/demo4_gradual_escalation.log")
    print("  go run agent/main.go demos/demo5_intermittent_attacks.log")
