# Turing Interview Prep: Senior Software Engineer – Go 1.26+ (LLM Evaluation & Repository Validation)

**Updated for Go 1.26 (February 2026)** - Modern patterns, errgroup, new features

Complete preparation guide for Golang-focused interview and coding rounds using the latest Go 1.26 features and best practices.

## Role Overview

**Focus Areas:**
1. **Go/Golang Expertise** - Modern concurrency patterns (errgroup), channels, interfaces, performance
2. **LLM Evaluation** - Metrics, benchmarking, quality assessment
3. **Repository Validation** - Code analysis, static checking, CI/CD
4. **System Design** - Scalable evaluation pipelines

---

## What's New in Go 1.26

### Key Features You Must Know

1. **new(expr)** - Allocate and initialize pointers inline
2. **Green Tea GC** - New garbage collector enabled by default (pacer-v3)
3. **Goroutine leak detector** - Built-in leak detection in tests
4. **New packages**: `crypto/hpke`, `crypto/mlkem/mlkemtest`, `testing/cryptotest`
5. **errors.Append()** - Alternative to errors.Join() for collecting errors
6. **Performance improvements** - 5-15% faster compilation, reduced memory usage

---

## Go 1.26 Modern Concurrency Patterns

### 1. Structured Concurrency with errgroup (MODERN WAY)

