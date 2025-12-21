package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"github.com/HarshithRajesh/LogIQ/parser"
	"log"
	"net/http"
	"os"
	"time"
)

const (
	ServerURL = "http://localhost:8000/ingest"
	LogFile   = "final_demo.log"
	// REVISED: Must match the generator count
	NormalLimit = 5000
	BatchSize   = 50
)

type LogData struct {
	Content  string `json:"content"`
	Template string `json:"template"`
}

func main() {
	fmt.Println("🚀 Starting LogIQ Agent...")
	fmt.Println("⏳ Warming up (Sending Normal Traffic)...")

	drain := parser.NewDrain()

	file, err := os.Open(LogFile)
	if err != nil {
		log.Fatalf("Error opening file: %v. Run generate_dataset.py first!", err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var batch []LogData
	lineCount := 0

	// Small delay to ensure DB is ready if you ran docker-compose just now
	time.Sleep(2 * time.Second)

	for scanner.Scan() {
		lineCount++
		rawLog := scanner.Text()
		template := drain.Parse(rawLog)

		batch = append(batch, LogData{Content: rawLog, Template: template})

		if len(batch) >= BatchSize {
			sendBatch(batch)
			batch = nil
		}

		// --- THROTTLING LOGIC ---
		if lineCount < NormalLimit {
			// Normal Mode: 10ms sleep = ~100 logs/sec (approx)
			// This creates a stable baseline for the Python script
			time.Sleep(10 * time.Millisecond)

			if lineCount%500 == 0 {
				fmt.Printf("\r[Normal Mode] Sent %d / %d logs...", lineCount, NormalLimit)
			}
		} else {
			// Attack Mode: NO SLEEP = Max speed (1000+ logs/sec)
			if lineCount == NormalLimit+1 {
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

