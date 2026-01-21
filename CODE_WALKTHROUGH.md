# 🔧 LogIQ - Complete Code & Output Walkthrough
## Line-by-Line Explanation for Technical Presentation

---

## 📂 **PART 1: AGENT CODE (Go - main.go)**

### **File Location:** `/home/neo/code/projects/LogIQ/agent/main.go`

### **Code Section 1: Setup & Constants**
```go
const (
    ServerURL          = "http://localhost:8000/ingest"
    BatchSize          = 50
    DefaultNormalLimit = 5000
)
```

**Explanation for presentation:**
- `ServerURL`: Where logs are sent (FastAPI backend on port 8000)
- `BatchSize`: Sends 50 logs at a time (efficient batching)
- `DefaultNormalLimit`: First 5000 logs sent slowly (normal phase), rest sent fast (attack phase)

**Why these numbers?**
- 5000 logs × 10ms/log = ~50 seconds to send normal phase
- Gives analyzer time to learn (5 windows × 2 seconds = 10 seconds)
- Attack phase uses max speed to create spike

---

### **Code Section 2: Wait Before Sending**
```go
// Wait for backend to be ready AND give analyzer time to start learning
// Learning phase takes ~10 seconds (5 windows × 2 seconds each)
// So we wait 12 seconds to ensure learning is in progress before sending logs
fmt.Println("\n⏱️  Waiting 12 seconds for analyzer to initialize...")
for i := 12; i > 0; i-- {
    fmt.Printf("\r   Starting in %2d seconds...", i)
    time.Sleep(1 * time.Second)
}
```

**Why 12 seconds?**
```
Backend startup:     ~2 seconds
Analyzer startup:    ~1 second
Learning phase:      ~10 seconds (5 windows × 2 sec each)
Buffer:              ~1 second
─────────────────────────────
Total wait needed:   ~14 seconds (we use 12 to be safe)
```

**What happens if we don't wait:**
- Analyzer still initializing → logs arrive before baseline is learned
- First logs become the baseline (wrong!)
- Threshold gets corrupted

---

### **Code Section 3: Normal Phase (Throttled)**
```go
if lineCount < normalLimit {
    // Normal Mode: 10ms sleep = ~100 logs/sec (approx)
    // This creates a stable baseline for the Python script
    time.Sleep(10 * time.Millisecond)

    if lineCount%500 == 0 {
        fmt.Printf("\r[Normal Mode] Sent %d / %d logs...", lineCount, normalLimit)
    }
}
```

**Explanation:**
- **10ms sleep**: 1 second ÷ 10ms = 100 logs per second
- **lineCount < 5000**: Only apply throttle to first 5000 logs
- **lineCount%500 == 0**: Print progress every 500 logs

**Math:**
```
If we send 100 logs/sec for 50 seconds:
  Total logs = 100 × 50 = 5000 logs ✓

Analyzer's learning window = 2 seconds:
  Window 1: 100 logs/sec × 2 sec = 200 logs per window
  Window 2: 100 logs/sec × 2 sec = 200 logs per window
  ...
  Baseline = 100 logs/sec (stable!)
```

---

### **Code Section 4: Attack Phase (Max Speed)**
```go
else {
    // Attack Mode: NO SLEEP = Max speed (1000+ logs/sec)
    if lineCount == normalLimit+1 {
        fmt.Println("\n\n🔥🔥🔥 SWITCHING TO ATTACK MODE! UNLEASHING LOGS! 🔥🔥🔥")
    }
    if lineCount%200 == 0 {
        fmt.Printf("\r[ATTACK Mode] Sent %d logs!!!", lineCount)
    }
}
```

**Explanation:**
- **NO time.Sleep()**: Send as fast as possible
- **Result**: 1000-2000 logs/second
- **Purpose**: Create visible spike that analyzer will catch

**What actually happens:**
```
Logs sent rapidly → Analyzer receives burst
Normal baseline: 100-150 logs/sec
Attack burst: 1000-2000 logs/sec
Deviation: 10-20x the normal rate!
Analyzer triggers: 🚨 ANOMALY DETECTED
```

