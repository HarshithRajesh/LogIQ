# LogIQ - Real-time Log Anomaly Detection System

LogIQ is a comprehensive system for concurrent log ingestion, processing, and real-time anomaly detection for scalable analytics and security operations.

## 🎯 What is LogIQ?

LogIQ showcases:
- **Real-time log ingestion** using concurrent Go processing
- **Intelligent log parsing** with Drain algorithm for template extraction
- **Multi-type anomaly detection**:
  - Frequency anomalies (volume spikes/DDoS detection)
  - Pattern anomalies (new error signatures/zero-day detection)
- **Production-ready architecture** with PostgreSQL + FastAPI + Grafana
- **Comprehensive demo suite** with 5 different attack scenarios

## 🚀 Quick Start

### Fastest Way (Recommended)
```bash
chmod +x quick_start.sh
./quick_start.sh
```

### Try Different Attacks
```bash
chmod +x run_demo.sh

# Volume spike (DDoS-like)
./run_demo.sh demo1_frequency_spike

# New error patterns
./run_demo.sh demo2_pattern_anomaly

# Combined attack
./run_demo.sh demo3_mixed_attack

# Slow-burn attack
./run_demo.sh demo4_gradual_escalation

# Multiple attack bursts
./run_demo.sh demo5_intermittent_attacks

# All demos sequentially
./run_demo.sh all
```

### Manual Setup
```bash
# Terminal 1: Infrastructure
docker-compose up -d

# Terminal 2: Backend
cd backend
python3 main.py

# Terminal 3: Analyzer
cd backend
python3 analyzer_enhanced.py fresh

# Terminal 4: Agent
cd agent
go run main.go ../demos/demo1_frequency_spike.log
```

## 📊 Demo Scenarios

| Demo | Attack Type | Expected Detection |
|------|------------|-------------------|
| **Demo 1** | Frequency spike (DDoS) | Volume anomaly |
| **Demo 2** | New error patterns | Pattern anomaly |
| **Demo 3** | Mixed attack | Volume + Pattern |
| **Demo 4** | Gradual escalation | Stepped volume anomaly |
| **Demo 5** | Intermittent bursts | Multiple alerts |

See [DEMO_GUIDE.md](DEMO_GUIDE.md) for detailed scenario descriptions.

## 🏗 Architecture

```
Log Files → Go Agent (Parsing) → FastAPI Backend → PostgreSQL
                                      ↓
                              Python Analyzer
                         (Frequency + Pattern Detection)
                                      ↓
                        Anomalies Table → Grafana Dashboard
```

## 🔧 Components

### Agent (Go)
- **File:** `agent/main.go`
- **Function:** Log ingestion and parsing using Drain algorithm
- **Features:** 
  - Concurrent processing
  - Template extraction
  - Configurable log file input
  - Throttling simulation (normal vs attack rates)

### Backend (Python/FastAPI)
- **File:** `backend/main.py`
- **Function:** REST API for log ingestion and storage
- **Endpoints:**
  - `GET /` - Health check
  - `POST /ingest` - Bulk log ingestion

### Analyzer (Python)
- **File:** `backend/analyzer_enhanced.py`
- **Function:** Real-time anomaly detection
- **Features:**
  - Learning phase (builds baseline)
  - Frequency anomaly detection (4-sigma threshold)
  - Pattern anomaly detection (new templates)
  - Two modes: `fresh` (reset) and `continue` (resume)

### Database (PostgreSQL)
- **File:** `database/init_schema.sql`
- **Tables:**
  - `logs` - Raw log entries with templates
  - `anomalies` - Detected anomaly events
  - `known_templates` - Template history

## 📈 How It Works

### Phase 1: Learning (First 5 time windows)
- Analyzer observes traffic patterns
- Records baseline mean and standard deviation
- Marks all observed templates as "normal"

### Phase 2: Detection (Ongoing)
- **Frequency Detection:** Alerts if traffic > mean + 4σ
- **Pattern Detection:** Alerts on new template appearances
- **Alert Recording:** Saves to database with deviation scores

### Phase 3: Analysis
- Evaluation script (`eval.py`) summarizes:
  - Total logs ingested
  - Time span covered
  - Anomaly counts by type

## 🎓 Understanding the Detection

### Frequency Anomalies
- **What:** Sudden increase in log volume
- **Detection:** Statistical deviation (Z-score > 4)
- **Example:** DDoS attack sending 1000s of logs/sec
- **Output:**
  ```
  🚨 FREQUENCY ANOMALY DETECTED!
  Actual Traffic: 987 logs/s
  Expected Max: 115 logs/s
  Deviation: 8.85x Sigma
  ```

### Pattern Anomalies
- **What:** New log templates never seen before
- **Detection:** Template not in `seen_templates` set
- **Example:** New error type from compromised service
- **Output:**
  ```
  🧩 PATTERN ANOMALY DETECTED - NEW TEMPLATE!
  Template: ERROR: Unauthorized access from IP <IP>
  ```

## 📝 Files Structure

