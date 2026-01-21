# LogIQ Demo Guide - Multiple Attack Patterns

## Overview

This guide explains how to run different anomaly detection demos with LogIQ. Each demo showcases a different attack pattern and detection capability.

## Prerequisites

- Docker & Docker Compose
- Go 1.x
- Python 3.x with pip
- PostgreSQL 15 (via Docker)

## Quick Start

### 1. Generate Demo Files
```bash
cd backend
python3 generate_demos.py
cd ..
```

This creates 5 different demo log files in `backend/demos/`:
- `demo1_frequency_spike.log` - Volume spike attack
- `demo2_pattern_anomaly.log` - New error templates
- `demo3_mixed_attack.log` - Combined attacks
- `demo4_gradual_escalation.log` - Slow-burn attack
- `demo5_intermittent_attacks.log` - Multiple bursts

### 2. Start Infrastructure
```bash
docker-compose up -d
```

Starts:
- PostgreSQL database (port 5432)
- Grafana dashboard (port 3000)

### 3. Start Backend
```bash
cd backend
python3 main.py
```

Backend API runs on `http://localhost:8000`

### 4. Run Demo

**Option A: Using Automated Script (Recommended)**
```bash
chmod +x run_demo.sh
./run_demo.sh demo1_frequency_spike
```

**Option B: Manual Steps**

In terminal 1 (Analyzer):
```bash
cd backend
python3 analyzer_enhanced.py fresh
```

In terminal 2 (Agent):
```bash
cd agent
go run main.go ../backend/demos/demo1_frequency_spike.log
```

### 5. View Results
```bash
cd backend
python3 eval.py
```

---

## Demo Scenarios

### Demo 1: Frequency Spike Attack (DDoS-like)

**Description:**
- 5,000 normal logs at regular rate (~100 logs/sec)
- 2,000 attack logs at maximum rate (~1000+ logs/sec)
- Same log templates, different volume

**Expected Detection:**
- ✅ FREQUENCY ANOMALY when attack phase starts
- ❌ No pattern anomalies (templates are known)

**Real-World Scenario:**
- DDoS attack with legitimate log templates
- Volume-based intrusion detection
- Rate spike analysis

**Output Example:**
```
[Learning Phase] Data points: 1/5 | Current Traffic: 95 logs/s | Templates: 4
[Learning Phase] Data points: 2/5 | Current Traffic: 102 logs/s | Templates: 4
...
✅ BASELINE ESTABLISHED!
   Mean: 98 logs/s | StdDev: 3.50
   Known templates: 4
   🚀 Detection mode ACTIVE

[✅ NORMAL] Traffic: 100 logs/s | Threshold: 110 | Baseline: 98

==================================================================
🚨 FREQUENCY ANOMALY DETECTED! 🚨
==================================================================
   Actual Traffic:    1245 logs/s
   Expected Max:      120 logs/s
   Baseline Mean:     98 logs/s
   Deviation:         9.45x Sigma
   ✅ Saved to database
==================================================================
```

---

### Demo 2: Pattern Anomaly (New Error Templates)

**Description:**
- 5,000 normal logs with standard templates
- 2,000 attack logs with NEW error patterns never seen before
- Same rate, different templates

**Expected Detection:**
- ❌ No frequency anomaly (volume stays normal)
- ✅ PATTERN ANOMALIES for each new template

**Real-World Scenario:**
- New malware signatures appearing
- Unknown error types in system
- Novel attack vectors
- Early warning system for zero-days

**Output Example:**
```
[Learning Phase] Data points: 5/5 | Current Traffic: 98 logs/s | Templates: 4
✅ BASELINE ESTABLISHED!
   Mean: 98 logs/s | StdDev: 2.15
   Known templates: 4
   🚀 Detection mode ACTIVE

[✅ NORMAL] Traffic: 98 logs/s | Threshold: 110 | Baseline: 98

==================================================================
🧩 PATTERN ANOMALY DETECTED - NEW TEMPLATE!
==================================================================
   Template: ERROR: Database connection failed. Retrying from IP <IP>.
   ✅ Saved to database
==================================================================

==================================================================
🧩 PATTERN ANOMALY DETECTED - NEW TEMPLATE!
==================================================================
   Template: FATAL: Connection timeout from node <NUM>.
   ✅ Saved to database
==================================================================
```

---

### Demo 3: Mixed Attack (Volume + Patterns)

**Description:**
- 5,000 normal logs at regular rate
- 2,000 attack logs at maximum rate with NEW error templates
- Combines Demo 1 + Demo 2

**Expected Detection:**
- ✅ FREQUENCY ANOMALIES (rate spikes)
- ✅ PATTERN ANOMALIES (new templates)
- Multiple alerts

