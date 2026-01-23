"""
Generate demo log files with intermittent attacks.
Each demo showcases realistic attack scenarios with normal-attack-normal cycles.
"""

import random

# ==================== NORMAL LOG TEMPLATES ====================
NORMAL_LOGS = [
    "INFO: User {uid} logged in successfully.",
    "INFO: User {uid} viewed dashboard.",
    "DEBUG: Cache hit for key session_{uid}.",
    "INFO: Health check passed for node {node}.",
    "INFO: Data sync completed for cluster {node}.",
    "DEBUG: Query execution time {ms}ms for user {uid}.",
    "DEBUG: Memory usage at {mem}% for process {pid}.",
]

# ==================== ATTACK LOG TEMPLATES ====================
VOLUME_ATTACK = [
    "ERROR: Request queue overflow detected.",
    "ERROR: Connection timeout from IP {ip}.",
    "ERROR: Database connection failed. Retrying...",
    "WARN: High latency detected: {ms}ms response time.",
    "ERROR: Failed to process request from {ip}.",
]

BRUTE_FORCE_ATTACK = [
    "ERROR: Brute force attempt detected: {attempts} failures from {ip}",
    "ALERT: Suspicious login pattern from {ip}",
    "WARN: Multiple failed authentication attempts from {ip}",
    "ERROR: Account lockout triggered for user {uid}",
    "ALERT: Rapid login attempts detected from {ip}",
]

RESOURCE_EXHAUSTION = [
    "ERROR: Resource exhaustion: CPU exceeded {cpu}%",
    "ERROR: Resource exhaustion: Memory exceeded {mem}%",
    "ERROR: Disk space critical: {disk}% full",
    "FATAL: Out of memory error detected",
    "ERROR: Maximum connections exceeded",
]

PATTERN_ANOMALY = [
    "ALERT: Suspicious query pattern detected in SELECT * FROM users WHERE id={uid}",
    "ALERT: SQL injection attempt detected",
    "ERROR: Unauthorized API endpoint access from {ip}",
    "ALERT: Malformed request detected",
    "ERROR: Suspicious data exfiltration pattern",
]

CASCADING_FAILURE = [
    "FATAL: Cascading failure in service svc_{node}",
    "ERROR: Service degradation detected",
    "ALERT: Circuit breaker opened for service {service}",
    "ERROR: Dependency service unavailable",
    "FATAL: Critical service failure",
]

# ==================== DEMO GENERATORS ====================

def generate_normal_logs(count):
    """Generate normal system logs."""
    logs = []
    for _ in range(count):
        template = random.choice(NORMAL_LOGS)
        log = template.format(
            uid=random.randint(1000, 9999),
            node=random.randint(1, 5),
            ms=random.randint(50, 500),
            mem=random.randint(40, 85),
            pid=random.randint(1000, 9999)
        )
        logs.append(log)
    return logs

def generate_volume_attack(count):
    """Generate volume-based DDoS attack logs."""
    logs = []
    for _ in range(count):
        template = random.choice(VOLUME_ATTACK)
        log = template.format(
            ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            ms=random.randint(5000, 30000)
        )
        logs.append(log)
    return logs

def generate_brute_force_attack(count):
    """Generate brute force / credential stuffing attack logs."""
    logs = []
    for _ in range(count):
        template = random.choice(BRUTE_FORCE_ATTACK)
        log = template.format(
            ip=f"192.168.{random.randint(100, 255)}.{random.randint(1, 255)}",
            attempts=random.randint(50, 500),
            uid=random.randint(1000, 9999)
        )
        logs.append(log)
    return logs

def generate_resource_exhaustion(count):
    """Generate resource exhaustion attack logs."""
    logs = []
    for _ in range(count):
        template = random.choice(RESOURCE_EXHAUSTION)
        log = template.format(
            cpu=random.randint(85, 100),
            mem=random.randint(85, 100),
            disk=random.randint(90, 99)
        )
        logs.append(log)
    return logs

def generate_pattern_anomaly(count):
    """Generate pattern anomaly / injection attack logs."""
    logs = []
    for _ in range(count):
        template = random.choice(PATTERN_ANOMALY)
        log = template.format(
            uid=random.randint(1000, 9999),
            ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            service=f"svc_{random.randint(1, 10)}"
        )
        logs.append(log)
    return logs

def generate_cascading_failure(count):
    """Generate cascading failure logs."""
    logs = []
    for _ in range(count):
        template = random.choice(CASCADING_FAILURE)
        log = template.format(
            node=random.randint(1, 10),
            service=f"svc_{random.randint(1, 10)}"
        )
        logs.append(log)
    return logs

# ==================== DEMO SCENARIOS ====================

def demo1_volume_ddos():
    """
    Demo 1: Volume-based DDoS Attack
    STABLE Learning Phase → Normal → Volume Attack → Normal → Attack → Normal
    
    Key: Learning phase has STABLE, CONSISTENT traffic
    (1000 logs × 10ms/log = 100 logs/sec for 10 seconds = 1000 logs stable)
    """
    logs = []
    
    # Phase 1: STABLE LEARNING baseline (1000 logs at stable ~100 logs/sec)
    # This will be the learning phase: 1000 logs at constant rate
    logs.extend(generate_normal_logs(1000))
    
    # Phase 2: Normal continued (1500 logs) - same rate as learning
    logs.extend(generate_normal_logs(1500))
    
    # Phase 3: First attack - Volume DDoS (1200 logs at high speed - SPIKE!)
    logs.extend(generate_volume_attack(1200))
    
    # Phase 4: Back to normal (1500 logs)
    logs.extend(generate_normal_logs(1500))
    
    # Phase 5: Second attack - Volume DDoS again (1200 logs)
    logs.extend(generate_volume_attack(1200))
    
    # Phase 6: Normal recovery (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    return logs

