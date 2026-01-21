# LogIQ Enhancement Summary

## Problem Identified

When running the analyzer on the final logs (5k normal + 2k attack), on the **first run**, everything was detected as anomalies. On **subsequent runs** after truncating the table, **nothing was detected**. This happened because:

1. **First Run Issue**: During learning phase, the analyzer was building baseline with attack logs still in database
2. **Subsequent Runs Issue**: All templates were already marked as "seen" in the `known_templates` table, so no new pattern anomalies would trigger
3. **Single Scenario**: Only one attack pattern was available, making it impossible to demonstrate different detection capabilities

## Solution Implemented

Created a **comprehensive multi-scenario demo system** with 5 distinct attack patterns, each showcasing different anomaly types.

---

## Components Added/Modified

### 1. **generate_demos.py** (NEW)
Creates 5 different log file scenarios:
- Each with 7,000 total logs (7k to match original count)
- Different attack patterns and signatures
- Customizable for future extensions

**Files Generated:**
```
demos/
├── demo1_frequency_spike.log      (5k normal + 2k attack @ high rate)
├── demo2_pattern_anomaly.log      (5k normal + 2k new error templates)
├── demo3_mixed_attack.log         (5k normal + 2k volume + patterns)
├── demo4_gradual_escalation.log   (7k with gradually increasing rate)
└── demo5_intermittent_attacks.log (alternating normal/attack bursts)
```

### 2. **analyzer_enhanced.py** (NEW)
Improved analyzer with two key modes:

```bash
python3 analyzer_enhanced.py fresh      # Clear tables + start fresh
python3 analyzer_enhanced.py continue   # Analyze existing logs
```

**Key Improvements:**
- ✅ Fresh mode clears `logs`, `anomalies`, and `known_templates` tables
- ✅ Better learning phase tracking (explicit 5-window baseline)
- ✅ Clear transition from learning → detection mode
- ✅ Improved console output with visual separators
- ✅ Better baseline statistics reporting

### 3. **agent/main.go** (UPDATED)
Made flexible to accept any log file:

```bash
# Before: Hard-coded final_demo.log
go run main.go

# After: Accepts any log file
go run main.go ../demos/demo1_frequency_spike.log
go run main.go ../demos/demo2_pattern_anomaly.log
```

**Changes:**
- Removed hard-coded `LogFile` constant
- Added command-line argument handling
- Maintained backward compatibility

### 4. **run_demo.sh** (NEW)
Fully automated demo runner:

```bash
# Single demo
./run_demo.sh demo1_frequency_spike

# All demos
./run_demo.sh all

# View results
./run_demo.sh view
```

**Features:**
- ✅ Prerequisites checking
- ✅ Docker startup
- ✅ Backend initialization
- ✅ Analyzer startup in fresh mode
- ✅ Agent execution
- ✅ Result evaluation
- ✅ Color-coded output

### 5. **DEMO_GUIDE.md** (NEW)
Comprehensive guide covering:
- All 5 demo scenarios in detail
- Real-world attack analogs
- Expected detection patterns
- Manual and automated execution
- Troubleshooting guide
- Architecture diagrams
- Performance metrics

### 6. **quick_start.sh** (NEW)
One-command setup for first-time users

---

## Demo Scenarios Explained

### Demo 1: Frequency Spike (DDoS-like)
- **Pattern:** 5k normal logs, then 2k attack logs at 10x rate
- **Detection:** ✅ Frequency anomaly (volume spike)
- **Real-world:** DDoS attacks, bot-driven volume spikes
- **Output:** Single large deviation event

### Demo 2: Pattern Anomaly (New Errors)
- **Pattern:** 5k normal logs, then 2k new error templates
- **Detection:** ✅ Pattern anomalies (new templates), ❌ No frequency anomaly
- **Real-world:** New malware, zero-day exploits, novel attack signatures
- **Output:** Multiple new template alerts

### Demo 3: Mixed Attack (Volume + Patterns)
- **Pattern:** 5k normal logs, then 2k high-volume attack with new patterns
- **Detection:** ✅ Both frequency AND pattern anomalies
- **Real-world:** Sophisticated multi-vector attacks, combined breaches
- **Output:** Combined frequency + pattern alerts