**❌ OLD STYLE (Don't use anymore):**
```go
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        // work
    }(i)
}
wg.Wait()
```

**✅ MODERN GO 1.26 STYLE:**
```go
package main

import (
    "context"
    "fmt"
    "time"

    "golang.org/x/sync/errgroup"
)

// Modern concurrent LLM evaluation with errgroup
func EvaluateConcurrently(ctx context.Context, tasks []EvaluationTask) ([]EvaluationResult, error) {
    g, ctx := errgroup.WithContext(ctx)
    
    // Set concurrency limit (Go 1.20+ feature)
    g.SetLimit(10) // Max 10 concurrent goroutines
    
    results := make([]EvaluationResult, len(tasks))
    
    // Launch goroutines - errgroup handles all synchronization
    for i, task := range tasks {
        // Go 1.22+ automatically captures loop variables correctly
        g.Go(func() error {
            result, err := evaluateTask(ctx, task)
            if err != nil {
                return fmt.Errorf("task %d failed: %w", i, err)
            }
            results[i] = result
            return nil
        })
    }
    
    // Wait for all goroutines and collect first error
    if err := g.Wait(); err != nil {
        return nil, err
    }
    
    return results, nil
}

type EvaluationTask struct {
    ModelName string
    Prompt    string
    Response  string
}

type EvaluationResult struct {
    Task      EvaluationTask
    Score     float64
    Latency   time.Duration
    Timestamp time.Time
}

func evaluateTask(ctx context.Context, task EvaluationTask) (EvaluationResult, error) {
    start := time.Now()
    
    select {
    case <-ctx.Done():
        return EvaluationResult{}, ctx.Err()
    case <-time.After(100 * time.Millisecond): // Simulate work
        score := calculateScore(task.Response)
        return EvaluationResult{
            Task:      task,
            Score:     score,
            Latency:   time.Since(start),
            Timestamp: time.Now(),
        }, nil
    }
}

func calculateScore(response string) float64 {
    // Placeholder scoring logic
    return 0.85
}
```

### 2. Modern Worker Pool with errgroup

**✅ GO 1.26 PATTERN:**
```go
type WorkerPool struct {
    maxWorkers int
    semaphore  chan struct{}
}

func NewWorkerPool(maxWorkers int) *WorkerPool {
    return &WorkerPool{
        maxWorkers: maxWorkers,
        semaphore:  make(chan struct{}, maxWorkers),
    }
}

// Process tasks with bounded concurrency using errgroup
func (p *WorkerPool) Process(ctx context.Context, tasks []EvaluationTask) ([]EvaluationResult, error) {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(p.maxWorkers)
    
    results := make([]EvaluationResult, len(tasks))
    
    for i, task := range tasks {
        g.Go(func() error {
            result, err := evaluateTask(ctx, task)
            if err != nil {
                return err
            }
            results[i] = result
            return nil
        })
    }
    
    if err := g.Wait(); err != nil {
        return nil, err
    }
    
    return results, nil
}
```

### 3. Go 1.26 new(expr) Feature

**✅ NEW IN GO 1.26:**
```go
type Config struct {
    Timeout     *time.Duration
    MaxRetries  *int
    EnableCache *bool
}

// OLD WAY - verbose
func oldWay() Config {
    timeout := 30 * time.Second
    retries := 3
    cache := true
    
    return Config{
        Timeout:     &timeout,
        MaxRetries:  &retries,
        EnableCache: &cache,
    }
}

// NEW GO 1.26 WAY - clean and inline
func modernWay() Config {
    return Config{
        Timeout:     new(30 * time.Second),  // ✅ Direct expression!
        MaxRetries:  new(3),
        EnableCache: new(true),
    }
}
```

### 4. Error Collection with errors.Append (Go 1.26)

**✅ GO 1.26 PATTERN:**
```go
import (
    "errors"
    "fmt"
)

// Collect multiple errors without stopping
func ValidateModels(models []string) error {
    var errs error
    
    for _, model := range models {
        if err := validateModel(model); err != nil {
            errs = errors.Append(errs, fmt.Errorf("model %s: %w", model, err))
        }
    }
    
    return errs
}

func validateModel(model string) error {
    if model == "" {
        return errors.New("empty model name")
    }
    return nil
}

// Alternative: errors.Join for slice of errors
func ValidateWithJoin(models []string) error {
    errs := make([]error, 0)
    
    for _, model := range models {
        if err := validateModel(model); err != nil {
            errs = append(errs, fmt.Errorf("model %s: %w", model, err))
        }
    }
    
    return errors.Join(errs...)
}
```

### 5. Context-Aware Pipeline Pattern

**✅ MODERN PIPELINE:**
```go
// Modern pipeline with context and errgroup
func EvaluationPipeline(ctx context.Context, tasks []EvaluationTask) (<-chan EvaluationResult, error) {
    g, ctx := errgroup.WithContext(ctx)
    
    // Stage 1: Generate tasks
    taskCh := make(chan EvaluationTask, len(tasks))
    g.Go(func() error {
        defer close(taskCh)
        for _, task := range tasks {
            select {
            case <-ctx.Done():
                return ctx.Err()
            case taskCh <- task:
            }
        }
        return nil
    })
    
    // Stage 2: Evaluate (with concurrency limit)
    resultCh := make(chan EvaluationResult, 10)
    g.SetLimit(5) // Max 5 concurrent evaluations
    
    for i := 0; i < 5; i++ {
        g.Go(func() error {
            for task := range taskCh {
                result, err := evaluateTask(ctx, task)
                if err != nil {
                    return err
                }
                select {
                case <-ctx.Done():
                    return ctx.Err()
                case resultCh <- result:
                }
            }
            return nil
        })
    }
    
    // Close results channel when all workers done
    go func() {
        _ = g.Wait()
        close(resultCh)
    }()
    
    return resultCh, nil
}
```

---

## Modern Interface Patterns (Go 1.26)

### 1. Generic Evaluator Interface

**✅ USING GENERICS (Go 1.18+):**
```go
// Generic evaluator for any metric type
type Evaluator[T any] interface {
    Evaluate(ctx context.Context, response, reference string) (T, error)
    Name() string
}

// Float64 score evaluator
type BLEUEvaluator struct {
    NGram int
}

func (b *BLEUEvaluator) Evaluate(ctx context.Context, response, reference string) (float64, error) {
    score := calculateBLEUScore(response, reference, b.NGram)
    return score, nil
}

func (b *BLEUEvaluator) Name() string {
    return fmt.Sprintf("BLEU-%d", b.NGram)
}

// Structured score evaluator
type DetailedScore struct {
    Overall   float64
    Precision float64
    Recall    float64
    F1        float64
}

type ROUGEEvaluator struct {
    Variant string
}

func (r *ROUGEEvaluator) Evaluate(ctx context.Context, response, reference string) (DetailedScore, error) {
    // Calculate detailed metrics
    return DetailedScore{
        Overall:   0.85,
        Precision: 0.90,
        Recall:    0.80,
        F1:        0.85,
    }, nil
}

func (r *ROUGEEvaluator) Name() string {
    return fmt.Sprintf("ROUGE-%s", r.Variant)
}

// Generic evaluation function
func RunEvaluation[T any](ctx context.Context, eval Evaluator[T], response, reference string) (T, error) {
    return eval.Evaluate(ctx, response, reference)
}

func calculateBLEUScore(response, reference string, ngram int) float64 {
    // Simplified BLEU calculation
    return 0.75
}
```

### 2. Functional Options Pattern (Modern Configuration)

**✅ GO 1.26 STYLE:**
```go
type EvaluationConfig struct {
    timeout     *time.Duration
    maxRetries  *int
    concurrency *int
    cacheEnabled *bool
}

type EvaluationOption func(*EvaluationConfig)

func WithTimeout(d time.Duration) EvaluationOption {
    return func(c *EvaluationConfig) {
        c.timeout = new(d) // Go 1.26 new(expr)
    }
}

func WithMaxRetries(n int) EvaluationOption {
    return func(c *EvaluationConfig) {
        c.maxRetries = new(n)
    }
}

func WithConcurrency(n int) EvaluationOption {
    return func(c *EvaluationConfig) {
        c.concurrency = new(n)
    }
}

func WithCache(enabled bool) EvaluationOption {
    return func(c *EvaluationConfig) {
        c.cacheEnabled = new(enabled)
    }
}

// Create evaluator with functional options
func NewEvaluator(opts ...EvaluationOption) *Evaluator {
    cfg := &EvaluationConfig{
        timeout:     new(5 * time.Second),
        maxRetries:  new(3),
        concurrency: new(10),
        cacheEnabled: new(false),
    }
    
    for _, opt := range opts {
        opt(cfg)
    }
    
    return &Evaluator{config: cfg}
}

type Evaluator struct {
    config *EvaluationConfig
}

// Usage
func main() {
    eval := NewEvaluator(
        WithTimeout(10 * time.Second),
        WithConcurrency(20),
        WithCache(true),
    )
    _ = eval
}
```

---

## Modern Error Handling (Go 1.26)

### 1. Structured Error Types with errors.Join/Append

**✅ GO 1.26 PATTERN:**
```go
import (
    "errors"
    "fmt"
)

// Custom error types
var (
    ErrInvalidScore  = errors.New("invalid score range")
    ErrEmptyResponse = errors.New("empty response")
    ErrTimeout       = errors.New("evaluation timeout")
    ErrModelNotFound = errors.New("model not found")
)

// Structured error with context
type EvaluationError struct {
    Task      EvaluationTask
    ModelName string
    Err       error
    Timestamp time.Time
}

func (e *EvaluationError) Error() string {
    return fmt.Sprintf("[%s] model %s: %v", 
        e.Timestamp.Format(time.RFC3339), e.ModelName, e.Err)
}

func (e *EvaluationError) Unwrap() error {
    return e.Err
}

// Modern error handling with defer and recover
func SafeEvaluate(ctx context.Context, task EvaluationTask) (result EvaluationResult, err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("panic during evaluation: %v", r)
        }
    }()
    
    if task.Response == "" {
        return EvaluationResult{}, fmt.Errorf("%w: task %s", ErrEmptyResponse, task.ModelName)
    }
    
    score := calculateScore(task.Response)
    
    if score < 0 || score > 1 {
        return EvaluationResult{}, fmt.Errorf("%w: got %f", ErrInvalidScore, score)
    }
    
    return EvaluationResult{
        Task:      task,
        Score:     score,
        Timestamp: time.Now(),
    }, nil
}

// Batch evaluation with error collection
func BatchEvaluate(ctx context.Context, tasks []EvaluationTask) ([]EvaluationResult, error) {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10)
    
    results := make([]EvaluationResult, len(tasks))
    var errs error
    var mu sync.Mutex
    
    for i, task := range tasks {
        g.Go(func() error {
            result, err := SafeEvaluate(ctx, task)
            if err != nil {
                mu.Lock()
                errs = errors.Append(errs, err) // Go 1.26 errors.Append
                mu.Unlock()
                return nil // Continue processing other tasks
            }
            results[i] = result
            return nil
        })
    }
    
    if err := g.Wait(); err != nil {
        return nil, err
    }
    
    return results, errs
}
```

---

## LLM Evaluation Implementation (Go 1.26)

### Modern BLEU Score with Generics

**✅ GO 1.26 IMPLEMENTATION:**
```go
package evaluation

import (
    "context"
    "math"
    "strings"
    "sync"
)

// Generic n-gram type
type NGram[T comparable] struct {
    tokens []T
}

// NGramCounter using generics
func NGramCounter[T comparable](tokens []T, n int) map[string]int {
    ngrams := make(map[string]int)
    
    for i := 0; i <= len(tokens)-n; i++ {
        key := strings.Join(toStrings(tokens[i:i+n]), " ")
        ngrams[key]++
    }
    
    return ngrams
}

func toStrings[T any](slice []T) []string {
    result := make([]string, len(slice))
    for i, v := range slice {
        result[i] = fmt.Sprint(v)
    }
    return result
}

// Modern BLEU implementation
type BLEUMetric struct {
    maxN      int
    smoothing bool
    weights   []float64
}

func NewBLEU(maxN int) *BLEUMetric {
    weights := make([]float64, maxN)
    for i := range weights {
        weights[i] = 1.0 / float64(maxN)
    }
    
    return &BLEUMetric{
        maxN:      maxN,
        smoothing: true,
        weights:   weights,
    }
}

func (b *BLEUMetric) Calculate(ctx context.Context, candidate, reference string) (float64, error) {
    candTokens := tokenize(candidate)
    refTokens := tokenize(reference)
    
    if len(candTokens) == 0 {
        return 0, nil
    }
    
    // Brevity penalty
    bp := b.brevityPenalty(len(candTokens), len(refTokens))
    
    // Calculate n-gram precisions concurrently
    precisions := make([]float64, b.maxN)
    g, ctx := errgroup.WithContext(ctx)
    
    for n := 1; n <= b.maxN; n++ {
        g.Go(func() error {
            p := b.ngramPrecision(candTokens, refTokens, n)
            precisions[n-1] = p
            return nil
        })
    }
    
    if err := g.Wait(); err != nil {
        return 0, err
    }
    
    // Geometric mean with smoothing
    geoMean := b.geometricMean(precisions)
    
    return bp * geoMean, nil
}

func (b *BLEUMetric) brevityPenalty(candLen, refLen int) float64 {
    if candLen >= refLen {
        return 1.0
    }
    return math.Exp(1 - float64(refLen)/float64(candLen))
}

func (b *BLEUMetric) ngramPrecision(candTokens, refTokens []string, n int) float64 {
    candNgrams := NGramCounter(candTokens, n)
    refNgrams := NGramCounter(refTokens, n)
    
    matches := 0
    total := 0
    
    for ngram, count := range candNgrams {
        total += count
        if refCount, exists := refNgrams[ngram]; exists {
            matches += min(count, refCount)
        }
    }
    
    if total == 0 {
        return 0
    }
    
    precision := float64(matches) / float64(total)
    
    // Add-k smoothing for zero precision
    if b.smoothing && precision == 0 {
        precision = 1.0 / float64(total+1)
    }
    
    return precision
}

func (b *BLEUMetric) geometricMean(precisions []float64) float64 {
    // Check for zero precision
    for _, p := range precisions {
        if p == 0 {
            return 0
        }
    }
    
    logSum := 0.0
    for i, p := range precisions {
        logSum += b.weights[i] * math.Log(p)
    }
    
    return math.Exp(logSum)
}

func tokenize(text string) []string {
    return strings.Fields(strings.ToLower(text))
}

func min(a, b int) int {
    return minInt(a, b)
}

func minInt(a, b int) int {
    if a < b {
        return a
    }
    return b
}
```

### Batch BLEU Evaluation with sync.Pool

**✅ MEMORY OPTIMIZATION:**
```go
var tokenPool = sync.Pool{
    New: func() interface{} {
        return make([]string, 0, 100)
    },
}

func BatchBLEU(ctx context.Context, pairs []struct{ Cand, Ref string }) ([]float64, error) {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(runtime.NumCPU())
    
    scores := make([]float64, len(pairs))
    metric := NewBLEU(4)
    
    for i, pair := range pairs {
        g.Go(func() error {
            // Get tokens from pool
            tokens := tokenPool.Get().([]string)
            defer func() {
                tokens = tokens[:0]
                tokenPool.Put(tokens)
            }()
            
            score, err := metric.Calculate(ctx, pair.Cand, pair.Ref)
            if err != nil {
                return err
            }
            scores[i] = score
            return nil
        })
    }
    
    if err := g.Wait(); err != nil {
        return nil, err
    }
    
    return scores, nil
}
```

---

## Repository Validation (Go 1.26)

### Modern AST Analysis with Generics

**✅ GO 1.26 ANALYZER:**
```go
package validator

import (
    "context"
    "fmt"
    "go/ast"
    "go/parser"
    "go/token"
    "os"
    "path/filepath"
    
    "golang.org/x/sync/errgroup"
)

type ValidationResult struct {
    FilePath   string
    Errors     []string
    Warnings   []string
    Complexity int
}

type FunctionInfo struct {
    Name       string
    File       string
    Complexity int
    Exported   bool
    HasDoc     bool
    Lines      int
    Receiver   string
}

type RepositoryValidator struct {
    rootPath string
    results  []ValidationResult
    mu       sync.RWMutex
}

func NewValidator(rootPath string) *RepositoryValidator {
    return &RepositoryValidator{
        rootPath: rootPath,
        results:  make([]ValidationResult, 0),
    }
}

// Modern concurrent validation
func (v *RepositoryValidator) Validate(ctx context.Context) error {
    files, err := v.findGoFiles(ctx)
    if err != nil {
        return err
    }
    
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(runtime.NumCPU())
    
    for _, file := range files {
        g.Go(func() error {
            return v.validateFile(ctx, file)
        })
    }
    
    return g.Wait()
}

func (v *RepositoryValidator) findGoFiles(ctx context.Context) ([]string, error) {
    var files []string
    
    err := filepath.WalkDir(v.rootPath, func(path string, d os.DirEntry, err error) error {
        if err != nil {
            return err
        }
        
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
        }
        
        // Skip vendor, .git, etc.
        if d.IsDir() {
            name := d.Name()
            if name == "vendor" || name == ".git" || name == "node_modules" {
                return filepath.SkipDir
            }
            return nil
        }
        
        if strings.HasSuffix(path, ".go") && !strings.HasSuffix(path, "_test.go") {
            files = append(files, path)
        }
        
        return nil
    })
    
    return files, err
}

func (v *RepositoryValidator) validateFile(ctx context.Context, path string) error {
    fset := token.NewFileSet()
    
    file, err := parser.ParseFile(fset, path, nil, parser.ParseComments)
    if err != nil {
        v.addResult(ValidationResult{
            FilePath: path,
            Errors:   []string{fmt.Sprintf("parse error: %v", err)},
        })
        return nil // Continue with other files
    }
    
    result := ValidationResult{
        FilePath: path,
        Errors:   make([]string, 0),
        Warnings: make([]string, 0),
    }
    
    // Analyze AST
    ast.Inspect(file, func(n ast.Node) bool {
        select {
        case <-ctx.Done():
            return false
        default:
        }
        
        switch node := n.(type) {
        case *ast.FuncDecl:
            v.analyzeFunction(node, fset, &result)
        case *ast.GenDecl:
            v.analyzeDeclaration(node, &result)
        }
        
        return true
    })
    
    v.addResult(result)
    return nil
}

func (v *RepositoryValidator) analyzeFunction(fn *ast.FuncDecl, fset *token.FileSet, result *ValidationResult) {
    // Check exported functions have documentation
    if fn.Name.IsExported() && fn.Doc == nil {
        result.Warnings = append(result.Warnings, 
            fmt.Sprintf("exported function %s lacks documentation", fn.Name.Name))
    }
    
    // Calculate cyclomatic complexity
    complexity := v.calculateComplexity(fn.Body)
    if complexity > 15 {
        result.Warnings = append(result.Warnings,
            fmt.Sprintf("function %s has high complexity: %d", fn.Name.Name, complexity))
    }
    
    result.Complexity += complexity
}

func (v *RepositoryValidator) calculateComplexity(body *ast.BlockStmt) int {
    if body == nil {
        return 0
    }
    
    complexity := 1 // Base complexity
    
    ast.Inspect(body, func(n ast.Node) bool {
        switch node := n.(type) {
        case *ast.IfStmt:
            complexity++
        case *ast.ForStmt, *ast.RangeStmt:
            complexity++
        case *ast.SwitchStmt, *ast.TypeSwitchStmt:
            complexity++
        case *ast.SelectStmt:
            complexity++
        case *ast.CaseClause:
            if len(node.List) > 0 { // Not default case
                complexity++
            }
        case *ast.BinaryExpr:
            if node.Op == token.LAND || node.Op == token.LOR {
                complexity++
            }
        }
        return true
    })
    
    return complexity
}

func (v *RepositoryValidator) analyzeDeclaration(decl *ast.GenDecl, result *ValidationResult) {
    // Check for exported types without documentation
    if decl.Tok == token.TYPE {
        for _, spec := range decl.Specs {
            if typeSpec, ok := spec.(*ast.TypeSpec); ok {
                if typeSpec.Name.IsExported() && decl.Doc == nil {
                    result.Warnings = append(result.Warnings,
                        fmt.Sprintf("exported type %s lacks documentation", typeSpec.Name.Name))
                }
            }
        }
    }
}

func (v *RepositoryValidator) addResult(result ValidationResult) {
    v.mu.Lock()
    defer v.mu.Unlock()
    v.results = append(v.results, result)
}

func (v *RepositoryValidator) GetResults() []ValidationResult {
    v.mu.RLock()
    defer v.mu.RUnlock()
    
    results := make([]ValidationResult, len(v.results))
    copy(results, v.results)
    return results
}

// Generate comprehensive report
func (v *RepositoryValidator) GenerateReport() string {
    results := v.GetResults()
    
    var report strings.Builder
    report.WriteString("=== Repository Validation Report ===\n\n")
    
    totalErrors := 0
    totalWarnings := 0
    totalComplexity := 0
    
    for _, result := range results {
        totalComplexity += result.Complexity
        
        if len(result.Errors) > 0 || len(result.Warnings) > 0 {
            report.WriteString(fmt.Sprintf("File: %s (complexity: %d)\n", result.FilePath, result.Complexity))
            
            for _, err := range result.Errors {
                report.WriteString(fmt.Sprintf("  ❌ ERROR: %s\n", err))
                totalErrors++
            }
            
            for _, warn := range result.Warnings {
                report.WriteString(fmt.Sprintf("  ⚠️  WARN: %s\n", warn))
                totalWarnings++
            }
            
            report.WriteString("\n")
        }
    }
    
    report.WriteString(fmt.Sprintf("Summary:\n"))
    report.WriteString(fmt.Sprintf("  Files Analyzed: %d\n", len(results)))
    report.WriteString(fmt.Sprintf("  Total Errors: %d\n", totalErrors))
    report.WriteString(fmt.Sprintf("  Total Warnings: %d\n", totalWarnings))
    report.WriteString(fmt.Sprintf("  Total Complexity: %d\n", totalComplexity))
    
    return report.String()
}
```

---

## Go 1.26 Interview Questions

### New Features

**Q1: What is new(expr) in Go 1.26?**

**Answer:** In Go 1.26, `new()` can now accept expressions, not just types. This allows inline pointer creation with initialization:

```go
// Before Go 1.26
timeout := 30 * time.Second
config := Config{Timeout: &timeout}

// Go 1.26+
config := Config{Timeout: new(30 * time.Second)}
```

**Q2: What is the Green Tea garbage collector?**

**Answer:** Green Tea (pacer-v3) is the new GC in Go 1.26 that provides:
- Better latency characteristics (reduced pause times)
- Improved memory utilization
- Smarter heap size prediction
- 5-10% performance improvement in GC-heavy workloads

**Q3: How does Go 1.26 detect goroutine leaks?**

**Answer:** Go 1.26 has built-in leak detection in tests:
```go
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m) // Detects leaked goroutines
}
```

### Modern Concurrency

**Q4: Why use errgroup instead of sync.WaitGroup?**

**Answer:**
- **Error handling**: errgroup collects and returns the first error
- **Context propagation**: Automatic cancellation on first error
- **Concurrency limiting**: Built-in `SetLimit()` method
- **Cleaner code**: No manual `Add()` and `Done()` calls

```go
// errgroup - Modern
g, ctx := errgroup.WithContext(ctx)
g.SetLimit(10)
for _, task := range tasks {
    g.Go(func() error {
        return process(ctx, task)
    })
}
return g.Wait()
```

**Q5: What's the difference between errors.Join and errors.Append?**

**Answer:**
- `errors.Join(errs...)`: Takes slice of errors, creates new multi-error
- `errors.Append(err1, err2)`: Appends to existing error, more efficient for building error chains

```go
// errors.Join - for slice of errors
var errs []error
errs = append(errs, err1, err2, err3)
return errors.Join(errs...)

// errors.Append - for incremental building
var errs error
errs = errors.Append(errs, err1)
errs = errors.Append(errs, err2)
return errs
```

### Performance

**Q6: How do you use sync.Pool correctly in Go 1.26?**

**Answer:**
```go
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func processData(data []byte) {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset() // Important: reset before returning
        bufferPool.Put(buf)
    }()
    
    // Use buf
    buf.Write(data)
}
```

**Q7: What tools are available for profiling in Go 1.26?**

**Answer:**
- `pprof`: CPU, memory, goroutine, block, mutex profiling
- `trace`: Execution tracer for detailed timeline analysis
- `go test -bench -benchmem`: Benchmark with memory stats
- `go build -gcflags="-m"`: Escape analysis

```bash
# CPU profiling
go test -cpuprofile=cpu.prof -bench=.
go tool pprof cpu.prof

# Memory profiling
go test -memprofile=mem.prof -bench=.
go tool pprof mem.prof

# Trace
go test -trace=trace.out
go tool trace trace.out
```

---

## Coding Problems (Go 1.26 Style)

### Problem 1: Concurrent LLM Batch Evaluator

**Requirements:**
- Evaluate 1000 prompts across 5 models
- Max 10 concurrent evaluations
- 5-second timeout per evaluation
- Collect all errors without stopping
- Return aggregated results

**✅ GO 1.26 SOLUTION:**
```go
package main

import (
    "context"
    "errors"
    "fmt"
    "sync"
    "time"
    
    "golang.org/x/sync/errgroup"
)

type Prompt struct {
    ID   int
    Text string
}

type Evaluation struct {
    PromptID int
    Model    string
    Score    float64
    Duration time.Duration
    Error    error
}

type BatchEvaluator struct {
    maxWorkers int
    timeout    time.Duration
    models     []string
}

func NewBatchEvaluator(maxWorkers int, timeout time.Duration, models []string) *BatchEvaluator {
    return &BatchEvaluator{
        maxWorkers: maxWorkers,
        timeout:    timeout,
        models:     models,
    }
}

func (b *BatchEvaluator) EvaluateBatch(ctx context.Context, prompts []Prompt) ([]Evaluation, error) {
    totalTasks := len(prompts) * len(b.models)
    results := make([]Evaluation, 0, totalTasks)
    var mu sync.Mutex
    
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(b.maxWorkers)
    
    for _, prompt := range prompts {
        for _, model := range b.models {
            g.Go(func() error {
                eval := b.evaluateOne(ctx, prompt, model)
                
                mu.Lock()
                results = append(results, eval)
                mu.Unlock()
                
                return nil // Don't stop on individual failures
            })
        }
    }
    
    if err := g.Wait(); err != nil {
        return results, err
    }
    
    return results, nil
}

func (b *BatchEvaluator) evaluateOne(ctx context.Context, prompt Prompt, model string) Evaluation {
    ctx, cancel := context.WithTimeout(ctx, b.timeout)
    defer cancel()
    
    start := time.Now()
    resultCh := make(chan float64, 1)
    
    go func() {
        // Simulate LLM evaluation
        time.Sleep(time.Duration(50+prompt.ID%450) * time.Millisecond)
        score := float64(prompt.ID%100) / 100.0
        resultCh <- score
    }()
    
    select {
    case score := <-resultCh:
        return Evaluation{
            PromptID: prompt.ID,
            Model:    model,
            Score:    score,
            Duration: time.Since(start),
            Error:    nil,
        }
    case <-ctx.Done():
        return Evaluation{
            PromptID: prompt.ID,
            Model:    model,
            Error:    fmt.Errorf("timeout after %v: %w", b.timeout, ctx.Err()),
            Duration: time.Since(start),
        }
    }
}

// Aggregate results by model
func AggregateResults(evaluations []Evaluation) map[string]ModelStats {
    stats := make(map[string]ModelStats)
    
    for _, eval := range evaluations {
        s := stats[eval.Model]
        s.Total++
        
        if eval.Error != nil {
            s.Errors++
        } else {
            s.ScoreSum += eval.Score
            s.SuccessCount++
            s.TotalDuration += eval.Duration
        }
        
        stats[eval.Model] = s
    }
    
    // Calculate averages
    for model, s := range stats {
        if s.SuccessCount > 0 {
            s.AvgScore = s.ScoreSum / float64(s.SuccessCount)
            s.AvgDuration = s.TotalDuration / time.Duration(s.SuccessCount)
        }
        stats[model] = s
    }
    
    return stats
}

type ModelStats struct {
    Total         int
    SuccessCount  int
    Errors        int
    ScoreSum      float64
    AvgScore      float64
    TotalDuration time.Duration
    AvgDuration   time.Duration
}

func main() {
    // Create 1000 prompts
    prompts := make([]Prompt, 1000)
    for i := range prompts {
        prompts[i] = Prompt{ID: i, Text: fmt.Sprintf("prompt_%d", i)}
    }
    
    // Create evaluator
    models := []string{"gpt-4", "claude-3", "gemini-pro", "llama-3", "mixtral"}
    evaluator := NewBatchEvaluator(10, 5*time.Second, models)
    
    // Run evaluation
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
    defer cancel()
    
    start := time.Now()
    results, err := evaluator.EvaluateBatch(ctx, prompts)
    duration := time.Since(start)
    
    if err != nil {
        fmt.Printf("Evaluation error: %v\n", err)
    }
    
    // Aggregate
    stats := AggregateResults(results)
    
    // Report
    fmt.Printf("\n=== Evaluation Results ===\n")
    fmt.Printf("Total Time: %v\n", duration)
    fmt.Printf("Total Evaluations: %d\n\n", len(results))
    
    for model, s := range stats {
        fmt.Printf("%s:\n", model)
        fmt.Printf("  Success: %d/%d (%.1f%%)\n", s.SuccessCount, s.Total, 
            float64(s.SuccessCount)/float64(s.Total)*100)
        fmt.Printf("  Avg Score: %.3f\n", s.AvgScore)
        fmt.Printf("  Avg Duration: %v\n", s.AvgDuration)
        fmt.Printf("  Errors: %d\n\n", s.Errors)
    }
}
```

### Problem 2: Generic Rate Limiter with Token Bucket

**✅ GO 1.26 WITH GENERICS:**
```go
package ratelimiter

import (
    "context"
    "time"
    
    "golang.org/x/time/rate"
)

// Generic rate limiter for any resource type
type RateLimiter[K comparable] struct {
    limiters map[K]*rate.Limiter
    mu       sync.RWMutex
    rate     rate.Limit
    burst    int
}

func NewRateLimiter[K comparable](r rate.Limit, burst int) *RateLimiter[K] {
    return &RateLimiter[K]{
        limiters: make(map[K]*rate.Limiter),
        rate:     r,
        burst:    burst,
    }
}

func (rl *RateLimiter[K]) getLimiter(key K) *rate.Limiter {
    rl.mu.RLock()
    limiter, exists := rl.limiters[key]
    rl.mu.RUnlock()
    
    if exists {
        return limiter
    }
    
    rl.mu.Lock()
    defer rl.mu.Unlock()
    
    // Double-check after acquiring write lock
    if limiter, exists := rl.limiters[key]; exists {
        return limiter
    }
    
    limiter = rate.NewLimiter(rl.rate, rl.burst)
    rl.limiters[key] = limiter
    return limiter
}

func (rl *RateLimiter[K]) Wait(ctx context.Context, key K) error {
    limiter := rl.getLimiter(key)
    return limiter.Wait(ctx)
}

func (rl *RateLimiter[K]) Allow(key K) bool {
    limiter := rl.getLimiter(key)
    return limiter.Allow()
}

// Usage with model names
func ExampleUsage() {
    // Per-model rate limiting
    limiter := NewRateLimiter[string](rate.Limit(10), 5) // 10 req/s, burst 5
    
    ctx := context.Background()
    
    // Wait for rate limit before API call
    if err := limiter.Wait(ctx, "gpt-4"); err != nil {
        fmt.Printf("Rate limit error: %v\n", err)
        return
    }
    
    // Make API call
    callModelAPI("gpt-4")
}

func callModelAPI(model string) {
    fmt.Printf("Calling %s API\n", model)
}
```

---

## Modern Testing Patterns (Go 1.26)

### Table-Driven Tests with Subtests

**✅ GO 1.26 PATTERN:**
```go
package evaluation

import (
    "context"
    "testing"
    "time"
)

func TestBLEUScore(t *testing.T) {
    tests := []struct {
        name      string
        candidate string
        reference string
        want      float64
        wantErr   bool
    }{
        {
            name:      "identical strings",
            candidate: "the cat sat on the mat",
            reference: "the cat sat on the mat",
            want:      1.0,
        },
        {
            name:      "completely different",
            candidate: "hello world",
            reference: "goodbye universe",
            want:      0.0,
        },
        {
            name:      "partial match",
            candidate: "the cat is on the mat",
            reference: "the cat sat on the mat",
            want:      0.75, // Approximate
        },
        {
            name:      "empty candidate",
            candidate: "",
            reference: "the cat sat on the mat",
            want:      0.0,
        },
    }
    
    metric := NewBLEU(4)
    ctx := context.Background()
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := metric.Calculate(ctx, tt.candidate, tt.reference)
            
            if (err != nil) != tt.wantErr {
                t.Errorf("Calculate() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            
            if !floatEqual(got, tt.want, 0.01) {
                t.Errorf("Calculate() = %v, want %v", got, tt.want)
            }
        })
    }
}

func floatEqual(a, b, epsilon float64) bool {
    return math.Abs(a-b) < epsilon
}

// Benchmark with Go 1.26 improvements
func BenchmarkBLEUScore(b *testing.B) {
    metric := NewBLEU(4)
    ctx := context.Background()
    
    benchmarks := []struct {
        name      string
        candidate string
        reference string
    }{
        {
            name:      "short",
            candidate: "the cat sat on the mat",
            reference: "the cat is on the mat",
        },
        {
            name:      "medium",
            candidate: strings.Repeat("the quick brown fox ", 10),
            reference: strings.Repeat("the quick brown fox ", 10),
        },
        {
            name:      "long",
            candidate: strings.Repeat("the quick brown fox jumps over lazy dog ", 100),
            reference: strings.Repeat("the quick brown fox jumps over lazy dog ", 100),
        },
    }
    
    for _, bm := range benchmarks {
        b.Run(bm.name, func(b *testing.B) {
            b.ReportAllocs()
            
            for i := 0; i < b.N; i++ {
                _, _ = metric.Calculate(ctx, bm.candidate, bm.reference)
            }
        })
    }
}

// Test with timeout
func TestEvaluationWithTimeout(t *testing.T) {
    ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
    defer cancel()
    
    task := EvaluationTask{
        ModelName: "slow-model",
        Prompt:    "test prompt",
        Response:  "test response",
    }
    
    // This should timeout
    _, err := evaluateTaskSlow(ctx, task)
    
    if !errors.Is(err, context.DeadlineExceeded) {
        t.Errorf("Expected timeout error, got %v", err)
    }
}

func evaluateTaskSlow(ctx context.Context, task EvaluationTask) (EvaluationResult, error) {
    select {
    case <-ctx.Done():
        return EvaluationResult{}, ctx.Err()
    case <-time.After(1 * time.Second):
        return EvaluationResult{}, nil
    }
}
```

### Testing with Goroutine Leak Detection

**✅ GO 1.26 FEATURE:**
```go
package evaluation

import (
    "testing"
    
    "go.uber.org/goleak"
)

func TestMain(m *testing.M) {
    // Automatically detect goroutine leaks
    goleak.VerifyTestMain(m,
        goleak.IgnoreTopFunction("internal/poll.runtime_pollWait"),
    )
}

func TestNoGoroutineLeak(t *testing.T) {
    defer goleak.VerifyNone(t)
    
    // Start goroutine with proper cleanup
    done := make(chan struct{})
    go func() {
        defer close(done)
        // Do work
    }()
    
    <-done // Wait for completion
}
```

---

## System Design (Go 1.26)

### Distributed LLM Evaluation Platform

**Modern Architecture:**

```
┌──────────────────┐
│   API Gateway    │ (Go + Gin)
│   Rate Limiting  │
└────────┬─────────┘
         │
┌────────▼──────────┐      ┌────────────────┐
│  Job Scheduler    │◄─────┤ Redis Streams  │
│  (errgroup based) │      │  (Job Queue)   │
└────────┬──────────┘      └────────────────┘
         │
┌────────▼────────────────────────┐
│   Worker Pool (Kubernetes)      │
│  ┌──────┐ ┌──────┐ ┌──────┐    │
│  │ Go   │ │ Go   │ │ Go   │    │
│  │Worker│ │Worker│ │Worker│    │
│  └───┬──┘ └───┬──┘ └───┬──┘    │
└──────┼────────┼────────┼────────┘
       │        │        │
┌──────▼────────▼────────▼───────┐
│   Results Store                │
│   PostgreSQL + TimescaleDB     │
│   (Time-series metrics)        │
└────────────────────────────────┘
```

**Modern Implementation:**

```go
package main

import (
    "context"
    "fmt"
    "time"
    
    "github.com/gin-gonic/gin"
    "github.com/redis/go-redis/v9"
    "golang.org/x/sync/errgroup"
)

// API Gateway with rate limiting
type APIGateway struct {
    redis       *redis.Client
    rateLimiter *RateLimiter[string]
}

func NewAPIGateway(redisAddr string) *APIGateway {
    return &APIGateway{
        redis:       redis.NewClient(&redis.Options{Addr: redisAddr}),
        rateLimiter: NewRateLimiter[string](rate.Limit(100), 10),
    }
}

type EvaluationRequest struct {
    Prompts  []string `json:"prompts" binding:"required"`
    Models   []string `json:"models" binding:"required"`
    Metrics  []string `json:"metrics"`
    Priority int      `json:"priority"`
}

type EvaluationResponse struct {
    JobID     string    `json:"job_id"`
    Status    string    `json:"status"`
    CreatedAt time.Time `json:"created_at"`
}

func (gw *APIGateway) SubmitJob(c *gin.Context) {
    // Rate limiting per user
    userID := c.GetHeader("X-User-ID")
    if err := gw.rateLimiter.Wait(c.Request.Context(), userID); err != nil {
        c.JSON(429, gin.H{"error": "rate limit exceeded"})
        return
    }
    
    var req EvaluationRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    
    // Create job
    jobID := generateJobID()
    job := Job{
        ID:        jobID,
        Prompts:   req.Prompts,
        Models:    req.Models,
        Metrics:   req.Metrics,
        Priority:  req.Priority,
        Status:    "queued",
        CreatedAt: time.Now(),
    }
    
    // Push to Redis Stream
    ctx := c.Request.Context()
    if err := gw.pushJob(ctx, job); err != nil {
        c.JSON(500, gin.H{"error": "failed to queue job"})
        return
    }
    
    c.JSON(202, EvaluationResponse{
        JobID:     jobID,
        Status:    "queued",
        CreatedAt: job.CreatedAt,
    })
}

type Job struct {
    ID        string
    Prompts   []string
    Models    []string
    Metrics   []string
    Priority  int
    Status    string
    CreatedAt time.Time
}

func (gw *APIGateway) pushJob(ctx context.Context, job Job) error {
    // Use Redis Streams for job queue
    data := map[string]interface{}{
        "id":         job.ID,
        "prompts":    strings.Join(job.Prompts, "|"),
        "models":     strings.Join(job.Models, "|"),
        "metrics":    strings.Join(job.Metrics, "|"),
        "priority":   job.Priority,
        "created_at": job.CreatedAt.Unix(),
    }
    
    _, err := gw.redis.XAdd(ctx, &redis.XAddArgs{
        Stream: "evaluation_jobs",
        Values: data,
    }).Result()
    
    return err
}

func generateJobID() string {
    return fmt.Sprintf("job_%d", time.Now().UnixNano())
}

// Worker with modern concurrency
type Worker struct {
    id          int
    redis       *redis.Client
    rateLimiter *RateLimiter[string]
    db          *Database
}

func (w *Worker) Start(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            if err := w.processNextJob(ctx); err != nil {
                time.Sleep(1 * time.Second)
            }
        }
    }
}

func (w *Worker) processNextJob(ctx context.Context) error {
    // Read from Redis Stream
    streams, err := w.redis.XReadGroup(ctx, &redis.XReadGroupArgs{
        Group:    "evaluation_workers",
        Consumer: fmt.Sprintf("worker_%d", w.id),
        Streams:  []string{"evaluation_jobs", ">"},
        Count:    1,
        Block:    5 * time.Second,
    }).Result()
    
    if err != nil || len(streams) == 0 {
        return err
    }
    
    msg := streams[0].Messages[0]
    job := w.parseJob(msg.Values)
    
    // Process with errgroup
    if err := w.evaluateJob(ctx, job); err != nil {
        return err
    }
    
    // Acknowledge message
    w.redis.XAck(ctx, "evaluation_jobs", "evaluation_workers", msg.ID)
    return nil
}

func (w *Worker) evaluateJob(ctx context.Context, job Job) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(5) // Max 5 concurrent evaluations per worker
    
    results := make([]EvaluationResult, 0)
    var mu sync.Mutex
    
    for _, prompt := range job.Prompts {
        for _, model := range job.Models {
            g.Go(func() error {
                // Rate limit per model
                if err := w.rateLimiter.Wait(ctx, model); err != nil {
                    return err
                }
                
                result, err := w.evaluate(ctx, prompt, model, job.Metrics)
                if err != nil {
                    return err
                }
                
                mu.Lock()
                results = append(results, result)
                mu.Unlock()
                
                return nil
            })
        }
    }
    
    if err := g.Wait(); err != nil {
        return err
    }
    
    // Store results
    return w.db.StoreResults(ctx, job.ID, results)
}

func (w *Worker) evaluate(ctx context.Context, prompt, model string, metrics []string) (EvaluationResult, error) {
    // Simulate evaluation
    time.Sleep(100 * time.Millisecond)
    return EvaluationResult{
        Score:     0.85,
        Timestamp: time.Now(),
    }, nil
}

func (w *Worker) parseJob(values map[string]interface{}) Job {
    return Job{
        ID:      values["id"].(string),
        Prompts: strings.Split(values["prompts"].(string), "|"),
        Models:  strings.Split(values["models"].(string), "|"),
        Metrics: strings.Split(values["metrics"].(string), "|"),
    }
}

type Database struct {
    // PostgreSQL connection
}

func (db *Database) StoreResults(ctx context.Context, jobID string, results []EvaluationResult) error {
    // Batch insert results
    return nil
}
```

---

## Best Practices Checklist (Go 1.26)

### ✅ Modern Concurrency
- [ ] Use `errgroup` instead of `sync.WaitGroup`
- [ ] Set concurrency limits with `g.SetLimit()`
- [ ] Always pass and respect `context.Context`
- [ ] Use goroutine leak detection in tests
- [ ] Implement proper cancellation

### ✅ Error Handling
- [ ] Use `errors.Append()` or `errors.Join()` for multiple errors
- [ ] Wrap errors with `fmt.Errorf("%w", err)`
- [ ] Check errors with `errors.Is()` and `errors.As()`
- [ ] Create sentinel errors as package variables
- [ ] Add context to errors

### ✅ Performance
- [ ] Use `sync.Pool` for frequently allocated objects
- [ ] Profile with pprof before optimizing
- [ ] Reduce allocations in hot paths
- [ ] Use buffered channels appropriately
- [ ] Benchmark with `-benchmem`

### ✅ Code Quality
- [ ] Run `golangci-lint` with strict rules
- [ ] Document all exported types and functions
- [ ] Keep cyclomatic complexity < 15
- [ ] Write table-driven tests
- [ ] Use meaningful variable names (Go 1.22+ loop var scoping)

### ✅ Modern Go Features
- [ ] Use `new(expr)` for inline pointer initialization
- [ ] Leverage generics for reusable code
- [ ] Use functional options pattern
- [ ] Implement structured logging
- [ ] Use type parameters where appropriate

---

## Resources

### Official Go 1.26 Documentation
- [Go 1.26 Release Notes](https://go.dev/doc/go1.26)
- [Go Blog](https://go.dev/blog/)
- [Effective Go](https://go.dev/doc/effective_go)

### Modern Patterns
- [errgroup documentation](https://pkg.go.dev/golang.org/x/sync/errgroup)
- [Context patterns](https://go.dev/blog/context)
- [Generics tutorial](https://go.dev/doc/tutorial/generics)

### Tools
- **golangci-lint**: https://golangci-lint.run/
- **pprof**: `go tool pprof`
- **goleak**: https://pkg.go.dev/go.uber.org/goleak
- **staticcheck**: https://staticcheck.io/

### Practice
- **LeetCode Go track**: Focus on concurrency
- **Exercism Go**: https://exercism.org/tracks/go
- **Go Playground**: https://go.dev/play/

---

## Study Plan (2 Weeks)

### Week 1: Modern Go 1.26 Features

**Days 1-2: errgroup & Modern Concurrency**
- Replace all WaitGroup code with errgroup
- Practice SetLimit() for bounded concurrency
- Build concurrent evaluation system
- Exercise: Convert old code to modern patterns

**Days 3-4: Go 1.26 New Features**
- Practice new(expr) syntax
- Learn Green Tea GC impact
- Use errors.Append() pattern
- Exercise: Refactor error handling

**Days 5-6: Generics & Modern Patterns**
- Build generic data structures
- Implement functional options
- Use type parameters effectively
- Exercise: Generic rate limiter

**Day 7: Performance & Profiling**
- Profile with pprof
- Optimize with sync.Pool
- Benchmark improvements
- Exercise: Optimize BLEU implementation

### Week 2: Advanced Topics & System Design

**Days 8-9: Repository Validation**
- Study go/ast package
- Build modern AST analyzers
- Implement complexity metrics
- Exercise: Build custom linter

**Days 10-11: System Design**
- Design distributed systems
- Modern microservices patterns
- Rate limiting strategies
- Exercise: Design evaluation platform

**Days 12-13: Testing & Quality**
- Goroutine leak detection
- Table-driven tests
- Benchmarking strategies
- Exercise: Comprehensive test suite

**Day 14: Final Review**
- Mock interviews
- Review all patterns
- System design practice
- Prepare questions

---

## Common Interview Pitfalls (Go 1.26)

### ❌ DON'T DO THIS:

```go
// 1. Using WaitGroup (old style)
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(n int) {
        defer wg.Done()
        // work
    }(i)
}
wg.Wait()

// 2. Ignoring context
func process(data []byte) error {
    // Missing context parameter
}

// 3. Not using new(expr)
timeout := 30 * time.Second
cfg := Config{Timeout: &timeout}

// 4. Ignoring errors
g.Go(func() error {
    process() // Not handling error
    return nil
})

// 5. Unbounded goroutines
for _, item := range items {
    go process(item) // No limit!
}
```

### ✅ DO THIS INSTEAD:

```go
// 1. Use errgroup (modern)
g, ctx := errgroup.WithContext(ctx)
g.SetLimit(10)
for i := 0; i < 10; i++ {
    g.Go(func() error {
        return process(ctx, i)
    })
}
return g.Wait()

// 2. Always use context
func process(ctx context.Context, data []byte) error {
    select {
    case <-ctx.Done():
        return ctx.Err()
    default:
        // work
    }
}

// 3. Use new(expr) in Go 1.26
cfg := Config{Timeout: new(30 * time.Second)}

// 4. Handle errors properly
g.Go(func() error {
    return process(ctx, data)
})

// 5. Bounded concurrency
g, ctx := errgroup.WithContext(ctx)
g.SetLimit(10)
for _, item := range items {
    g.Go(func() error {
        return process(ctx, item)
    })
}
```

---

## Final Tips

1. **Always use context** - Every function that does I/O should accept context.Context
2. **Prefer errgroup** - Stop using sync.WaitGroup for new code
3. **Think about cancellation** - What happens when context is cancelled?
4. **Profile before optimizing** - Don't guess, measure with pprof
5. **Write tests first** - Table-driven tests with subtests
6. **Use Go 1.26 features** - Show you know modern patterns
7. **Explain trade-offs** - Every design has pros and cons
8. **Ask clarifying questions** - Show you think about requirements
9. **Keep it simple** - Don't over-engineer
10. **Practice out loud** - Explain your thinking during coding

---

## Quick Reference Card

### errgroup Pattern
```go
g, ctx := errgroup.WithContext(ctx)
g.SetLimit(10)
for _, task := range tasks {
    g.Go(func() error { return process(ctx, task) })
}
return g.Wait()
```

### new(expr) Pattern
```go
cfg := Config{
    Timeout: new(30 * time.Second),
    Retries: new(3),
}
```

### Error Collection
```go
var errs error
errs = errors.Append(errs, err1)
errs = errors.Append(errs, err2)
return errs
```

### Rate Limiting
```go
limiter := rate.NewLimiter(rate.Limit(10), 5)
if err := limiter.Wait(ctx); err != nil {
    return err
}
```

### Context with Timeout
```go
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
```

---

**Good luck with your Turing interview! 🚀**

*Remember: Modern Go is about structured concurrency, proper error handling, and leveraging the type system. Show that you write idiomatic Go 1.26 code!*
