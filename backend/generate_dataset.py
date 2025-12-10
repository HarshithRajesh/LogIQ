ipackage parser

import (
	"crypto/md5"
	"fmt"
	"regexp"
	"strings"
	"sync"
)

// DrainNode represents a node in the Prefix Tree (Trie)
type DrainNode struct {
	Children map[string]*DrainNode
	Template string
	Count    int
}

// DrainParser implements the Drain algorithm using a Prefix Tree
type DrainParser struct {
	Root         *DrainNode
	Templates    map[string]string
	mu           sync.RWMutex
	simThreshold float64
	maxDepth     int
	numberRegex  *regexp.Regexp
}

// NewDrainParser creates a new Drain parser instance
func NewDrainParser() *DrainParser {
	return &DrainParser{
		Root:         &DrainNode{Children: make(map[string]*DrainNode)},
		Templates:    make(map[string]string),
		simThreshold: 0.5,
		maxDepth:     5,
		numberRegex:  regexp.MustCompile(`\b\d+\b`),
	}
}

// Parse processes a log line and returns templateID, template string, and parameters
func (d *DrainParser) Parse(logLine string) (string, string, []string) {
	d.mu.Lock()
	defer d.mu.Unlock()

	// Extract the actual log message (remove timestamp and metadata)
	message := d.extractMessage(logLine)
	
	// Tokenize the message
	tokens := strings.Fields(message)
	if len(tokens) == 0 {
		return "", "", []string{}
	}

	// Mask numbers in tokens for pattern matching
	maskedTokens := d.maskNumbers(tokens)
	
	// Search for matching template in the tree
	node := d.searchTree(maskedTokens)
	
	// Extract parameters by comparing original tokens with template
	params := d.extractParameters(tokens, strings.Fields(node.Template))
	
	// Generate template ID
	templateID := d.generateTemplateID(node.Template)
	
	return templateID, node.Template, params
}

// extractMessage removes timestamp and severity prefix from log line
func (d *DrainParser) extractMessage(logLine string) string {
	// Split by ']' to remove timestamp and severity
	parts := strings.Split(logLine, "]")
	if len(parts) >= 3 {
		// Return everything after "[SEVERITY] service:"
		return strings.TrimSpace(strings.Join(parts[2:], "]"))
	}
	return logLine
}

// maskNumbers replaces all numbers with <*> token
func (d *DrainParser) maskNumbers(tokens []string) []string {
	masked := make([]string, len(tokens))
	for i, token := range tokens {
		if d.numberRegex.MatchString(token) {
			masked[i] = "<*>"
		} else {
			masked[i] = token
		}
	}
	return masked
}

// searchTree traverses the prefix tree to find or create a matching template
func (d *DrainParser) searchTree(tokens []string) *DrainNode {
	node := d.Root
	depth := 0
	
	for depth < len(tokens) && depth < d.maxDepth {
		token := tokens[depth]
		
		// If exact match exists, follow it
		if child, exists := node.Children[token]; exists {
			node = child
			depth++
			continue
		}
		
		// Check for wildcard match
		if child, exists := node.Children["<*>"]; exists {
			node = child
			depth++
			continue
		}
		
		// No match found, create new branch
		newNode := &DrainNode{
			Children: make(map[string]*DrainNode),
			Template: strings.Join(tokens, " "),
			Count:    1,
		}
		node.Children[token] = newNode
		return newNode
	}
	
	// If we've reached a leaf or max depth, update count
	if node.Template == "" {
		node.Template = strings.Join(tokens, " ")
	}
	node.Count++
	
	return node
}

// extractParameters compares original tokens with template to extract variable values
func (d *DrainParser) extractParameters(original, template []string) []string {
	params := []string{}
	
	minLen := len(original)
	if len(template) < minLen {
		minLen = len(template)
	}
	
	for i := 0; i < minLen; i++ {
		if template[i] == "<*>" && original[i] != "<*>" {
			params = append(params, original[i])
		}
	}
	
	return params
}

// generateTemplateID creates a unique MD5 hash for the template
func (d *DrainParser) generateTemplateID(template string) string {
	hash := md5.Sum([]byte(template))
	return fmt.Sprintf("%x", hash[:8]) // Use first 8 bytes for shorter ID
}

// GetStats returns parser statistics
func (d *DrainParser) GetStats() map[string]int {
	d.mu.RLock()
	defer d.mu.RUnlock()
	
	stats := make(map[string]int)
	d.collectStats(d.Root, stats)
	return stats
}

