package parser

import (
	"fmt"
	"regexp"
	"strings"
)

type Drain struct {
	Templates map[string]string
	Counter   int
}

func NewDrain() *Drain {
	return &Drain{
		Templates: make(map[string]string),
		Counter:   0,
	}
}

// UNIVERSAL RULES (Applied to ALL logs)
var (
	// 1. IPs (Standard IPv4)
	reIP = regexp.MustCompile(`\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`)

	// 2. Hex Values (0x4f, 0xDeadBeef) - Common in Linux/System logs
	reHex = regexp.MustCompile(`0x[0-9a-fA-F]+`)

	// 3. THE "MAGIC" RULE: Any sequence of digits is treated as a Variable
	// This automatically handles IDs, Timestamps, Ports, PIDs, BlockIDs, etc.
	reNum = regexp.MustCompile(`\d+`)
)

func (d *Drain) Parse(log string) (string, string) {
	// --- STEP 1: UNIVERSAL SANITIZATION ---
	// We replace specific formats first, then generic numbers.
	cleanLog := log
	cleanLog = reIP.ReplaceAllString(cleanLog, "<IP>")
	cleanLog = reHex.ReplaceAllString(cleanLog, "<HEX>")

	// The "Nuclear Option": Turn ALL remaining digits into <NUM>.
	// Example: "sshd[1234]" -> "sshd[<NUM>]"
	// Example: "blk_-1234" -> "blk_-<NUM>"
	// Example: "2025-10-10" -> "<NUM>-<NUM>-<NUM>"
	cleanLog = reNum.ReplaceAllString(cleanLog, "<NUM>")

	// --- STEP 2: CLUSTERING ---
	tokens := strings.Fields(cleanLog)
	if len(tokens) == 0 {
		return "", ""
	}

	// We calculate the signature using Log Length + First 4 Tokens.
	// Since we masked all numbers, "sshd[1234]" and "sshd[5678]"
	// are now Identical ("sshd[<NUM>]"), so they naturally group together.
	scanLen := 4
	if len(tokens) < 4 {
		scanLen = len(tokens)
	}

	signature := fmt.Sprintf("%d %s", len(tokens), strings.Join(tokens[:scanLen], " "))

	// --- STEP 3: MATCH ---
	if existingID, exists := d.Templates[signature]; exists {
		return existingID, cleanLog
	}

	d.Counter++
	eventID := fmt.Sprintf("E%d", d.Counter)
	d.Templates[signature] = eventID

	return eventID, cleanLog
}