def demo2_brute_force_attack():
    """
    Demo 2: Brute Force / Credential Stuffing Attack
    STABLE Learning → Normal → Brute Force → Normal → Resource Exhaustion → Normal
    """
    logs = []
    
    # Phase 1: STABLE LEARNING baseline (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    # Phase 2: Normal continued (1500 logs)
    logs.extend(generate_normal_logs(1500))
    
    # Phase 3: Brute force attack (1000 logs - SPIKE!)
    logs.extend(generate_brute_force_attack(1000))
    
    # Phase 4: Back to normal (1500 logs)
    logs.extend(generate_normal_logs(1500))
    
    # Phase 5: Resource exhaustion attack (800 logs)
    logs.extend(generate_resource_exhaustion(800))
    
    # Phase 6: Normal recovery (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    return logs

def demo3_pattern_anomaly():
    """
    Demo 3: Pattern Anomaly / SQL Injection Attack
    STABLE Learning → Normal → Pattern Anomaly → Normal → Cascading Failure → Normal
    """
    logs = []
    
    # Phase 1: STABLE LEARNING baseline (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    # Phase 2: Normal continued (1500 logs)
    logs.extend(generate_normal_logs(1500))
    
    # Phase 3: Pattern anomaly attack (1000 logs - new templates!)
    logs.extend(generate_pattern_anomaly(1000))
    
    # Phase 4: Back to normal (1500 logs)
    logs.extend(generate_normal_logs(1500))
    
    # Phase 5: Cascading failure attack (800 logs)
    logs.extend(generate_cascading_failure(800))
    
    # Phase 6: Normal recovery (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    return logs

def demo4_mixed_attacks():
    """
    Demo 4: Mixed Attack Scenario
    STABLE Learning → Normal → Volume → Normal → Brute Force → Normal → Resource Exhaustion → Normal
    """
    logs = []
    
    # Phase 1: STABLE LEARNING baseline (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    # Phase 2: Normal period (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    # Phase 3: Volume attack (800 logs - SPIKE 1)
    logs.extend(generate_volume_attack(800))
    
    # Phase 4: Normal period (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    # Phase 5: Brute force attack (800 logs - SPIKE 2)
    logs.extend(generate_brute_force_attack(800))
    
    # Phase 6: Normal period (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    # Phase 7: Resource exhaustion (800 logs - SPIKE 3)
    logs.extend(generate_resource_exhaustion(800))
    
    # Phase 8: Normal recovery (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    return logs

def demo5_sophisticated_attack():
    """
    Demo 5: Sophisticated Multi-Vector Attack
    STABLE Learning → Normal → [Volume + Pattern] → Normal → [Brute Force + Resource] → Normal
    """
    logs = []
    
    # Phase 1: STABLE LEARNING baseline (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    # Phase 2: Normal period (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    # Phase 3: First sophisticated multi-vector attack
    logs.extend(generate_volume_attack(500))           # Volume spike
    logs.extend(generate_pattern_anomaly(500))         # + new patterns
    
    # Phase 4: Normal period (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    # Phase 5: Second sophisticated multi-vector attack
    logs.extend(generate_brute_force_attack(500))      # Brute force
    logs.extend(generate_resource_exhaustion(500))     # + resource exhaustion
    
    # Phase 6: Normal recovery (1000 logs)
    logs.extend(generate_normal_logs(1000))
    
    return logs

# ==================== FILE GENERATION ====================

def save_demo(filename, logs):
    """Save logs to file."""
    with open(filename, "w") as f:
        for log in logs:
            f.write(f"{log}\n")
    print(f"✅ {filename} ({len(logs)} logs)")

def generate_all():
    """Generate all demo scenarios."""
    print("🎬 Generating Demo Scenarios with Intermittent Attacks...\n")
    
    save_demo("demo1_volume_ddos.log", demo1_volume_ddos())
    save_demo("demo2_brute_force_attack.log", demo2_brute_force_attack())
    save_demo("demo3_pattern_anomaly.log", demo3_pattern_anomaly())
    save_demo("demo4_mixed_attacks.log", demo4_mixed_attacks())
    save_demo("demo5_sophisticated_attack.log", demo5_sophisticated_attack())
    
    print("\n📊 Demo Scenarios Summary:")
    print("  Demo 1: Volume DDoS attack → returns to normal → repeats")
    print("  Demo 2: Brute Force + Resource Exhaustion attacks with normal periods")
    print("  Demo 3: Pattern Anomaly + Cascading Failure attacks with normal periods")
    print("  Demo 4: Volume → Brute Force → Resource Exhaustion (spaced out)")
    print("  Demo 5: Multi-vector attacks (Volume+Pattern, then Brute Force+Resource)")
    print("\n🎯 All demos now show realistic attack interruptions!")

if __name__ == "__main__":
    generate_all()
