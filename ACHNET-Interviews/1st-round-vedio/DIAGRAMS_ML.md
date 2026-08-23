# Machine Learning Visual Diagrams

## 1. Types of Machine Learning

```
                    Machine Learning
                           |
        ┌──────────────────┼──────────────────┐
        |                  |                  |
   Supervised         Unsupervised      Reinforcement
    Learning            Learning           Learning
        |                  |                  |
   ┌────┴────┐        ┌────┴────┐       ┌────┴────┐
   |         |        |         |       |         |
Regression  Class.  Clustering Association  Agent  Environment
   |         |        |         |           |         |
 [X→y]    [X→y]    [X→?]     [X→X]      [Action] [Reward]

Examples:
- Regression: House price prediction
- Classification: Email spam detection
- Clustering: Customer segmentation
- Association: Market basket analysis
- RL: Game playing, robotics
```

## 2. Supervised Learning Flow

```
Training Phase:
┌──────────────┐
│ Training     │
│ Data (X, y)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Algorithm   │  ← Choose: Linear, Tree, NN, SVM, etc.
│  Learning    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Trained    │
│    Model     │
└──────┬───────┘
       │
Testing Phase: │
       │
       ▼
┌──────────────┐
│  New Data    │
│    (X)       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Predictions  │
│    (ŷ)       │
└──────────────┘
```

## 3. Neural Network Architecture

```
Input Layer    Hidden Layers    Output Layer
    (3)          (4, 3)            (2)

x₁ ○────────●────────●────────○ ŷ₁
           /│\      /│\       │
x₂ ○──────/─┼─\────/─┼─\─────○ ŷ₂
         /  │  \  /  │  \
x₃ ○────●───●───●●───●───●
         \  │  /  \  │  /
          \ │ /    \ │ /
           \│/      \│/

Each connection has a weight (w)
Each neuron has a bias (b)

Neuron computation:
z = Σ(wᵢxᵢ) + b
a = activation(z)
```

## 4. Activation Functions

```
1. Sigmoid:           σ(x) = 1/(1 + e⁻ˣ)
   
   1 |        ╱────
     |      ╱
   0 |────╱
     └──────────── x
   
   Range: (0, 1)
   Use: Binary classification output

2. ReLU:              f(x) = max(0, x)
   
     |      ╱
     |    ╱
   0 |──╱─────── x
     |
   
   Range: [0, ∞)
   Use: Hidden layers (most popular)

3. Tanh:              tanh(x) = (eˣ - e⁻ˣ)/(eˣ + e⁻ˣ)
   
   1 |      ╱────
     |    ╱
   0 |──╱────── x
     |╱
  -1 |
   
   Range: (-1, 1)
   Use: Hidden layers

4. Softmax:           σ(xᵢ) = eˣⁱ/Σeˣʲ
   
   Converts logits to probabilities
   Σ probabilities = 1
   Use: Multi-class classification output
```

## 5. Backpropagation Flow

```
Forward Pass:
Input → Layer₁ → Layer₂ → ... → Output → Loss
  x       a₁       a₂              ŷ       L

Backward Pass (Gradients):
Loss → ∂L/∂W_out → ∂L/∂W₂ → ∂L/∂W₁ → ∂L/∂W_in
  L                                        
  ↓
Update Weights:
W_new = W_old - η × ∂L/∂W
        (η = learning rate)
```

## 6. Gradient Descent Types

```
1. Batch Gradient Descent:
   
   ┌─────────────────────┐
   │ All Training Data   │ → Compute Gradient → Update Weights
   │   (Entire Dataset)  │
   └─────────────────────┘
   
   Pros: Stable, converges to minimum
   Cons: Slow for large datasets

2. Stochastic Gradient Descent (SGD):
   
   ┌──────┐
   │ One  │ → Compute Gradient → Update Weights → Repeat
   │Sample│
   └──────┘
   
   Pros: Fast, online learning
   Cons: Noisy, oscillates

3. Mini-Batch Gradient Descent:
   
   ┌──────────────┐
   │ Mini-Batch   │ → Compute Gradient → Update Weights → Next Batch
   │ (32, 64, etc)│
   └──────────────┘
   
   Pros: Balance speed and stability
   Cons: Best practice (most used)
```

