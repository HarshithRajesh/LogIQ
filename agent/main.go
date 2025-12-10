package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"
	// "strings"
	"time"

	"github.com/HarshithRajesh/LogIQ/parser"
)

// LogEntry represents the structure expected by the backend API
type LogEntry struct {
	Timestamp   string   `json:"timestamp"`
	ServiceName string   `json:"service_name"`
	Severity    string   `json:"severity"`
	TemplateID  string   `json:"template_id"`
	LogTemplate string   `json:"log_template"`
	Parameters  []string `json:"parameters"`
	RawMessage  string   `json:"raw_message"`
}

const (
	logFile     = "final_demo.log"
	apiEndpoint = "http://localhost:8000/ingest"

	// Auto-Pilot Mode Thresholds
	normalBatchSize = 50
	normalSleep     = 100 * time.Millisecond
	attackBatchSize = 500
	attackThreshold = 30000
)

var (
	severityRegex = regexp.MustCompile(`\[(INFO|DEBUG|WARN|ERROR|CRITICAL)\]`)
	serviceRegex  = regexp.MustCompile(`\]\s+([a-z\-]+):`)
)

func main() {
	fmt.Println("=================================================")
	fmt.Println("LogIQ Agent - Real-time Log Ingestion")
	fmt.Println("=================================================")

	// Initialize Drain parser
	drainParser := parser.NewDrainParser()

	// Open log file
	file, err := os.Open(logFile)
	if err != nil {
		log.Fatalf("Error opening log file: %v", err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	var batch []LogEntry
	lineNumber := 0
	totalSent := 0

	fmt.Println("\n🚀 Starting log ingestion in Auto-Pilot Mode...")
	fmt.Println("   Phase 1 (Lines 0-30000): Steady stream (50/batch, 100ms delay)")
	fmt.Println("   Phase 2 (Lines 30000+): Attack simulation (500/batch, no delay)")
	fmt.Println()

	startTime := time.Now()

	for scanner.Scan() {
		line := scanner.Text()
		lineNumber++

		// Parse log line using Drain
		templateID, templateStr, params := drainParser.Parse(line)

		// Extract metadata from log line
		severity := extractSeverity(line)
		serviceName := extractServiceName(line)

		// Create log entry with LIVE timestamp (time.Now())
		entry := LogEntry{
			Timestamp:   time.Now().Format(time.RFC3339),
			ServiceName: serviceName,
			Severity:    severity,
			TemplateID:  templateID,
			LogTemplate: templateStr,
			Parameters:  params,
			RawMessage:  line,
		}

		batch = append(batch, entry)

		// Auto-Pilot Mode Logic
		var shouldSend bool
		var sleepDuration time.Duration

		if lineNumber < attackThreshold {
			// Normal Phase: Send in batches of 50, sleep 100ms
			shouldSend = len(batch) >= normalBatchSize
			sleepDuration = normalSleep
		} else {
			// Attack Phase: Send in batches of 500, no sleep
			shouldSend = len(batch) >= attackBatchSize
			sleepDuration = 0

			// Print attack phase notification once
			if lineNumber == attackThreshold {
				fmt.Println("\n🔴 ATTACK PHASE INITIATED - Simulating DDoS")
				fmt.Println("   Batch size: 500 | Sleep: 0ms\n")
			}
		}

		// Send batch when threshold is reached
		if shouldSend {
			if err := sendBatch(batch); err != nil {
				log.Printf("❌ Error sending batch: %v", err)
			} else {
				totalSent += len(batch)

				// Print progress
				if lineNumber < attackThreshold {
					if totalSent%500 == 0 {
						fmt.Printf("✅ Sent %d logs (Line %d) - Normal Phase\n", totalSent, lineNumber)
					}
				} else {
					fmt.Printf("🔥 Sent %d logs (Line %d) - ATTACK PHASE\n", totalSent, lineNumber)
				}
			}

			batch = []LogEntry{}

			// Sleep if in normal phase
			if sleepDuration > 0 {
				time.Sleep(sleepDuration)
			}
		}
	}

	// Send remaining logs
	if len(batch) > 0 {
		if err := sendBatch(batch); err != nil {
			log.Printf("❌ Error sending final batch: %v", err)
		} else {
			totalSent += len(batch)
		}
	}

	if err := scanner.Err(); err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	elapsed := time.Since(startTime)

	fmt.Println("\n=================================================")
	fmt.Println("✅ Log Ingestion Complete!")
	fmt.Println("=================================================")
	fmt.Printf("Total logs sent: %d\n", totalSent)
	fmt.Printf("Total lines processed: %d\n", lineNumber)
	fmt.Printf("Time elapsed: %v\n", elapsed)
	fmt.Printf("Logs per second: %.2f\n", float64(totalSent)/elapsed.Seconds())
	fmt.Println("=================================================")
}

// sendBatch sends a batch of log entries to the backend API
func sendBatch(batch []LogEntry) error {
	jsonData, err := json.Marshal(batch)
	if err != nil {
		return fmt.Errorf("error marshaling JSON: %w", err)
	}

	resp, err := http.Post(apiEndpoint, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	return nil
}

// extractSeverity extracts severity level from log line
func extractSeverity(line string) string {
	matches := severityRegex.FindStringSubmatch(line)
	if len(matches) > 1 {
		return matches[1]
	}
	return "INFO"
}

// extractServiceName extracts service name from log line
func extractServiceName(line string) string {
	matches := serviceRegex.FindStringSubmatch(line)
	if len(matches) > 1 {
		return matches[1]
	}
	return "unknown-service"
}
