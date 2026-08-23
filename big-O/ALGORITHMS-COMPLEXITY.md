# Algorithms Time & Space Complexity

## Sorting Algorithms

| Algorithm | Best Time | Average Time | Worst Time | Space | Stable | Notes |
|-----------|-----------|--------------|------------|-------|--------|-------|
| **Bubble Sort** | O(n) | O(n²) | O(n²) | O(1) | ✓ | Good for nearly sorted data |
| **Selection Sort** | O(n²) | O(n²) | O(n²) | O(1) | ✗ | Always O(n²) comparisons |
| **Insertion Sort** | O(n) | O(n²) | O(n²) | O(1) | ✓ | Efficient for small/nearly sorted |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) | ✓ | Divide and conquer |
| **Quick Sort** | O(n log n) | O(n log n) | O(n²) | O(log n) | ✗ | Fast in practice, good pivot matters |
| **Heap Sort** | O(n log n) | O(n log n) | O(n log n) | O(1) | ✗ | In-place, not stable |
| **Counting Sort** | O(n + k) | O(n + k) | O(n + k) | O(k) | ✓ | k = range of input, for integers |
| **Radix Sort** | O(d(n + k)) | O(d(n + k)) | O(d(n + k)) | O(n + k) | ✓ | d = digits, k = base |
| **Bucket Sort** | O(n + k) | O(n + k) | O(n²) | O(n + k) | ✓ | Uniformly distributed input |
| **Tim Sort** | O(n) | O(n log n) | O(n log n) | O(n) | ✓ | Python/Java default |

## Searching Algorithms

| Algorithm | Time Complexity | Space | Prerequisites | Notes |
|-----------|----------------|-------|---------------|-------|
| **Linear Search** | O(n) | O(1) | None | Check each element |
| **Binary Search** | O(log n) | O(1) | Sorted array | Divide and conquer |
| **Binary Search (Recursive)** | O(log n) | O(log n) | Sorted array | Stack space for recursion |
| **Jump Search** | O(√n) | O(1) | Sorted array | Jump by √n steps |
| **Interpolation Search** | O(log log n) avg, O(n) worst | O(1) | Sorted, uniformly distributed | Like binary but estimates position |
| **Exponential Search** | O(log n) | O(1) | Sorted array | Finds range then binary search |
| **Ternary Search** | O(log₃ n) | O(1) | Sorted array | Divide into 3 parts |

## Graph Algorithms