## 7. Bias-Variance Tradeoff

```
         Error
           │
           │    ╱────── Total Error
           │   ╱
           │  ╱  ╲
           │ ╱    ╲_____ Bias²
           │╱          
           │╲          ╱
           │ ╲        ╱ Variance
           │  ╲______╱
           │
           └──────────────► Model Complexity
         Simple      Optimal     Complex

Underfitting ←────────┼────────→ Overfitting
(High Bias)           │        (High Variance)

Training Error:  High           Low           Very Low
Testing Error:   High           Low           High
```

## 8. Train-Validation-Test Split

```
┌─────────────────────────────────────────────────┐
│              Full Dataset (100%)                │
└─────────────────────────────────────────────────┘
        ↓                ↓                 ↓
┌──────────────┐  ┌──────────┐    ┌─────────────┐
│  Training    │  │Validation│    │    Test     │
│    (70%)     │  │  (15%)   │    │   (15%)     │
└──────┬───────┘  └────┬─────┘    └──────┬──────┘
       │               │                  │
       │               │                  │
   Train Model    Tune Hyperparams    Final Eval
    (Learn)       (Select Model)     (Report Score)
```

## 9. Cross-Validation (K-Fold)

```
5-Fold Cross-Validation:

Iteration 1: [Test][Train][Train][Train][Train]
Iteration 2: [Train][Test][Train][Train][Train]
Iteration 3: [Train][Train][Test][Train][Train]
Iteration 4: [Train][Train][Train][Test][Train]
Iteration 5: [Train][Train][Train][Train][Test]
             ↓     ↓     ↓     ↓     ↓
           Score₁ Score₂ Score₃ Score₄ Score₅

Final Score = Average(Score₁, Score₂, ..., Score₅)

Reduces variance, better model evaluation
```

## 10. Confusion Matrix (Binary Classification)

```
                 Predicted
                 Neg   Pos
              ┌─────┬─────┐
Actual   Neg  │ TN  │ FP  │
              ├─────┼─────┤
         Pos  │ FN  │ TP  │
              └─────┴─────┘

TN = True Negative  (Correctly predicted negative)
FP = False Positive (Incorrectly predicted positive) - Type I Error
FN = False Negative (Incorrectly predicted negative) - Type II Error
TP = True Positive  (Correctly predicted positive)

Metrics:
Accuracy  = (TP + TN) / Total
Precision = TP / (TP + FP)  - "Of predicted positives, how many correct?"
Recall    = TP / (TP + FN)  - "Of actual positives, how many found?"
F1 Score  = 2 × (Precision × Recall) / (Precision + Recall)
```

## 11. ROC Curve

```
TPR
(Recall) 
  1 │       ●────●
    │      ╱      
    │     ╱   AUC = 0.9
  0.5│   ╱     (Good)
    │  ╱
    │ ╱  Random Classifier
    │╱   (AUC = 0.5)
  0 └──────────────── FPR
    0    0.5        1

TPR = True Positive Rate = TP/(TP+FN)
FPR = False Positive Rate = FP/(FP+TN)

AUC (Area Under Curve):
- 0.5 = Random guessing
- 0.7-0.8 = Acceptable
- 0.8-0.9 = Excellent
- 0.9-1.0 = Outstanding
```

## 12. Decision Tree Structure

```
                Root Node
              [Age <= 30?]
               /        \
            Yes          No
             ╱            ╲
     [Income <= 50K?]   [Credit >= 700?]
         /    \            /         \
      Yes      No        Yes          No
       │       │          │            │
    Deny    Approve    Approve       Deny
    (Leaf)  (Leaf)     (Leaf)       (Leaf)

Splits based on:
- Information Gain (ID3, C4.5)
- Gini Impurity (CART)
- Variance Reduction (Regression)
```

## 13. Random Forest Ensemble

```
Training Data
     │
     ├─── Bootstrap Sample 1 → Decision Tree 1 ──┐
     │                                             │
     ├─── Bootstrap Sample 2 → Decision Tree 2 ──┤
     │                                             ├→ Voting/Averaging → Final Prediction
     ├─── Bootstrap Sample 3 → Decision Tree 3 ──┤
     │                                             │
     └─── Bootstrap Sample N → Decision Tree N ──┘

Bagging (Bootstrap Aggregating) + Random Feature Selection
Reduces variance, prevents overfitting
```