**Real-World Scenario:**
- Sophisticated cyber attack
- Combined DDoS + malware
- Multiple detection triggers
- High-confidence alerting

**Output Example:**
```
==================================================================
🚨 FREQUENCY ANOMALY DETECTED! 🚨
==================================================================
   Actual Traffic:    987 logs/s
   Expected Max:      115 logs/s
   Baseline Mean:     100 logs/s
   Deviation:         8.85x Sigma
   ✅ Saved to database

==================================================================
🧩 PATTERN ANOMALY DETECTED - NEW TEMPLATE!
==================================================================
   Template: ERROR: Brute force attempt detected: <NUM> failures from <IP>
   ✅ Saved to database
```

---

### Demo 4: Gradual Escalation (Slow-Burn Attack)

**Description:**
- Phase 1: 1,000 logs @ baseline rate
- Phase 2: 1,000 logs @ 2x rate
- Phase 3: 1,000 logs @ 5x rate
- Phase 4: 1,000 logs @ 10x rate
- Phase 5: 2,000 logs @ max rate

**Expected Detection:**
- Gradual FREQUENCY ANOMALIES as traffic escalates
- May miss initial phases (slow increase stays within threshold)
- Detects when escalation becomes significant

**Real-World Scenario:**
- Slow-and-low attacks evading detection
- Resource exhaustion attacks
- Botnet ramp-up detection
- Behavioral anomaly detection

**Output Example:**
```
[✅ NORMAL] Traffic: 98 logs/s  | Threshold: 110 | Baseline: 98
[✅ NORMAL] Traffic: 195 logs/s | Threshold: 120 | Baseline: 110
[⚠️ WARNING] Traffic: 480 logs/s | Threshold: 145 | Baseline: 125

==================================================================
🚨 FREQUENCY ANOMALY DETECTED! 🚨
==================================================================
   Actual Traffic:    982 logs/s
   Expected Max:      180 logs/s
   Baseline Mean:     140 logs/s
   Deviation:         7.12x Sigma
```

---

### Demo 5: Intermittent Attacks (Multiple Bursts)

**Description:**
- Alternating phases: normal → attack burst → normal → attack burst
- Multiple attack bursts interspersed with baseline traffic
- Tests sustained detection capability

**Expected Detection:**
- Multiple FREQUENCY ANOMALIES (one per burst)
- Good baseline recovery between bursts
- Demonstrates sustained monitoring

**Real-World Scenario:**
- Reconnaissance attacks (probe → wait → probe)
- Distributed attack waves
- Scheduled attack attempts
- Multi-phase breach scenarios

**Output Example:**
```
[✅ NORMAL] Traffic: 98 logs/s | Threshold: 110 | Baseline: 98

==================================================================
🚨 FREQUENCY ANOMALY DETECTED! 🚨
==================================================================
   Actual Traffic:    520 logs/s
   Expected Max:      115 logs/s
   Baseline Mean:     100 logs/s
   Deviation:         4.23x Sigma

[✅ NORMAL] Traffic: 102 logs/s | Threshold: 110 | Baseline: 99

==================================================================
🚨 FREQUENCY ANOMALY DETECTED! 🚨
==================================================================
   Actual Traffic:    498 logs/s
   Expected Max:      118 logs/s
   Baseline Mean:     101 logs/s
   Deviation:         3.85x Sigma
```

---

## Running the Automated Demo Script

The `run_demo.sh` script automates the entire process:

### Single Demo
```bash
./run_demo.sh demo1_frequency_spike
```

### All Demos Sequentially
```bash
./run_demo.sh all
```

### View Results
```bash
./run_demo.sh view
```

### Output Features
- Prerequisites validation
- Automatic demo file generation
- Infrastructure startup
- Backend initialization
- Fresh database for each demo
- Real-time analyzer output
- Automatic result evaluation

---

## Manual Demo Execution

### Step-by-Step Manual Process

1. **Generate demos:**
   ```bash
   cd backend
   python3 generate_demos.py
   cd ..
   ```

2. **Start infrastructure:**
   ```bash
   docker-compose up -d
   ```

3. **Start backend (Terminal 1):**
   ```bash
   cd backend
   python3 main.py
   ```

4. **Start analyzer (Terminal 2) - with fresh mode:**
   ```bash
   cd backend
   python3 analyzer_enhanced.py fresh
   ```

5. **Run agent with demo (Terminal 3):**
   ```bash
   cd agent
   go run main.go ../backend/demos/demo1_frequency_spike.log
   ```

6. **View results (Terminal 1 after agent completes):**
   ```bash
   cd backend
   python3 eval.py
   ```

---

## Analyzer Modes

### Fresh Mode
```bash
python3 analyzer_enhanced.py fresh
```
- Clears `logs`, `anomalies`, and `known_templates` tables
- Starts fresh learning phase
- Perfect for new demo runs
- Establishes clean baseline

