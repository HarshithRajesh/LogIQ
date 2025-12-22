// "github.com/HarshithRajesh/LogIQ/parser"
package main

import (
	"bufio"
	"fmt"
	"github.com/HarshithRajesh/LogIQ/parser"
	"log"
	"os"
	"sort"
	"strings"
	"time"
)

func main() {
	// 1. Get Filename from Command Line
	if len(os.Args) < 2 {
		fmt.Println("❌ Usage: go run benchmark.go <filename>")
		return
	}
	filename := os.Args[1]

	// 2. Open File
	file, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	fmt.Printf("📊 BENCHMARKING: %s\n", filename)

	drain := parser.NewDrain()
	counts := make(map[string]int)
	templates := make(map[string]string)
	totalLogs := 0

	scanner := bufio.NewScanner(file)

	// 3. START TIMER
	start := time.Now()

	// 4. PROCESS (One Pass)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.TrimSpace(line) == "" {
			continue
		}

		id, template := drain.Parse(line)

		// Store stats
		if _, exists := templates[id]; !exists {
			templates[id] = template
		}
		counts[id]++
		totalLogs++
	}

	// 5. STOP TIMER
	duration := time.Since(start)
	logsPerSec := float64(totalLogs) / duration.Seconds()

	// 6. OUTPUT
	fmt.Println("\n✅ COMPLETE")
	fmt.Printf("⏱️  Time: %.4fs | ⚡ Speed: %.2f logs/sec | 📂 Count: %d\n", duration.Seconds(), logsPerSec, totalLogs)

	fmt.Println("\n📝 TEMPLATES FOUND:")
	fmt.Println("----------------------------------------------------------------------")
	fmt.Printf("%-5s | %-6s | %s\n", "ID", "Count", "Template Structure")
	fmt.Println("----------------------------------------------------------------------")

	// Sort & Print
	type Row struct {
		ID  string
		Num int
	}
	var rows []Row
	for id := range templates {
		var num int
		fmt.Sscanf(id, "E%d", &num)
		rows = append(rows, Row{id, num})
	}
	sort.Slice(rows, func(i, j int) bool { return rows[i].Num < rows[j].Num })

	for _, r := range rows {
		// Truncate for cleaner display
		text := templates[r.ID]
		if len(text) > 75 {
			text = text[:72] + "..."
		}
		fmt.Printf("%-5s | %-6d | %s\n", r.ID, counts[r.ID], text)
	}
	fmt.Println("----------------------------------------------------------------------")
}