### Demo 4: Gradual Escalation (Slow-burn)
- **Pattern:** 7k logs with traffic gradually increasing over time
- **Detection:** ✅ Frequency anomalies as traffic crosses thresholds
- **Real-world:** Slow-and-low attacks, resource exhaustion, botnet ramp-up
- **Output:** Multiple anomalies as escalation happens

### Demo 5: Intermittent Attacks (Multiple Bursts)
- **Pattern:** Alternating normal/attack phases throughout the log stream
- **Detection:** ✅ Multiple frequency anomalies (one per burst)
- **Real-world:** Reconnaissance attacks, multi-phase breaches, scheduled attacks
- **Output:** Repeated anomaly events with baseline recovery

---

## How It Solves the Original Problem

### ❌ Original Issue 1: "Everything detected as anomaly on first run"
**Solution:** Demo files have clean separation. Learning phase (5 windows) uses only normal logs before any anomalies are tested.

### ❌ Original Issue 2: "Nothing detected on reruns"
**Solution:** Use `analyzer_enhanced.py fresh` mode to:
- Clear the `known_templates` table
- Reset in-memory template tracking
- Start fresh learning phase

### ❌ Original Issue 3: "Can't show different attack patterns"
**Solution:** 5 different demo files showcase:
- Volume-based attacks
- Signature-based attacks  
- Combined attacks
- Gradual attacks
- Multi-phase attacks

---

## Usage Workflow

### Option A: Automated (Recommended)
```bash
# Make script executable
chmod +x run_demo.sh quick_start.sh

# Run first demo automatically
./quick_start.sh

# Run other demos
./run_demo.sh demo2_pattern_anomaly
./run_demo.sh demo3_mixed_attack
./run_demo.sh all  # Run all demos sequentially
```

### Option B: Manual Control
```bash
# Terminal 1: Backend
cd backend && python3 main.py

# Terminal 2: Analyzer (fresh mode for new demo)
cd backend && python3 analyzer_enhanced.py fresh

# Terminal 3: Agent
cd agent && go run main.go ../demos/demo1_frequency_spike.log

# Terminal 1: View results
cd backend && python3 eval.py
```

---

## Key Improvements Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Demo Files** | 1 fixed scenario | 5 different scenarios |
| **Reusability** | Had to manually truncate tables | Fresh mode automates cleanup |
| **Documentation** | README only | DEMO_GUIDE.md with details |
| **Attack Types** | Single DDoS pattern | 5 distinct patterns |
| **Automation** | Manual multi-step process | One-command demos |
| **Learning Phase** | Ambiguous | Explicit 5-window baseline |
| **Agent Flexibility** | Hard-coded log file | Command-line configurable |
| **Demo Variety** | Couldn't show different attacks | Showcase all detection types |

---

## Files Modified/Created

### New Files
- `backend/generate_demos.py` - Demo file generator
- `backend/analyzer_enhanced.py` - Enhanced analyzer with modes
- `run_demo.sh` - Automated demo runner
- `quick_start.sh` - One-command setup
- `DEMO_GUIDE.md` - Comprehensive guide

### Modified Files
- `agent/main.go` - Added command-line argument support

### Existing Files (Unchanged)
- `backend/main.py` - Backend API (no changes needed)
- `backend/eval.py` - Results evaluator (works with all demos)
- `database/init_schema.sql` - Database schema (no changes needed)

---

## Next Steps

1. **Try the demos:**
   ```bash
   ./quick_start.sh
   ```

2. **Explore different scenarios:**
   ```bash
   ./run_demo.sh demo2_pattern_anomaly
   ./run_demo.sh demo3_mixed_attack
   ```

3. **Customize for your needs:**
   - Edit `generate_demos.py` to add your own attack patterns
   - Adjust sensitivity in `analyzer_enhanced.py` (change `SIGMA_MULTIPLIER`)
   - Create new demo scenarios as needed

4. **Integrate with your monitoring:**
   - Connect to Grafana for visualization
   - Export anomalies to your SIEM
   - Set up alerts based on detection types

---

## Testing the Solution

To verify everything works:

```bash
# 1. Generate demos
python3 backend/generate_demos.py

# 2. Verify files created
ls -lh demos/

# 3. Run automated demo
./run_demo.sh demo1_frequency_spike

# 4. Try another scenario
./run_demo.sh demo2_pattern_anomaly
```

Expected result: Each demo should detect different anomaly types without needing to manually clear tables between runs.