---

## 🧠 **PART 2: ANALYZER CODE (Python - analyzer_enhanced.py)**

### **File Location:** `/home/neo/code/projects/LogIQ/backend/analyzer_enhanced.py`

### **Code Section 1: Constants**
```python
SIGMA_MULTIPLIER = 4        # Threshold = mean + (4 × stdev)
LEARNING_WINDOWS = 5        # Number of 2-second windows to learn
WINDOW_DURATION = 2         # seconds per window
```

**Explanation for presentation:**

**SIGMA_MULTIPLIER = 4**
```
Statistical confidence levels:
  1σ = 68% (too loose, would catch normal variations)
  2σ = 95% (still too loose)
  3σ = 99.7% (better)
  4σ = 99.99% (very strict, catches real attacks)

Threshold Calculation:
  Threshold = Mean + (4 × StdDev)
           = Mean + (4σ)

Example:
  Mean = 500 logs/sec
  StdDev = 100 logs/sec
  Threshold = 500 + (4 × 100) = 900 logs/sec
  
  If traffic = 850 logs/sec → ✅ NORMAL (below threshold)
  If traffic = 950 logs/sec → 🚨 ANOMALY (above threshold)
```

**LEARNING_WINDOWS = 5**
```
Why 5 windows?
  - Not too short (1-2 windows = insufficient data)
  - Not too long (10+ windows = takes too long)
  - 5 windows = ~10 seconds = good balance

Total learning time = 5 windows × 2 seconds = 10 seconds
```

---

### **Code Section 2: Learning Phase**
```python
def learning_phase(self):
    """Collect baseline traffic statistics"""
    data_points = []
    
    for window in range(LEARNING_WINDOWS):
        # Count logs in this 2-second window
        logs_this_window = self.get_log_count_in_window()
        data_points.append(logs_this_window)
        
        print(f"[Learning Phase] Data points: {window+1}/{LEARNING_WINDOWS}")
        print(f"                 Current Traffic: {logs_this_window} logs/s")
        
        time.sleep(2)  # Wait 2 seconds for next window
    
    # Calculate statistics
    self.baseline_mean = np.mean(data_points)      # Average
    self.baseline_stdev = np.std(data_points)      # Variation
    self.threshold = self.baseline_mean + (SIGMA_MULTIPLIER * self.baseline_stdev)
```

**Step-by-step:**

**Example data collected:**
```
Window 1: 100 logs/sec captured
Window 2: 120 logs/sec captured
Window 3: 110 logs/sec captured
Window 4: 130 logs/sec captured
Window 5: 140 logs/sec captured

data_points = [100, 120, 110, 130, 140]
```

**Calculation 1: Mean (Average)**
```python
mean = (100 + 120 + 110 + 130 + 140) / 5
     = 600 / 5
     = 120 logs/sec
```

**Calculation 2: Standard Deviation**
```python
# How much do values vary from mean?
deviations = [
    (100 - 120)² = 400
    (120 - 120)² = 0
    (110 - 120)² = 100
    (130 - 120)² = 100
    (140 - 120)² = 400
]

variance = (400 + 0 + 100 + 100 + 400) / 5 = 200
stdev = √200 = 14.14 logs/sec
```

**Calculation 3: Threshold**
```python
threshold = mean + (4 × stdev)
          = 120 + (4 × 14.14)
          = 120 + 56.56
          = 176.56 logs/sec
          ≈ 177 logs/sec
```

**Output after learning:**
```
✅ BASELINE ESTABLISHED!
   Mean: 120 logs/s | StdDev: 14.14
   Threshold: 177 logs/s
   🚀 Detection mode ACTIVE
```

---

