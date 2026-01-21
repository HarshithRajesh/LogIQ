#!/bin/bash
# LogIQ Setup Guide - Choose Your Preferred Method

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║           LogIQ Setup - Choose Your Method                  ║
╚═══════════════════════════════════════════════════════════════╝

METHOD 1: Manual (Recommended for Seeing Everything)
────────────────────────────────────────────────────
This gives you full control and visibility of what's happening

  open MANUAL_SETUP.md
  # Follow the 3-terminal setup

  OR directly:
  Terminal 1: cd backend && python3 main.py
  Terminal 2: cd backend && python3 analyzer_enhanced.py fresh
  Terminal 3: cd agent && go run main.go ../demos/demo1_frequency_spike.log

METHOD 2: Run Individual Demo
──────────────────────────────
Run automated demos with the runner script

  ./run_demo.sh demo1_frequency_spike
  ./run_demo.sh demo2_pattern_anomaly
  ./run_demo.sh demo3_mixed_attack
  ./run_demo.sh all

METHOD 3: Quick One-Command
────────────────────────────
Runs everything in background (less visible but automated)

  ./quick_start.sh
  
Note: You may see 0 logs due to timing. 
Use METHOD 1 or 2 for better results!

═══════════════════════════════════════════════════════════════

RECOMMENDED FOR YOU:
────────────────────
Since you prefer manual 3-terminal setup, use METHOD 1

See MANUAL_SETUP.md for detailed instructions
EOF
