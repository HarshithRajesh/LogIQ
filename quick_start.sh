#!/bin/bash
# Quick Start Guide for LogIQ Demos
# This script sets up and runs your first demo

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║  LogIQ - Real-time Log Anomaly Detection System       ║"
echo "║         Quick Start Guide                             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Step 1: Starting Docker Infrastructure...${NC}"
docker-compose up -d
sleep 3
echo -e "${GREEN}✅ Docker containers running${NC}"
echo ""

echo -e "${BLUE}Step 2: Generating Demo Log Files...${NC}"
cd backend
python3 generate_demos.py
cd ..
echo -e "${GREEN}✅ Demo files created in /demos${NC}"
echo ""

echo -e "${BLUE}Step 3: Starting Backend Server...${NC}"
cd backend
python3 main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
# Wait longer for backend to fully start
for i in {1..10}; do
  if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend running on http://localhost:8000${NC}"
    break
  fi
  if [ $i -eq 10 ]; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    cat /tmp/backend.log
    exit 1
  fi
  echo "  Waiting for backend... ($i/10)"
  sleep 1
done
cd ..
echo ""

echo -e "${BLUE}Step 4: Starting Analyzer in Fresh Mode...${NC}"
cd backend
timeout 120 python3 analyzer_enhanced.py fresh > /tmp/analyzer.log 2>&1 &
ANALYZER_PID=$!
# Give analyzer time to connect to DB and start
sleep 3
cd ..
echo -e "${GREEN}✅ Analyzer started (learning baseline)${NC}"
echo ""

echo -e "${BLUE}Step 5: Running Demo 1 - Frequency Spike Attack...${NC}"
echo "  (5000 normal logs @ 100/sec, then 2000 attack logs @ 1000+/sec)"
cd agent
go run main.go ../demos/demo1_frequency_spike.log
cd ..

if [ ! -f /tmp/analyzer.log ]; then
  echo -e "${RED}❌ Analyzer log not found${NC}"
  exit 1
fi
echo ""

echo -e "${BLUE}Step 6: Letting Analyzer Finish (30 seconds)...${NC}"
sleep 30
# Kill analyzer gracefully
if [ ! -z "$ANALYZER_PID" ] && kill -0 $ANALYZER_PID 2>/dev/null; then
  kill $ANALYZER_PID 2>/dev/null
  sleep 1
fi
# Kill backend
if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
  kill $BACKEND_PID 2>/dev/null
fi
echo ""

echo -e "${BLUE}Step 7: Viewing Results...${NC}"
cd backend
python3 eval.py
cd ..
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo -e "${GREEN}║                  ✅ Demo Complete!               ║${NC}"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results Summary:"
echo "  - Check database entries in PostgreSQL"
echo "  - View Grafana dashboards: http://localhost:3000"
echo "  - Run more demos from /demos folder"
echo ""
echo "🎯 Try other demos:"
echo "  agent/main.go ../demos/demo2_pattern_anomaly.log"
echo "  agent/main.go ../demos/demo3_mixed_attack.log"
echo "  agent/main.go ../demos/demo4_gradual_escalation.log"
echo "  agent/main.go ../demos/demo5_intermittent_attacks.log"
echo ""
echo "📖 For detailed guide, see: DEMO_GUIDE.md"