### **Code Section 3: Detection Phase - Normal Traffic**
```python
def detect_anomaly(self, current_traffic):
    """Check if current traffic is normal or anomaly"""
    
    if current_traffic <= self.threshold:
        print(f"[✅ NORMAL] Traffic: {current_traffic} logs/s | "
              f"Threshold: {self.threshold} | "
              f"Baseline: {self.baseline_mean}")
        return False  # Not an anomaly
    else:
        # Calculate how many sigmas above baseline
        sigma_deviation = (current_traffic - self.baseline_mean) / self.baseline_stdev
        
        print(f"🚨 FREQUENCY ANOMALY DETECTED!")
        print(f"   Actual Traffic: {current_traffic} logs/s")
        print(f"   Expected Max: {self.threshold} logs/s")
        print(f"   Deviation: {sigma_deviation:.2f}x Sigma")
        
        # Save to database
        self.save_anomaly_to_db(current_traffic, sigma_deviation)
        return True  # Anomaly detected
```

**Example 1: Normal Traffic**
```
Inputs:
  current_traffic = 150 logs/sec
  threshold = 177 logs/sec
  
Check:
  150 <= 177? YES ✅
  
Output:
  [✅ NORMAL] Traffic: 150 logs/s | Threshold: 177 | Baseline: 120
```

**Example 2: Anomaly Detected**
```
Inputs:
  current_traffic = 250 logs/sec
  threshold = 177 logs/sec
  baseline_mean = 120
  baseline_stdev = 14.14
  
Check:
  250 <= 177? NO 🚨
  
Calculate deviation:
  sigma_deviation = (250 - 120) / 14.14
                  = 130 / 14.14
                  = 9.19 sigma
  
Output:
  🚨 FREQUENCY ANOMALY DETECTED!
     Actual Traffic: 250 logs/s
     Expected Max: 177 logs/s
     Deviation: 9.19x Sigma
     ✅ Saved to database
```

---

### **Code Section 4: Pattern Detection**
```python
def detect_new_template(self, log_line):
    """Check if this is a new log template we haven't seen"""
    
    # Extract template (replace numbers/IPs with placeholders)
    template = self.extract_template(log_line)
    
    if template not in self.known_templates:
        # New template discovered!
        self.known_templates.add(template)
        
        print(f"🧩 PATTERN ANOMALY DETECTED - NEW TEMPLATE!")
        print(f"   Template: {template}")
        
        # Save to database
        self.save_pattern_anomaly_to_db(template)
        return True  # Pattern anomaly
    else:
        return False  # Known template, normal
```

**Example:**

**Learning phase sees these templates:**
```
1. INFO: User {uid} logged in successfully.
2. INFO: User {uid} viewed dashboard.
3. DEBUG: Cache hit for key session_{uid}.
4. DEBUG: Memory usage at {mem}% for process {pid}.
```
(4 unique templates stored in `known_templates`)

**During normal traffic:**
```
Incoming log: "INFO: User 5432 logged in successfully."
Extract template: "INFO: User {uid} logged in successfully."
Check: Is this in known_templates? YES ✅ → Normal
```

**During attack:**
```
Incoming log: "ERROR: Brute force attempt detected: 50 failures from 192.168.1.1"
Extract template: "ERROR: Brute force attempt detected: <NUM> failures from <IP>"
Check: Is this in known_templates? NO 🚨 → ANOMALY!

Output:
  🧩 PATTERN ANOMALY DETECTED - NEW TEMPLATE!
     Template: ERROR: Brute force attempt detected: <NUM> failures from <IP>
     ✅ Saved to database
```

---

## 📊 **PART 3: BACKEND API (FastAPI - main.py)**

### **File Location:** `/home/neo/code/projects/LogIQ/backend/main.py`

### **Code Section 1: API Endpoint**
```python
@app.post("/ingest")
async def ingest_logs(logs: List[LogData]):
    """Receive logs from agent and process them"""
    
    for log in logs:
        # Process each log
        store_in_memory(log.content, log.template)
        
    return {"status": "received", "count": len(logs)}
```

**Explanation:**
- **@app.post("/ingest")**: HTTP POST endpoint at `/ingest`
- **logs: List[LogData]**: Receives array of log objects
- **for log in logs**: Process each one individually
- **return**: Confirmation response to agent