```
LogIQ/
├── README.md                    # This file
├── DEMO_GUIDE.md                # Detailed demo documentation
├── SOLUTION_SUMMARY.md          # Enhancement summary
├── docker-compose.yml           # Infrastructure setup
├── quick_start.sh              # One-command setup
├── run_demo.sh                 # Automated demo runner
├── demos/                       # Demo log files
│   ├── demo1_frequency_spike.log
│   ├── demo2_pattern_anomaly.log
│   ├── demo3_mixed_attack.log
│   ├── demo4_gradual_escalation.log
│   └── demo5_intermittent_attacks.log
├── agent/                       # Go agent
│   ├── main.go
│   ├── parser/
│   │   └── drain.go
│   └── benchmark/
│       └── benchmark.go
├── backend/                     # Python backend
│   ├── main.py                 # FastAPI server
│   ├── analyzer_enhanced.py    # Enhanced analyzer (NEW)
│   ├── analyzer.py             # Original analyzer
│   ├── generate_demos.py       # Demo generator (NEW)
│   ├── generate_dataset.py     # Original dataset generator
│   ├── eval.py                 # Results evaluator
│   └── requirements.txt
└── database/
    └── init_schema.sql         # Database schema
```

## 🔍 Performance Metrics

- **Normal Throughput:** ~100 logs/sec
- **Attack Throughput:** 1000+ logs/sec
- **Learning Phase:** ~10 seconds (5 windows × 2 seconds)
- **Detection Latency:** 2 seconds per check window
- **Alert Recording:** < 100ms

## 🛠 Customization

### Add Your Own Attack Pattern
1. Edit `backend/generate_demos.py`
2. Create a new demo function (e.g., `generate_demo6_custom()`)
3. Call it in `main()`
4. Run: `python3 backend/generate_demos.py`
5. Use: `go run agent/main.go ../demos/demo6_custom.log`

### Adjust Detection Sensitivity
In `backend/analyzer_enhanced.py`:
```python
SIGMA_MULTIPLIER = 4  # Default: 4-sigma threshold
                       # Increase: More conservative (fewer false positives)
                       # Decrease: More sensitive (catch subtle anomalies)
```

### Change Learning Phase Duration
In `backend/analyzer_enhanced.py`:
```python
LEARNING_WINDOWS = 5  # Number of windows to observe before alerting
CHECK_INTERVAL = 2    # Seconds between checks
```

## 🐳 Infrastructure

### Using Docker Compose
```bash
docker-compose up -d        # Start
docker-compose ps           # Check status
docker-compose logs -f db   # View DB logs
docker-compose down         # Stop
```

### Manual Database Setup
```bash
# Connect to PostgreSQL
psql -h localhost -U admin -d logiq

# View logs
SELECT COUNT(*) FROM logs;

# View anomalies
SELECT * FROM anomalies ORDER BY detected_at DESC;
```

### Grafana Access
- **URL:** http://localhost:3000
- **User:** admin
- **Password:** admin (default)
- Create dashboards to visualize logs and anomalies

## ⚠️ Troubleshooting

### Issue: Nothing detected on second run
```bash
# Use fresh mode to reset
python3 backend/analyzer_enhanced.py fresh
```

### Issue: Backend won't start
```bash
# Check if already running
lsof -i :8000

# Check PostgreSQL
docker-compose ps
docker-compose logs db
```

### Issue: Agent connection refused
```bash
# Verify backend is running
curl http://localhost:8000

# Check firewall
sudo ufw status
```

### Issue: Demo files not found
```bash
# Regenerate demos
cd backend
python3 generate_demos.py
cd ..
```

## 📊 Example Output

```
🧠 AI Analyzer Started.
⏳ Waiting for data stream to build baseline...
[Learning Phase] Data points: 1/5 | Current Traffic: 98 logs/s | Templates: 4
[Learning Phase] Data points: 2/5 | Current Traffic: 102 logs/s | Templates: 4
...
✅ BASELINE ESTABLISHED!
   Mean: 100 logs/s | StdDev: 2.50
   Known templates: 4
   🚀 Detection mode ACTIVE

[✅ NORMAL] Traffic: 99 logs/s | Threshold: 115 | Baseline: 100

==================================================================
🚨 FREQUENCY ANOMALY DETECTED! 🚨
==================================================================
   Actual Traffic:    1234 logs/s
   Expected Max:      120 logs/s
   Baseline Mean:     100 logs/s
   Deviation:         9.50x Sigma
   ✅ Saved to database
==================================================================
```

## 🔗 Integration Examples

### Connect to SIEM
```python
# In analyzer_enhanced.py, add:
import requests
requests.post("https://your-siem:5000/alerts", json=anomaly_data)
```

### Export to Prometheus
```python
from prometheus_client import Counter
anomaly_counter = Counter('logiq_anomalies', 'Anomaly count', ['type'])
```

### Send to Slack
```python
import slack
client.chat_postMessage(channel="#alerts", text=alert_message)
```

## 📚 Documentation

- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Detailed demo scenarios and walkthrough
- **[SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)** - Enhancement details and architecture

## ✨ Features

- ✅ Real-time log ingestion (Go)
- ✅ Efficient log parsing (Drain algorithm)
- ✅ Multi-type anomaly detection
- ✅ PostgreSQL persistence
- ✅ Grafana visualization
- ✅ 5 different demo scenarios
- ✅ Automated testing framework
- ✅ Easy customization
- ✅ Production-ready architecture

## 🤝 Contributing

To add improvements:
1. Create new demo scenarios in `generate_demos.py`
2. Test with `run_demo.sh`
3. Document in `DEMO_GUIDE.md`
4. Submit with test results

## 📝 License

Part of the LogIQ project by HarshithRajesh

## 📞 Support

For issues or questions:
1. Check DEMO_GUIDE.md for troubleshooting
2. Review SOLUTION_SUMMARY.md for architecture details
3. Run `./quick_start.sh` to verify setup