func (d *DrainParser) collectStats(node *DrainNode, stats map[string]int) {
	if node.Template != "" {
		stats[node.Template] = node.Count
	}
	for _, child := range node.Children {
		d.collectStats(child, stats)
	}
}mport random
from datetime import datetime, timedelta

def generate_dataset():
    """
    Generate 50,000 logs with time compression to simulate normal operations and DDoS attack.
    
    Normal Phase: 30,000 logs with 50ms intervals
    Attack Phase: 2,000 logs with 1ms intervals (simulating DDoS)
    Remaining: 18,000 logs with 50ms intervals (recovery phase)
    """
    
    # Start timestamp: 2 hours ago
    current_time = datetime.now() - timedelta(hours=2)
    
    # Log templates for normal operations
    normal_templates = [
        "User {id} logged in",
        "Process started",
        "Request processed successfully",
        "Cache hit for key {id}",
        "API call to service {id} completed",
        "Session {id} created",
        "File {id} uploaded successfully",
        "Background job {id} completed",
        "Configuration reloaded",
        "Health check passed"
    ]
    
    # Attack template
    attack_template = "Database connection failed error {code}"
    
    # Service names
    services = ["auth-service", "api-gateway", "user-service", "payment-service", "notification-service"]
    
    # Severity levels
    normal_severity = ["INFO", "DEBUG", "WARN"]
    attack_severity = ["ERROR", "CRITICAL"]
    
    logs = []
    
    # Phase 1: Normal Phase - 30,000 logs
    print("Generating Normal Phase (30,000 logs)...")
    for i in range(30000):
        template = random.choice(normal_templates)
        service = random.choice(services)
        severity = random.choice(normal_severity)
        
        # Fill template with random ID
        if "{id}" in template:
            log_message = template.format(id=random.randint(1000, 9999))
        else:
            log_message = template
        
        # Format log entry
        log_entry = f"{current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} [{severity}] {service}: {log_message}"
        logs.append(log_entry)
        
        # Increment by 50ms for normal logs
        current_time += timedelta(milliseconds=50)
        
        if (i + 1) % 10000 == 0:
            print(f"  Generated {i + 1} normal logs...")
    
    # Phase 2: Attack Phase - 2,000 logs (DDoS simulation)
    print("Generating Attack Phase (2,000 logs - DDoS simulation)...")
    for i in range(2000):
        service = random.choice(services)
        severity = random.choice(attack_severity)
        error_code = random.choice([500, 502, 503, 504, 1062, 2003, 2006])
        
        # Fill attack template with error code
        log_message = attack_template.format(code=error_code)
        
        # Format log entry
        log_entry = f"{current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} [{severity}] {service}: {log_message}"
        logs.append(log_entry)
        
        # Increment by 1ms for attack logs (TIME COMPRESSION - simulating DDoS)
        current_time += timedelta(milliseconds=1)
        
        if (i + 1) % 500 == 0:
            print(f"  Generated {i + 1} attack logs...")
    
    # Phase 3: Recovery Phase - 18,000 logs (back to normal)
    print("Generating Recovery Phase (18,000 logs)...")
    for i in range(18000):
        template = random.choice(normal_templates)
        service = random.choice(services)
        severity = random.choice(normal_severity)
        
        # Fill template with random ID
        if "{id}" in template:
            log_message = template.format(id=random.randint(1000, 9999))
        else:
            log_message = template
        
        # Format log entry
        log_entry = f"{current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} [{severity}] {service}: {log_message}"
        logs.append(log_entry)
        
        # Increment by 50ms for normal logs
        current_time += timedelta(milliseconds=50)
        
        if (i + 1) % 5000 == 0:
            print(f"  Generated {i + 1} recovery logs...")
    
    # Write all logs to file
    print(f"\nWriting {len(logs)} logs to final_demo.log...")
    with open("final_demo.log", "w") as f:
        for log in logs:
            f.write(log + "\n")
    
    print("\n" + "="*60)
    print("Dataset Generated Successfully!")
    print("="*60)
    print(f"Total logs: {len(logs)}")
    print(f"  Normal Phase: 30,000 logs (50ms intervals)")
    print(f"  Attack Phase: 2,000 logs (1ms intervals - DDoS)")
    print(f"  Recovery Phase: 18,000 logs (50ms intervals)")
    print(f"File: final_demo.log")
    print("="*60)


if __name__ == "__main__":
    generate_dataset()