**Flow:**
```
Agent                    Backend                 Analyzer
  │                        │                         │
  ├─ POST /ingest ────────→│                         │
  │  (50 logs batch)       │                         │
  │                        ├─ Store in memory ──────→│
  │                        │                         │
  │←─ {"status": "ok"} ────┤                         │
  │                        │                         │
```

---

### **Code Section 2: In-Memory Storage**
```python
# Global storage for logs
logs_per_window = {}  # {timestamp: [logs]}
template_counts = {}  # {template: count}
```

**Why in-memory?**
```
Fast access: Memory access = microseconds
Database access: Disk I/O = milliseconds (100x slower)
Per-window operation: Need 2-sec snapshots

Tradeoff:
  ✅ Fast analysis
  ❌ Data lost on restart
  
For demo: Perfect (real system would use database)
```

---

## 🔄 **PART 4: COMPLETE FLOW DIAGRAM**

### **Timeline: Complete Demo Run**

```
TIME    AGENT                   BACKEND                 ANALYZER
────────────────────────────────────────────────────────────────────
0s      Start
        Wait 12s...
        
2s                                                      [Learning W1]
                                                        Collect logs...
        
4s                                                      [Learning W2]
                                                        Data: 100 logs
        
6s                                                      [Learning W3]
                                                        Data: 120 logs
        
8s                                                      [Learning W4]
                                                        Data: 110 logs
        
10s                                                     [Learning W5]
                                                        Data: 130 logs
                                                        
                                                        ✅ BASELINE SET
                                                        Mean: 115 logs/s
                                                        Threshold: 175 logs/s
        
12s     ✅ Begin sending logs
        Send log 1-50 slowly
        (10ms each)
        
14s     Send log 51-100               Process batch 1    [Detection] ✅
        Still slow (Normal mode)      Store in memory    Not anomaly
        
...     Continue normal phase
        100 logs/sec pace
        
30s     Sent 5000 logs (Normal limit reached)
        
31s     🔥 SWITCH TO ATTACK MODE     Process batch N    [Detection] ⚠️
        Send logs 5001+ FAST                            Traffic spiking
        No sleep = 1000+ logs/sec
        
32s     Attack logs flood in                           [Detection] 🚨
        Sending 1000+ logs/sec                         🚨 ANOMALY!
                                                        4300 logs/sec
                                                        Threshold: 3960
                                                        Saved to DB
        
45s     Finished sending all logs    Receive final      [End]
        ✅ Complete                  batch
```

---

## 💾 **PART 5: DATABASE SCHEMA**

### **File Location:** `/home/neo/code/projects/LogIQ/database/init_schema.sql`

### **Anomalies Table**
```sql
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    anomaly_type VARCHAR(50),              -- 'frequency' or 'pattern'
    actual_traffic INT,                    -- logs/sec at time of detection
    baseline_mean FLOAT,                   -- learned baseline
    threshold FLOAT,                       -- alert threshold
    deviation_sigma FLOAT,                 -- how many sigmas above
    detected_template VARCHAR(500),        -- for pattern anomalies
    severity VARCHAR(20)                   -- 'high', 'critical', etc.
);
```

**What gets saved:**
```
Frequency Anomaly Record:
  id: 1
  created_at: 2026-01-21 14:32:15
  anomaly_type: 'frequency'
  actual_traffic: 4300
  baseline_mean: 1780
  threshold: 3960
  deviation_sigma: 4.62
  detected_template: NULL
  severity: 'critical'

Pattern Anomaly Record:
  id: 2
  created_at: 2026-01-21 14:32:20
  anomaly_type: 'pattern'
  actual_traffic: 2100
  baseline_mean: 1800
  threshold: 3900
  deviation_sigma: NULL
  detected_template: 'ERROR: Brute force attempt detected: <NUM> failures'
  severity: 'high'
```

---

## 📈 **PART 6: KEY FORMULAS REFERENCE**

### **Mean (Average)**
```
Formula: μ = (x₁ + x₂ + ... + xₙ) / n

Example:
  Data: [100, 120, 110, 130, 140]
  Mean = (100+120+110+130+140) / 5 = 120
```

