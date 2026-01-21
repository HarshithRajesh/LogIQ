#!/bin/bash
# Demo Runner for LogIQ
# Usage: ./run_demo.sh demo1|demo2|demo3|demo4|demo5|all

set -e

DEMO_DIR="demos"
AGENT_DIR="agent"
BACKEND_DIR="backend"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found${NC}"
        exit 1
    fi
    
    if ! command -v go &> /dev/null; then
        echo -e "${RED}❌ Go not found${NC}"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

# Ensure demo files exist
generate_demos() {
    echo -e "${BLUE}📂 Generating demo log files...${NC}"
    cd "${BACKEND_DIR}"
    python3 generate_demos.py
    cd ..
}

# Start infrastructure
start_infrastructure() {
    echo -e "${BLUE}🐳 Checking Docker containers...${NC}"
    
    # Check if containers are running
    if ! docker ps | grep -q logiq_db; then
        echo -e "${YELLOW}Starting Docker containers...${NC}"
        docker-compose up -d
        echo -e "${YELLOW}Waiting for services to be ready...${NC}"
        sleep 5
    else
        echo -e "${GREEN}✅ Containers already running${NC}"
    fi
}

# Start backend
start_backend() {
    echo -e "${BLUE}🚀 Starting backend server...${NC}"
    
    # Check if backend is already running
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend already running${NC}"
        return
    fi
    
    cd "${BACKEND_DIR}"
    python3 main.py > /tmp/logiq_backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/logiq_backend.pid
    
    # Wait for backend to start
    echo -e "${YELLOW}Waiting for backend to start...${NC}"
    sleep 3
    
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend running (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${RED}❌ Backend failed to start${NC}"
        cat /tmp/logiq_backend.log
        exit 1
    fi
    cd ..
}

# Run demo
run_demo() {
    local demo_name=$1
    local demo_file="${DEMO_DIR}/${demo_name}.log"
    
    if [ ! -f "$demo_file" ]; then
        echo -e "${RED}❌ Demo file not found: $demo_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📊 Running: ${demo_name}${NC}"
    echo -e "${YELLOW}Description:${NC}"
    
    case $demo_name in
        demo1_frequency_spike)
            echo "  Frequency Spike Attack (DDoS-like)"
            echo "  - 5000 normal logs at regular rate"
            echo "  - 2000 attack logs at 10x rate"
            echo "  Expected: FREQUENCY anomaly when attack phase starts"
            ;;
        demo2_pattern_anomaly)
            echo "  Pattern Anomaly (New error templates)"
            echo "  - 5000 normal logs"
            echo "  - 2000 new/unknown error patterns"
            echo "  Expected: PATTERN anomaly with new templates"
            ;;
        demo3_mixed_attack)
            echo "  Mixed Attack (Volume + New patterns)"
            echo "  - 5000 normal logs"
            echo "  - 2000 high-volume attack logs with new error templates"
            echo "  Expected: Both FREQUENCY and PATTERN anomalies"
            ;;
        demo4_gradual_escalation)
            echo "  Gradual Escalation (Slow-burn attack)"
            echo "  - 5 phases with increasing traffic"
            echo "  Expected: FREQUENCY anomaly as traffic escalates"
            ;;
        demo5_intermittent_attacks)
            echo "  Intermittent Attacks (Multiple bursts)"
            echo "  - Multiple attack bursts interspersed with normal traffic"
            echo "  Expected: Multiple FREQUENCY anomalies"
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}Starting analyzer in fresh mode...${NC}"
    cd "${BACKEND_DIR}"
    timeout 120 python3 analyzer_enhanced.py fresh &
    ANALYZER_PID=$!
    echo $ANALYZER_PID > /tmp/logiq_analyzer.pid
    cd ..
    
    # Give analyzer time to clear tables
    sleep 2
    
    echo -e "${YELLOW}Sending log file to agent...${NC}"
    cd "${AGENT_DIR}"
    go run main.go "../${demo_file}"
    cd ..
    
    # Keep analyzer running for 30 more seconds to catch all anomalies
    echo -e "${YELLOW}Analyzing results (30 more seconds)...${NC}"
    sleep 30
    
    # Kill analyzer
    if [ -f /tmp/logiq_analyzer.pid ]; then
        kill $(cat /tmp/logiq_analyzer.pid) 2>/dev/null || true
        rm /tmp/logiq_analyzer.pid
    fi
    
    echo ""
    echo -e "${GREEN}✅ Demo complete!${NC}"
}

# View results
view_results() {
    echo -e "${BLUE}📊 Viewing anomaly detection results...${NC}"
    cd "${BACKEND_DIR}"
    python3 eval.py
    cd ..
}

# Main menu
show_menu() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           LogIQ Demo - Anomaly Detection                  ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Available demos:"
    echo "  1. demo1_frequency_spike      - DDoS-like volume spike"
    echo "  2. demo2_pattern_anomaly      - New error templates"
    echo "  3. demo3_mixed_attack         - Combined volume + patterns"
    echo "  4. demo4_gradual_escalation   - Slow-burn attack"
    echo "  5. demo5_intermittent_attacks - Multiple attack bursts"
    echo ""
    echo "Usage:"
    echo "  ./run_demo.sh demo1_frequency_spike"
    echo "  ./run_demo.sh demo2_pattern_anomaly"
    echo "  ./run_demo.sh all              (run all demos sequentially)"
    echo "  ./run_demo.sh view             (show results)"
    echo ""
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        show_menu
        exit 1
    fi
    
    check_prerequisites
    generate_demos
    start_infrastructure
    start_backend
    
    if [ "$1" = "all" ]; then
        echo -e "${GREEN}Running all demos...${NC}"
        run_demo "demo1_frequency_spike"
        echo ""
        echo -e "${YELLOW}Press Enter to continue to next demo...${NC}"
        read
        run_demo "demo2_pattern_anomaly"
        echo ""
        echo -e "${YELLOW}Press Enter to continue to next demo...${NC}"
        read
        run_demo "demo3_mixed_attack"
        echo ""
        echo -e "${YELLOW}Press Enter to continue to next demo...${NC}"
        read
        run_demo "demo4_gradual_escalation"
        echo ""
        echo -e "${YELLOW}Press Enter to continue to next demo...${NC}"
        read
        run_demo "demo5_intermittent_attacks"
    elif [ "$1" = "view" ]; then
        view_results
    else
        run_demo "$1"
    fi
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    Demo Summary                           ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    view_results
}

main "$@"
