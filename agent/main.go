package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/HarshithRajesh/LogIQ/parser"
)

const (
	ServerURL          = "http://localhost:8000/ingest"
	BatchSize          = 50
	DefaultNormalLimit = 5000 // Default: first 5000 logs are "normal", rest are "attack"
)

type LogData struct {
	Content  string `json:"content"`
	Template string `json:"template"`
}

func main() {
	// Get log file from command line argument or use default
	var logFile string
	if len(os.Args) > 1 {
		logFile = os.Args[1]
	} else {
		logFile = "final_demo.log"
	}

	fmt.Println("🚀 Starting LogIQ Agent...")
	fmt.Printf("📂 Reading log file: %s\n", logFile)
	fmt.Println("⏳ Warming up (Sending Normal Traffic)...")

	drain := parser.NewDrain()

	file, err := os.Open(logFile)
	if err != nil {
		log.Fatalf("Error opening file: %v. Run generate_dataset.py first!", err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var batch []LogData
	lineCount := 0
	normalLimit := DefaultNormalLimit

	// IMPORTANT: Wait for backend to be ready AND give analyzer time to start learning
	// Learning phase takes ~10 seconds (5 windows × 2 seconds each)
	// So we wait 12 seconds to ensure learning is in progress before sending logs
	fmt.Println("\n⏱️  Waiting 12 seconds for analyzer to initialize...")
	for i := 12; i > 0; i-- {
		fmt.Printf("\r   Starting in %2d seconds...", i)
		time.Sleep(1 * time.Second)
	}
	fmt.Println("\r✅ Analyzer initialized. Starting log transmission!\n")

	for scanner.Scan() {
		lineCount++
		rawLog := scanner.Text()
		_, template := drain.Parse(rawLog)

		batch = append(batch, LogData{Content: rawLog, Template: template})

		if len(batch) >= BatchSize {
			sendBatch(batch)
			batch = nil
		}

		// --- THROTTLING LOGIC ---
		if lineCount < normalLimit {
			// Normal Mode: 10ms sleep = ~100 logs/sec (approx)
			// This creates a stable baseline for the Python script
			time.Sleep(10 * time.Millisecond)

			if lineCount%500 == 0 {
				fmt.Printf("\r[Normal Mode] Sent %d / %d logs...", lineCount, normalLimit)
			}
		} else {
			// Attack Mode: NO SLEEP = Max speed (1000+ logs/sec)
			if lineCount == normalLimit+1 {
				fmt.Println("\n\n🔥🔥🔥 SWITCHING TO ATTACK MODE! UNLEASHING LOGS! 🔥🔥🔥")
			}
			if lineCount%200 == 0 {
				fmt.Printf("\r[ATTACK Mode] Sent %d logs!!!", lineCount)
			}
		}
	}

	if len(batch) > 0 {
		sendBatch(batch)
	}
	fmt.Println("\n✅ Log File processing complete.")
}

func sendBatch(logs []LogData) {
	jsonData, _ := json.Marshal(logs)
	http.Post(ServerURL, "application/json", bytes.NewBuffer(jsonData))
}