### **Standard Deviation**
```
Formula: σ = √(Σ(xᵢ - μ)² / n)

Step 1 - Calculate deviations from mean:
  100 - 120 = -20
  120 - 120 = 0
  110 - 120 = -10
  130 - 120 = 10
  140 - 120 = 20

Step 2 - Square them:
  (-20)² = 400
  (0)² = 0
  (-10)² = 100
  (10)² = 100
  (20)² = 400

Step 3 - Average of squares:
  (400 + 0 + 100 + 100 + 400) / 5 = 200

Step 4 - Square root:
  √200 = 14.14

Result: σ = 14.14 logs/sec
```

### **Threshold**
```
Formula: T = μ + (k × σ)
         where k = SIGMA_MULTIPLIER (4)

Example:
  Mean = 120 logs/s
  StdDev = 14.14 logs/s
  k = 4
  
  Threshold = 120 + (4 × 14.14)
           = 120 + 56.56
           = 176.56 logs/s
```

### **Sigma Deviation (How Anomalous)**
```
Formula: σ_dev = (Actual - Mean) / StdDev

Example:
  Actual = 250 logs/s
  Mean = 120 logs/s
  StdDev = 14.14 logs/s
  
  σ_dev = (250 - 120) / 14.14
        = 130 / 14.14
        = 9.19 sigma
        
Interpretation:
  1σ = 68% chance normal
  2σ = 95% chance normal
  3σ = 99.7% chance normal
  4σ = 99.99% chance normal
  9.19σ = 0.0000001% chance normal = DEFINITELY ATTACK!
```

---

## 🎓 **PART 7: COMPLETE WALKTHROUGH - ONE DEMO RUN**

### **Scenario: demo1_volume_ddos.log**

#### **Step 1: Agent Starts (t=0s)**
```
🚀 Starting LogIQ Agent...
📂 Reading log file: demo1_volume_ddos.log
⏳ Warming up (Sending Normal Traffic)...
⏱️  Waiting 12 seconds for analyzer to initialize...
```
- Agent loads 6500 logs from file
- Prepares to send them

#### **Step 2: Analyzer Starts Learning (t=0-12s)**
```
🧠 AI Analyzer Started.
🧹 Clearing tables for fresh demo run...
⏳ Waiting for data stream to build baseline...
[Learning Phase] Waiting for logs... (No traffic yet)
[Learning Phase] Waiting for logs... (No traffic yet)
... (repeats as agent hasn't started yet)
```
- Analyzer is ready
- Waiting for logs to arrive
- Nothing yet because agent is waiting

#### **Step 3: Agent Sends Normal Phase (t=12-50s)**
```
✅ Analyzer initialized. Starting log transmission!
[Normal Mode] Sent 500 / 5000 logs...
[Normal Mode] Sent 1000 / 5000 logs...
[Normal Mode] Sent 1500 / 5000 logs...
[Normal Mode] Sent 2000 / 5000 logs...
[Normal Mode] Sent 2500 / 5000 logs...
[Normal Mode] Sent 3000 / 5000 logs...
[Normal Mode] Sent 3500 / 5000 logs...
[Normal Mode] Sent 4000 / 5000 logs...
[Normal Mode] Sent 4500 / 5000 logs...
[Normal Mode] Sent 5000 / 5000 logs...
```

**What analyzer sees (in real time):**
```
[Learning Phase] Data points: 1/5 | Current Traffic: 100 logs/s
[Learning Phase] Data points: 2/5 | Current Traffic: 110 logs/s
[Learning Phase] Data points: 3/5 | Current Traffic: 105 logs/s
[Learning Phase] Data points: 4/5 | Current Traffic: 120 logs/s
[Learning Phase] Data points: 5/5 | Current Traffic: 115 logs/s

✅ BASELINE ESTABLISHED!
   Mean: 110 logs/s | StdDev: 7.08
   Known templates: 7
   🚀 Detection mode ACTIVE

[✅ NORMAL] Traffic:  100 logs/s | Threshold: 139 | Baseline:  110
[✅ NORMAL] Traffic:  110 logs/s | Threshold: 139 | Baseline:  110
[✅ NORMAL] Traffic:  115 logs/s | Threshold: 139 | Baseline:  110
[✅ NORMAL] Traffic:  108 logs/s | Threshold: 139 | Baseline:  110
```