| Algorithm | Time Complexity | Space | Notes |
|-----------|----------------|-------|-------|
| **BFS (Breadth-First Search)** | O(V + E) | O(V) | Queue-based, shortest path unweighted |
| **DFS (Depth-First Search)** | O(V + E) | O(V) | Stack-based, detect cycles |
| **Dijkstra's Algorithm** | O((V + E) log V) | O(V) | Shortest path, non-negative weights, min heap |
| **Dijkstra (Array)** | O(V²) | O(V) | Shortest path, dense graphs |
| **Bellman-Ford** | O(VE) | O(V) | Shortest path, handles negative weights |
| **Floyd-Warshall** | O(V³) | O(V²) | All pairs shortest path |
| **Prim's Algorithm** | O((V + E) log V) | O(V) | Minimum spanning tree, min heap |
| **Prim's (Array)** | O(V²) | O(V) | MST, dense graphs |
| **Kruskal's Algorithm** | O(E log E) | O(V) | MST, union-find |
| **Topological Sort (DFS)** | O(V + E) | O(V) | DAG only, stack-based |
| **Topological Sort (Kahn's)** | O(V + E) | O(V) | DAG only, BFS-based |
| **Tarjan's SCC** | O(V + E) | O(V) | Strongly connected components |
| **Kosaraju's SCC** | O(V + E) | O(V) | SCC, two DFS passes |
| **A* Search** | O(E) | O(V) | Shortest path with heuristic |
| **Floyd's Cycle Detection** | O(n) | O(1) | Detect cycle in linked list |

## Tree Algorithms

| Algorithm | Time Complexity | Space | Notes |
|-----------|----------------|-------|-------|
| **Tree Traversal (Inorder)** | O(n) | O(h) | h = height, recursive stack |
| **Tree Traversal (Preorder)** | O(n) | O(h) | Root → Left → Right |
| **Tree Traversal (Postorder)** | O(n) | O(h) | Left → Right → Root |
| **Level Order Traversal** | O(n) | O(w) | w = max width, BFS |
| **Binary Search (BST)** | O(log n) avg, O(n) worst | O(1) | Balanced BST is O(log n) |
| **BST Insertion** | O(log n) avg, O(n) worst | O(1) | Unbalanced can be O(n) |
| **BST Deletion** | O(log n) avg, O(n) worst | O(1) | Find successor/predecessor |
| **AVL Tree Operations** | O(log n) | O(1) | Self-balancing BST |
| **Red-Black Tree Operations** | O(log n) | O(1) | Self-balancing BST |
| **Heap Insert** | O(log n) | O(1) | Bubble up |
| **Heap Extract Min/Max** | O(log n) | O(1) | Bubble down |
| **Heapify** | O(n) | O(1) | Build heap from array |
| **Trie Insert/Search** | O(m) | O(m) | m = key length |
| **Segment Tree Build** | O(n) | O(n) | Range queries |
| **Segment Tree Query** | O(log n) | O(1) | Range sum/min/max |
| **Fenwick Tree (BIT) Update** | O(log n) | O(n) | Prefix sums |
| **Fenwick Tree Query** | O(log n) | O(1) | Cumulative frequency |

## Dynamic Programming Problems

| Problem | Time Complexity | Space | Pattern |
|---------|----------------|-------|---------|
| **Fibonacci (Recursive)** | O(2ⁿ) | O(n) | Exponential without memoization |
| **Fibonacci (Memoization)** | O(n) | O(n) | Top-down DP |
| **Fibonacci (Tabulation)** | O(n) | O(n) | Bottom-up DP |
| **Fibonacci (Optimized)** | O(n) | O(1) | Only store last 2 values |
| **0/1 Knapsack** | O(nW) | O(nW) | n items, W capacity |
| **Knapsack (Space Optimized)** | O(nW) | O(W) | 1D array |
| **Longest Common Subsequence** | O(mn) | O(mn) | m, n = string lengths |
| **LCS (Space Optimized)** | O(mn) | O(min(m,n)) | 1D array |
| **Longest Increasing Subsequence** | O(n²) | O(n) | DP solution |
| **LIS (Binary Search)** | O(n log n) | O(n) | Patience sorting |
| **Edit Distance** | O(mn) | O(mn) | Levenshtein distance |
| **Coin Change** | O(n × amount) | O(amount) | n = coins |
| **Matrix Chain Multiplication** | O(n³) | O(n²) | Optimal parenthesization |
| **Rod Cutting** | O(n²) | O(n) | Max profit |
| **Subset Sum** | O(n × sum) | O(n × sum) | NP-complete |
| **Palindrome Partitioning** | O(n²) | O(n²) | Min cuts |
| **Word Break** | O(n² × m) | O(n) | n = length, m = dict size |

## String Algorithms

| Algorithm | Time Complexity | Space | Notes |
|-----------|----------------|-------|-------|
| **Naive Pattern Matching** | O(nm) | O(1) | n = text, m = pattern |
| **KMP (Knuth-Morris-Pratt)** | O(n + m) | O(m) | Build LPS array |
| **Rabin-Karp** | O(n + m) avg, O(nm) worst | O(1) | Rolling hash |
| **Boyer-Moore** | O(n/m) best, O(nm) worst | O(m) | Skip characters |
| **Z Algorithm** | O(n + m) | O(n + m) | Pattern matching |
| **Aho-Corasick** | O(n + m + z) | O(m) | Multiple pattern matching, z = matches |
| **Manacher's Algorithm** | O(n) | O(n) | Longest palindromic substring |
| **Suffix Array** | O(n log n) | O(n) | Pattern matching, LCP |
| **Suffix Tree** | O(n) | O(n) | Ukkonen's algorithm |
| **Longest Palindrome (DP)** | O(n²) | O(n²) | Dynamic programming |
| **Longest Palindrome (Expand)** | O(n²) | O(1) | Expand around center |

## Array/List Algorithms

| Algorithm | Time Complexity | Space | Notes |
|-----------|----------------|-------|-------|
| **Two Pointers (Sorted)** | O(n) | O(1) | Two sum, container |
| **Sliding Window** | O(n) | O(k) | Max/min in window |
| **Kadane's Algorithm** | O(n) | O(1) | Max subarray sum |
| **Dutch National Flag** | O(n) | O(1) | 3-way partitioning |
| **Boyer-Moore Voting** | O(n) | O(1) | Majority element |
| **Quick Select** | O(n) avg, O(n²) worst | O(1) | Kth largest element |
| **Median of Medians** | O(n) | O(log n) | Guaranteed O(n) select |
| **Prefix Sum** | O(n) build, O(1) query | O(n) | Range sum queries |
| **Difference Array** | O(n) build, O(1) update | O(n) | Range updates |
| **Monotonic Stack** | O(n) | O(n) | Next greater element |
| **Monotonic Queue** | O(n) | O(k) | Sliding window max |

## Mathematical Algorithms

| Algorithm | Time Complexity | Space | Notes |
|-----------|----------------|-------|-------|
| **GCD (Euclidean)** | O(log min(a,b)) | O(1) | Greatest common divisor |
| **GCD (Recursive)** | O(log min(a,b)) | O(log min(a,b)) | Stack space |
| **LCM** | O(log min(a,b)) | O(1) | Uses GCD |
| **Prime Check (Trial Division)** | O(√n) | O(1) | Check divisibility |
| **Prime Check (Miller-Rabin)** | O(k log³ n) | O(1) | Probabilistic, k iterations |
| **Sieve of Eratosthenes** | O(n log log n) | O(n) | All primes up to n |
| **Segmented Sieve** | O(n log log n) | O(√n) | Primes in range |
| **Prime Factorization** | O(√n) | O(log n) | Trial division |
| **Modular Exponentiation** | O(log n) | O(1) | (a^b) % m |
| **Fast Exponentiation** | O(log n) | O(1) | a^b |
| **Matrix Exponentiation** | O(m³ log n) | O(m²) | m×m matrix to power n |
| **Fibonacci (Matrix)** | O(log n) | O(1) | Using matrix exponentiation |

## Backtracking Algorithms

| Algorithm | Time Complexity | Space | Notes |
|-----------|----------------|-------|-------|
| **N-Queens** | O(n!) | O(n²) | Place n queens |
| **Sudoku Solver** | O(9^(n×n)) | O(n²) | n = grid size (typically 9) |
| **Permutations** | O(n × n!) | O(n) | Generate all permutations |
| **Combinations** | O(2ⁿ) | O(n) | Generate all subsets |
| **Subset Sum** | O(2ⁿ) | O(n) | Find subset with sum |
| **Graph Coloring** | O(m^n) | O(n) | m colors, n vertices |
| **Hamiltonian Path** | O(n!) | O(n) | Visit all vertices once |
| **Word Search** | O(m × n × 4^L) | O(L) | m×n grid, L = word length |

## Greedy Algorithms

| Algorithm | Time Complexity | Space | Notes |
|-----------|----------------|-------|-------|
| **Activity Selection** | O(n log n) | O(1) | Sort by finish time |
| **Fractional Knapsack** | O(n log n) | O(1) | Sort by value/weight |
| **Huffman Coding** | O(n log n) | O(n) | Min heap for frequencies |
| **Job Sequencing** | O(n² log n) | O(n) | Maximize profit |
| **Interval Scheduling** | O(n log n) | O(1) | Non-overlapping intervals |

## Bit Manipulation

| Operation | Time Complexity | Space | Notes |
|-----------|----------------|-------|-------|
| **Count Set Bits** | O(log n) | O(1) | Brian Kernighan's algorithm |
| **Check Power of 2** | O(1) | O(1) | n & (n-1) == 0 |
| **Get/Set/Clear Bit** | O(1) | O(1) | Bit operations |
| **XOR All Elements** | O(n) | O(1) | Find unique element |
| **Generate Subsets** | O(2ⁿ) | O(1) | Use bitmask |

## Advanced Data Structures

| Data Structure | Insert | Delete | Search | Space | Notes |
|----------------|--------|--------|--------|-------|-------|
| **Hash Table** | O(1) avg | O(1) avg | O(1) avg | O(n) | Worst case O(n) with collisions |
| **Binary Search Tree** | O(log n) avg | O(log n) avg | O(log n) avg | O(n) | Worst O(n) if unbalanced |
| **AVL Tree** | O(log n) | O(log n) | O(log n) | O(n) | Self-balancing |
| **Red-Black Tree** | O(log n) | O(log n) | O(log n) | O(n) | Self-balancing |
| **B-Tree** | O(log n) | O(log n) | O(log n) | O(n) | Disk-based, multiple children |
| **Trie** | O(m) | O(m) | O(m) | O(ALPHABET × N × M) | m = key length |
| **Segment Tree** | O(n) build | - | O(log n) | O(n) | Range queries |
| **Fenwick Tree (BIT)** | O(log n) | - | O(log n) | O(n) | Prefix sums |
| **Disjoint Set (Union-Find)** | O(α(n)) | - | O(α(n)) | O(n) | α = inverse Ackermann |
| **Min/Max Heap** | O(log n) | O(log n) | O(1) peek | O(n) | Priority queue |
| **Skip List** | O(log n) avg | O(log n) avg | O(log n) avg | O(n) | Probabilistic balancing |
| **Bloom Filter** | O(k) | - | O(k) | O(m) | k = hash functions, probabilistic |

## Divide & Conquer

| Algorithm | Time Complexity | Space | Recurrence |
|-----------|----------------|-------|------------|
| **Binary Search** | O(log n) | O(1) | T(n) = T(n/2) + O(1) |
| **Merge Sort** | O(n log n) | O(n) | T(n) = 2T(n/2) + O(n) |
| **Quick Sort** | O(n log n) avg | O(log n) | T(n) = 2T(n/2) + O(n) |
| **Closest Pair of Points** | O(n log n) | O(n) | T(n) = 2T(n/2) + O(n) |
| **Strassen's Matrix Mult** | O(n^2.807) | O(n²) | T(n) = 7T(n/2) + O(n²) |
| **Karatsuba Multiplication** | O(n^1.585) | O(n log n) | T(n) = 3T(n/2) + O(n) |

## Two Pointers Patterns

| Pattern | Time Complexity | Space | Use Case |
|---------|----------------|-------|----------|
| **Opposite Direction** | O(n) | O(1) | Two sum sorted, palindrome |
| **Same Direction (Fast/Slow)** | O(n) | O(1) | Remove duplicates, cycle detection |
| **Sliding Window (Fixed)** | O(n) | O(1) | Max sum k elements |
| **Sliding Window (Variable)** | O(n) | O(k) | Longest substring |

## Master Theorem Quick Reference

For recurrence: T(n) = aT(n/b) + f(n)

| Case | Condition | Result |
|------|-----------|--------|
| 1 | f(n) = O(n^c), c < log_b(a) | T(n) = Θ(n^log_b(a)) |
| 2 | f(n) = Θ(n^c log^k n), c = log_b(a) | T(n) = Θ(n^c log^(k+1) n) |
| 3 | f(n) = Ω(n^c), c > log_b(a) | T(n) = Θ(f(n)) |

## Common Complexity Classes

| Class | Name | Example |
|-------|------|---------|
| O(1) | Constant | Hash table lookup |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Array traversal |
| O(n log n) | Linearithmic | Merge sort, quick sort |
| O(n²) | Quadratic | Bubble sort, nested loops |
| O(n³) | Cubic | Floyd-Warshall, matrix multiplication |
| O(2ⁿ) | Exponential | Recursive fibonacci, subsets |
| O(n!) | Factorial | Permutations, TSP brute force |
| O(n^n) | N to the N | Generating all passwords |
