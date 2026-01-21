#!/bin/bash
# Manual Setup Guide for LogIQ Demos
# Run each command in a SEPARATE terminal for best results

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║        LogIQ - Manual Setup Guide (3 Terminals)              ║
╚═══════════════════════════════════════════════════════════════╝

SETUP: 3 TERMINAL WINDOWS

Before starting: Make sure Docker is running
  docker-compose up -d

═══════════════════════════════════════════════════════════════

TERMINAL 1: Backend Server
─────────────────────────────────────────────────────────────

cd backend
python3 main.py

Expected output:
  🚀 Starting Backend on http://0.0.0.0:8000
  Uvicorn running on 0.0.0.0:8000
  Application startup complete

Wait for "startup complete" before proceeding!

═══════════════════════════════════════════════════════════════

TERMINAL 2: Analyzer (Fresh Mode)
─────────────────────────────────────────────────────────────

cd backend
python3 analyzer_enhanced.py fresh

Expected output:
  🧠 AI Analyzer Started.
  🧹 Clearing tables for fresh demo run...
  ✅ Tables cleared successfully
  ⏳ Waiting for data stream to build baseline...
  [Learning Phase] Data points: 1/5 | Current Traffic: ...

Keep this running! It will show detection events.

═══════════════════════════════════════════════════════════════

TERMINAL 3: Agent (Choose a Demo)
─────────────────────────────────────────────────────────────

First, generate demo files if not already done:
  cd backend
  python3 generate_demos.py
  cd ..

Then run agent with one of these:

  # Demo 1: Frequency Spike (DDoS-like)
  cd agent
  go run main.go ../demos/demo1_frequency_spike.log

  # Demo 2: Pattern Anomaly (New Errors)
  cd agent
  go run main.go ../demos/demo2_pattern_anomaly.log

  # Demo 3: Mixed Attack (Volume + Patterns)
  cd agent
  go run main.go ../demos/demo3_mixed_attack.log

  # Demo 4: Gradual Escalation (Slow-burn)
  cd agent
  go run main.go ../demos/demo4_gradual_escalation.log

  # Demo 5: Intermittent Attacks (Bursts)
  cd agent
  go run main.go ../demos/demo5_intermittent_attacks.log

Expected output in Terminal 3:
  🚀 Starting LogIQ Agent...
  ⏳ Warming up (Sending Normal Traffic)...
  [Normal Mode] Sent 1000 / 5000 logs...
  ...
  🔥🔥🔥 SWITCHING TO ATTACK MODE! UNLEASHING LOGS! 🔥🔥🔥
  [ATTACK Mode] Sent 7000 logs!!!
  ✅ Log File processing complete.

Expected output in Terminal 2 (Analyzer):
  [Learning Phase] Data points: 1/5 | Current Traffic: 98 logs/s
  [Learning Phase] Data points: 2/5 | Current Traffic: 102 logs/s
  ...
  ✅ BASELINE ESTABLISHED!
     Mean: 100 logs/s | StdDev: 2.50
     Known templates: 4
     🚀 Detection mode ACTIVE

  [✅ NORMAL] Traffic: 100 logs/s | Threshold: 115 | Baseline: 100

  ==================================================================
  🚨 FREQUENCY ANOMALY DETECTED! 🚨
  ==================================================================
     Actual Traffic: 1245 logs/s
     Expected Max: 120 logs/s
     Baseline Mean: 100 logs/s
     Deviation: 9.50x Sigma
     ✅ Saved to database
  ==================================================================

═══════════════════════════════════════════════════════════════

VIEWING RESULTS
─────────────────────────────────────────────────────────────

After agent completes (Terminal 3), in any terminal:

  cd backend
  python3 eval.py

Or connect to database:
  psql -h localhost -U admin -d logiq
  
  SELECT COUNT(*) FROM logs;
  SELECT * FROM anomalies ORDER BY detected_at DESC;

Or view Grafana:
  http://localhost:3000 (admin/admin)

═══════════════════════════════════════════════════════════════

TRYING DIFFERENT DEMOS
─────────────────────────────────────────────────────────────

To run a different demo:

1. Agent finishes (Terminal 3)
2. Stop Analyzer (Terminal 2) - Ctrl+C
3. Start new Analyzer run: python3 analyzer_enhanced.py fresh
4. Run new agent demo (Terminal 3):
   cd agent
   go run main.go ../demos/demo2_pattern_anomaly.log

This ensures fresh baseline for each demo!

═══════════════════════════════════════════════════════════════

TROUBLESHOOTING
─────────────────────────────────────────────────────────────

Backend not responding?
  curl http://localhost:8000/
  Should see: {"status":"Online",...}

Analyzer not connecting to DB?
  docker-compose logs db
  Check PostgreSQL is running

Agent connection refused?
  Check backend is running: lsof -i :8000
  Add sleep in agent if needed

Demo files missing?
  cd backend
  python3 generate_demos.py

═══════════════════════════════════════════════════════════════

QUICK SUMMARY
─────────────────────────────────────────────────────────────

Terminal 1: cd backend && python3 main.py
Terminal 2: cd backend && python3 analyzer_enhanced.py fresh
Terminal 3: cd agent && go run main.go ../demos/demo1_frequency_spike.log

Watch Terminal 2 for anomaly detection!

═══════════════════════════════════════════════════════════════
EOF
