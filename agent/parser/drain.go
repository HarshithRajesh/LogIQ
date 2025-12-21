package parser

import (
	"regexp"
	"strings"
)

type Drain struct {
	// Simple map to store learned templates: Length -> list of templates
	Templates map[int][]string
}

func NewDrain() *Drain {
	return &Drain{
		Templates: make(map[int][]string),
	}
}

// Parse takes a raw log line and returns the template
func (d *Drain) Parse(log string) string {
	// 1. Pre-processing: Remove numbers and simple dynamic variables
	re := regexp.MustCompile(`\d+`)
	cleaned := re.ReplaceAllString(log, "<*>")

	tokens := strings.Fields(cleaned)
	length := len(tokens)

	// 2. Check if we have seen this structure
	if _, exists := d.Templates[length]; !exists {
		d.Templates[length] = []string{cleaned}
		return cleaned
	}

	// For this demo, we assume the cleaned string is the template
	// In a full production Drain, you would compare token similarity here.
	return cleaned
}
