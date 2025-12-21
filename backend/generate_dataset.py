import time
import random

FILENAME = "final_demo.log"
# REVISED: 5000 logs takes ~50 seconds to send. 
# Enough for the AI to learn, fast enough for a demo.
NORMAL_COUNT = 5000 
ATTACK_COUNT = 2000

# Templates
NORMAL_LOGS = [
    "INFO: User {uid} logged in successfully.",
    "INFO: User {uid} viewed dashboard.",
    "DEBUG: Cache hit for key session_{uid}.",
    "INFO: Health check passed for node {node}."
]

ATTACK_LOGS = [
    "ERROR: Database connection failed. Retrying...",
    "FATAL: Connection timeout from IP {ip}.",
    "ERROR: NullPointerException at Service.ProcessPayment."
]

def generate():
    print(f"Generating {FILENAME} with {NORMAL_COUNT} normal logs...")
    with open(FILENAME, "w") as f:
        # Phase 1: Normal Traffic
        for i in range(NORMAL_COUNT):
            template = random.choice(NORMAL_LOGS)
            log = template.format(uid=random.randint(1000, 9999), node=random.randint(1, 5))
            f.write(f"{log}\n")
        
        # Phase 2: Attack Traffic
        for i in range(ATTACK_COUNT):
            template = random.choice(ATTACK_LOGS)
            log = template.format(ip=f"192.168.1.{random.randint(1,255)}")
            f.write(f"{log}\n")
            
    print("✅ Dataset generated successfully!")

if __name__ == "__main__":
    generate()