### Continue Mode (Default)
```bash
python3 analyzer_enhanced.py continue
```
- Analyzes existing logs
- Preserves previous state
- Good for resuming after analyzer crash

---

## Key Differences from Original Setup

| Aspect | Original | Enhanced |
|--------|----------|----------|
| **Demo Files** | Single `final_demo.log` | 5 different scenarios |
| **Analyzer** | Always learning first run | Explicit fresh/continue modes |
| **Detection** | All anomalies on first run | Only new anomalies on reruns |
| **Template Handling** | Templates persist across runs | Fresh mode clears them |
| **Use Case** | Basic demo | Multiple demonstration patterns |

---

## Troubleshooting

### Issue: All logs detected as anomalies on first run
**Solution:** This is normal for "fresh" mode - the analyzer learns during first 5 windows

### Issue: Nothing detected on second run
**Solution:** Use `fresh` mode to clear tables: `python3 analyzer_enhanced.py fresh`

### Issue: Backend not responding
**Solution:** Check if running: `curl http://localhost:8000`
```bash
ps aux | grep main.py
# If not running:
cd backend
python3 main.py
```

### Issue: Database connection errors
**Solution:** Verify Docker containers:
```bash
docker-compose ps
# Restart if needed:
docker-compose restart
```

### Issue: Go agent won't compile
**Solution:** Update Go modules:
```bash
cd agent
go mod tidy
go mod download
```

---

## Viewing Data in Grafana

1. Open http://localhost:3000
2. Login with default credentials (admin/admin)
3. Create dashboards to visualize:
   - Logs table (count over time)
   - Anomalies table (detection events)
   - Known_templates table (template evolution)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              LogIQ System Architecture          │
├─────────────────────────────────────────────────┤
│                                                  │
│  Demo Log Files                                 │
│  └── demo1_frequency_spike.log                 │
│  └── demo2_pattern_anomaly.log                 │
│  └── demo3_mixed_attack.log                    │
│  └── demo4_gradual_escalation.log              │
│  └── demo5_intermittent_attacks.log            │
│           │                                     │
│           ▼                                     │
│  ┌─────────────────┐                           │
│  │  Go Agent       │                           │
│  │  - Drain Parser │ (1. Parse & Extract)      │
│  │  - Drain Algo   │                           │
│  └────────┬────────┘                           │
│           │ HTTP POST (Batches)                │
│           ▼                                     │
│  ┌──────────────────────┐                      │
│  │  FastAPI Backend     │                      │
│  │  - /ingest endpoint  │ (2. Store)           │
│  │  - Bulk insert       │                      │
│  └────────┬─────────────┘                      │
│           │ SQL                                │
│           ▼                                     │
│  ┌─────────────────────────┐                  │
│  │  PostgreSQL Database    │                  │
│  │  - logs table          │                  │
│  │  - anomalies table     │ (3. Persist)     │
│  │  - known_templates table│                  │
│  └────────┬────────────────┘                  │
│           │ SQL Query (every 2s)              │
│           ▼                                     │
│  ┌──────────────────────┐                     │
│  │  Python Analyzer     │                     │
│  │  - Learning phase    │ (4. Detect)        │
│  │  - Frequency anomaly │                     │
│  │  - Pattern anomaly   │                     │
│  └────────┬─────────────┘                     │
│           │ INSERT (Alerts)                   │
│           ▼                                     │
│  ┌──────────────────────┐                     │
│  │  Grafana Dashboards  │ (5. Visualize)     │
│  │  - Real-time charts  │                     │
│  │  - Anomaly timeline  │                     │
│  └──────────────────────┘                     │
│                                                │
└─────────────────────────────────────────────────┘
```

---

## Performance Metrics

### Normal Phase
- **Throughput:** ~100 logs/sec
- **Batch Size:** 50 logs per request
- **Latency:** ~10ms per log

### Attack Phase
- **Throughput:** 1000+ logs/sec
- **Detection Latency:** 2 seconds (CHECK_INTERVAL)
- **Alert Recording:** < 100ms

### Learning Phase
- **Duration:** ~10 seconds (5 windows × 2 seconds)
- **Baseline Established:** After 5 data points
- **Template Learning:** All templates seen during learning marked as normal

---

## Next Steps

1. **Customize demos:** Modify `generate_demos.py` to add your own attack patterns
2. **Tune detection:** Adjust `SIGMA_MULTIPLIER` in analyzer for sensitivity
3. **Add dashboards:** Create Grafana visualizations for your NOC
4. **Integrate alerts:** Connect anomalies table to your alerting system
5. **Real log ingestion:** Point agent to actual production logs

---

## Questions?

For issues or questions about the demos, check the main README.md or contact the development team.