## 14. Gradient Boosting

```
Step 1: Train weak learner f₁(x)
        Predictions: ŷ₁
        Residuals: r₁ = y - ŷ₁

Step 2: Train f₂(x) on residuals r₁
        Predictions: ŷ₂
        Residuals: r₂ = r₁ - ŷ₂

Step 3: Train f₃(x) on residuals r₂
        Predictions: ŷ₃
        ...

Final Model:
F(x) = f₁(x) + α·f₂(x) + α·f₃(x) + ... + α·fₙ(x)
       (α = learning rate)

Sequential learning, reduces bias
Examples: XGBoost, LightGBM, CatBoost
```

## 15. SVM (Support Vector Machine)

```
                    Maximum Margin
                         ←→
Class -1              │ │ │           Class +1
   ○                  │ │ │              ●
     ○                │ │ │            ●
       ○             ┌┼─┼─┼┐         ●
         ○          ││ │ │ ││       ●
   ○       ○        ││ │ │ ││     ●
     ○              ││ │ │ ││   ●     ●
       ○            │└─┼─┼─┘│ ●
         ○          │  │ │  │●         ●
           ○        │  │ │  │
                    │  │ │  │
            Support │  │ │  │Support
            Vectors │  │ │  │Vectors
                    │  │ │  │
             Margin │  │ │  │ Margin
           Boundary │  │ │  │Boundary
                       │ │
                       │ │
                  Decision
                  Boundary

Goal: Maximize margin between classes
Kernel Trick: Transform to higher dimensions for non-linear separation
```

## 16. K-Means Clustering

```
Iteration 1:          Iteration 2:          Converged:
Random Centroids      Update Centroids      Final Clusters

  ●   ○   ●            ●       ●              ●  ○○○  ●
 ○ ○ ○ ○ ○ ○          ○ ○   ○ ○             ○○  ●  ○○
○   ○   ○   ○        ○   ○ ○   ○           ○○   ●   ○○
  ○   ○   ○            ○   ●   ○              ○○●○○
   ○ ○ ○ ○              ○ ○ ○ ○                ●●●

Steps:
1. Initialize K centroids randomly
2. Assign each point to nearest centroid
3. Update centroids to mean of assigned points
4. Repeat 2-3 until convergence

Elbow Method to find optimal K:
WCSS
  │╲
  │ ╲___
  │     ─────
  └──────────► K
     ↑
   Elbow (optimal K)
```

## 17. PCA (Principal Component Analysis)

```
Original 2D Data:        After PCA:

    │  ●                     │
  y │ ●  ●                   │  ●●●●●
    │●    ●              PC2 │
    │  ●  ●                  │
    └────────── x            └────────── PC1
                             (maximum variance)

Steps:
1. Standardize data (mean=0, std=1)
2. Compute covariance matrix
3. Calculate eigenvectors & eigenvalues
4. Sort by eigenvalue (importance)
5. Project data onto top k eigenvectors

Reduces dimensions while preserving variance
```

## 18. Regularization Effect

```
No Regularization:           L2 Regularization (Ridge):
                            
    │  ●                        │  ●
  y │ ●╱─●                    y │ ●──●
    │●─╱   ●                    │●    ●
    │──╱───●                    │  ──●
    └────────── x               └────────── x
    Overfitting                 Smoother fit
    (High variance)             (Reduced variance)

Cost Function:
Loss = MSE + λ × Σ(weights²)
                  ↑
            Regularization term

λ (lambda) controls regularization strength:
- λ = 0: No regularization
- λ ↑: More regularization (simpler model)
```

## 19. Learning Curves

```
Good Fit:                    Overfitting:
Error                        Error
  │                            │
  │  Training ───────          │  Training ───────
  │        ─────               │
  │  Validation ─────          │  Validation
  │                            │         ─────────
  └──────────► Samples         └──────────► Samples

Both converge                  Large gap between curves
Low error                      Training error low, validation high

Underfitting:
Error
  │  Training ───────
  │        ─────────
  │  Validation 
  │         ─────────
  └──────────► Samples

Both high error
Curves converge at high error
```

## 20. CNN Architecture (Convolutional Neural Network)

