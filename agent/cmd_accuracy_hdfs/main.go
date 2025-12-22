package main

// Accuracy benchmark for the Drain-style parser using the public HDFS_2k dataset.
// It compares our parsed / normalized template against the EventTemplate column
// from HDFS_2k.log_structured.csv to estimate parsing accuracy.
//
// Usage:
//   cd agent
//   go run ./cmd_accuracy_hdfs
//
// Notes:
//   - We treat "<*>" in the ground-truth template as a generic variable token.
//   - We map our "<IP>", "<HEX>", and "<NUM>" tokens to the same generic "<VAR>"
//     token before comparison. This rewards correct structure even if the
//     variable-type tag differs.

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/HarshithRajesh/LogIQ/parser"
)

const (
	// Relative to the agent/ directory when you `cd agent`.
	hdfsStructuredPath = "benchmark/HDFS_2k.log_structured.csv"
)

func main() {
	fmt.Println("📊 Evaluating Drain parsing accuracy on HDFS_2k.log_structured.csv")

	f, err := os.Open(hdfsStructuredPath)
	if err != nil {
		log.Fatalf("failed to open %s: %v", hdfsStructuredPath, err)
	}
	defer f.Close()

	r := csv.NewReader(f)
	r.FieldsPerRecord = -1 // allow variable-length records just in case

	records, err := r.ReadAll()
	if err != nil {
		log.Fatalf("failed to read CSV: %v", err)
	}

	if len(records) <= 1 {
		log.Fatalf("CSV appears to be empty or missing data rows")
	}

	// CSV header:
	// LineId,Date,Time,Pid,Level,Component,Content,EventId,EventTemplate
	// We will always take the last two columns as (EventId, EventTemplate)
	const minColumns = 9

	drain := parser.NewDrain()

	var total int
	var matches int

	for i, rec := range records {
		// Skip header
		if i == 0 {
			continue
		}

		if len(rec) < minColumns {
			// Skip malformed rows but keep going
			continue
		}

		content := rec[6]
		gtTemplate := rec[len(rec)-1]

		_, parsedTemplate := drain.Parse(content)

		normGT := normalizeGroundTruth(gtTemplate)
		normParsed := normalizeParsed(parsedTemplate)

		total++
		if normGT == normParsed {
			matches++
		}
	}

	if total == 0 {
		log.Fatalf("no valid rows found in CSV")
	}

	accuracy := float64(matches) / float64(total) * 100.0
	fmt.Printf("✅ HDFS_2k parsing accuracy: %.2f%% (%d / %d lines matched)\n", accuracy, matches, total)
}

// normalizeGroundTruth converts the HDFS EventTemplate with "<*>" placeholders
// into a comparable form that uses "<VAR>" for all variable positions.
func normalizeGroundTruth(t string) string {
	// Treat every "<*>" as a variable.
	norm := strings.ReplaceAll(t, "<*>", "<VAR>")
	// Trim spaces for robustness
	return strings.TrimSpace(norm)
}

// normalizeParsed maps our Drain placeholders (<IP>, <HEX>, <NUM>) to "<VAR>"
// so we can compare structural similarity against the ground truth.
func normalizeParsed(t string) string {
	norm := t
	norm = strings.ReplaceAll(norm, "<IP>", "<VAR>")
	norm = strings.ReplaceAll(norm, "<HEX>", "<VAR>")
	norm = strings.ReplaceAll(norm, "<NUM>", "<VAR>")
	return strings.TrimSpace(norm)
}