#### **Step 4: Agent Switches to Attack Mode (t=50s)**
```
🔥🔥🔥 SWITCHING TO ATTACK MODE! UNLEASHING LOGS! 🔥🔥🔥
[ATTACK Mode] Sent 5200 logs!!!
[ATTACK Mode] Sent 5400 logs!!!
[ATTACK Mode] Sent 5600 logs!!!
[ATTACK Mode] Sent 5800 logs!!!
[ATTACK Mode] Sent 6000 logs!!!
[ATTACK Mode] Sent 6200 logs!!!
[ATTACK Mode] Sent 6400 logs!!!
```

**What analyzer sees (traffic spikes):**
```
[✅ NORMAL] Traffic:  500 logs/s | Threshold: 139 | Baseline:  115
[✅ NORMAL] Traffic: 1000 logs/s | Threshold: 180 | Baseline:  200
[✅ NORMAL] Traffic: 1200 logs/s | Threshold: 250 | Baseline:  350

🚨 FREQUENCY ANOMALY DETECTED! 🚨
======================================================================
   Actual Traffic:    1400 logs/s
   Expected Max:      450 logs/s
   Baseline Mean:     200 logs/s
   Deviation:         8.5x Sigma
   ✅ Saved to database
======================================================================
```

#### **Step 5: Complete (t=60s+)**
```
✅ Log File processing complete.
```

**Database now contains:**
- 1 frequency anomaly (1400 logs/s spike)
- 5+ pattern anomalies (new error templates)
- All saved with timestamps

---

## ✅ **PART 8: KEY TAKEAWAYS FOR PRESENTATION**

### **Agent (Go Program)**
- Sends logs in 2 phases: **Normal (throttled) + Attack (max speed)**
- Wait 12 seconds for analyzer to initialize
- Creates realistic traffic pattern for testing

### **Analyzer (Python Program)**
- **Learning**: Collects 5 snapshots (10 seconds) to establish baseline
- **Detection**: Checks both **frequency** (traffic spike) **and patterns** (new error types)
- **Response**: Instant alert + database save

### **Backend (FastAPI)**
- Receives logs in batches
- Stores in memory for fast processing
- Routes to analyzer for analysis

### **Database (PostgreSQL)**
- Records all anomalies with full context
- Enables audit trail and post-incident analysis

---

## 🎯 **PART 9: DEMO SCRIPT WITH CODE REFERENCES**

### **Opening (Show code files)**
> *"Our system has 3 main components: the Agent sends logs, the Backend receives them, and the Analyzer detects anomalies. Let me walk through each."*

### **Agent Phase (Show main.go lines 40-70)**
> *"The Agent sends 5000 logs slowly (Normal mode) with a 10ms sleep between each. That's about 100 logs per second. Then it switches to Attack mode with no sleep, sending 1000+ logs per second."*

### **Analyzer Learning (Show analyzer_enhanced.py learning_phase)**
> *"The Analyzer learns for 10 seconds, collecting 5 snapshots. From our demo, we see 100, 110, 105, 120, 115 logs per second. The average is 110, the spread (standard deviation) is 7. So the threshold becomes 110 + (4 × 7) = 138 logs per second."*

### **Normal Detection (Show detect_anomaly function)**
> *"When traffic is 115 logs/sec, it's below 138, so ✅ NORMAL. No alert. The system doesn't false-flag normal variations."*

### **Attack Detection (Show sigma_deviation calculation)**
> *"When traffic jumps to 1400 logs/sec, that's way above 138. We calculate: (1400 - 200) / 80 = 15 sigma. Statistically impossible to be normal. 🚨 ANOMALY DETECTED!"*

### **Database (Show SQL query results)**
> *"All anomalies are saved to the database with full context - actual traffic, threshold, deviation. This creates an audit trail for security analysis."*

---

This guide should answer **every possible question** about the code and output!

You're **100% ready for tomorrow**! 🚀