```
Input Image          Conv          Pool         Conv          Pool        Flatten    FC         Output
(28x28x1)          (5x5x32)     (2x2)       (5x5x64)     (2x2)                     Layers
                                                                         
┌─────────┐       ┌────────┐   ┌──────┐    ┌────────┐   ┌──────┐    ┌──────┐   ┌───────┐   ┌────┐
│         │       │        │   │      │    │        │   │      │    │      │   │       │   │    │
│   28    │  →    │   24   │ → │  12  │ →  │    8   │ → │   4  │ →  │ 1024 │ → │  128  │ → │ 10 │
│         │       │        │   │      │    │        │   │      │    │      │   │       │   │    │
└─────────┘       └────────┘   └──────┘    └────────┘   └──────┘    └──────┘   └───────┘   └────┘
                                                                         
   Input          Feature Maps              Feature Maps              Vector     Dense    Classes
                  (Learn edges,             (Learn patterns)                    Layers
                   textures)

Conv: Applies filters to detect features
Pool: Reduces spatial dimensions (Max/Average pooling)
FC: Fully connected layers for classification
```

## 21. RNN vs LSTM

```
RNN (Recurrent Neural Network):

x₁ → [h₁] → x₂ → [h₂] → x₃ → [h₃] → ...
     ↓           ↓           ↓
     y₁          y₂          y₃

Problem: Vanishing gradient (can't learn long-term dependencies)

LSTM (Long Short-Term Memory):

x₁ → [LSTM Cell] → x₂ → [LSTM Cell] → x₃ → [LSTM Cell]
     │  ├─ Forget Gate                    ↓
     │  ├─ Input Gate                     y₃
     │  └─ Output Gate
     ↓
    Cell State (c₁) ───────→ (c₂) ───────→ (c₃)
    (Long-term memory)

Solves: Vanishing gradient via cell state
Use: Sequences (text, time-series, speech)
```

## 22. Attention Mechanism (Transformer)

```
Query: "What do I want to focus on?"
Key:   "What do I have?"
Value: "What is the actual content?"

Attention(Q, K, V) = softmax(QK^T / √d_k) × V

Example: "The cat sat on the mat"

When processing "sat":
Q = "sat"
K = ["The", "cat", "sat", "on", "the", "mat"]
Attention scores:
  The: 0.05  (low attention)
  cat: 0.70  (HIGH attention) ←
  sat: 0.10
  on:  0.05
  the: 0.05
  mat: 0.05

"sat" pays most attention to "cat" (subject of action)
```

## 23. Batch Normalization

```
Without Batch Norm:          With Batch Norm:

Layer outputs vary widely    Layer outputs normalized

Distribution at Layer 2:     Distribution at Layer 2:
  │   ●                         │
  │●   ●●●                      │    ●●●
  │ ●●●   ●                     │  ●●●●●●●
  └──────────                   └──────────
  Wide, shifting               Centered, stable

Benefits:
- Faster training
- Higher learning rates possible
- Reduces internal covariate shift
- Regularization effect
```

## 24. Dropout Regularization

```
Training (Dropout = 0.5):     Testing (No Dropout):

Input                         Input
  ○                             ○
  │                             │
 ╱│╲                           ╱│╲
●─×─●  (50% neurons dropped)  ●─●─●  (All neurons active)
│ │ │                         │ │ │
╲─┼─╱                         ╲─┼─╱
  ○                             ○
Output                        Output

Randomly drops neurons during training
Prevents co-adaptation
Reduces overfitting
```

## 25. Transfer Learning

```
Pre-trained Model (ImageNet):   Fine-tuned for Custom Task:

┌──────────────────┐             ┌──────────────────┐
│   Input Layer    │             │   Input Layer    │
├──────────────────┤             ├──────────────────┤
│   Conv Layers    │             │   Conv Layers    │ ← Frozen
│  (Feature Extractor) │ →       │  (Feature Extractor) │   (Don't train)
│   1000 classes   │             ├──────────────────┤
└──────────────────┘             │  New FC Layers   │ ← Train only
                                 │   10 classes     │   these layers
                                 └──────────────────┘

Benefits:
- Less training data needed
- Faster training
- Better performance on small datasets
```

This covers the major ML concepts with visual diagrams!
