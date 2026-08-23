# Generative AI - 50 Interview Questions with Answers

## Generative AI Fundamentals (Questions 1-10)

### Q1. What is Generative AI and how does it differ from traditional AI?
**Answer**: 

**Generative AI**: Creates new content (text, images, code, audio).

**Traditional AI**: Classifies, predicts, or analyzes existing data.

**Comparison**:
| Aspect | Traditional AI | Generative AI |
|--------|----------------|---------------|
| **Output** | Classification, prediction | New content creation |
| **Examples** | Spam detection, fraud detection | ChatGPT, DALL-E, Midjourney |
| **Training** | Supervised learning | Self-supervised, unsupervised |
| **Goal** | Pattern recognition | Pattern synthesis |

**Examples**:
- **Traditional**: "Is this email spam?" (Yes/No)
- **Generative**: "Write an email about..." (Creates email)

### Q2. Explain the difference between discriminative and generative models.
**Answer**: 

**Discriminative models**: Learn P(Y|X) - probability of Y given X
```
Input X → Model → Class Y
Example: Given image, classify as cat or dog
```

**Generative models**: Learn P(X|Y) or P(X) - distribution of data
```
Noise/Prompt → Model → Generate X
Example: Generate image of a cat
```

**Examples**:
- **Discriminative**: Logistic Regression, SVM, CNNs for classification
- **Generative**: GANs, VAEs, GPT, Diffusion models

**Mathematical**:
- Discriminative: Directly model decision boundary
- Generative: Model data distribution, can sample new examples

**When to use**:
- **Discriminative**: Classification tasks, often better performance
- **Generative**: Need to create new data, understand data distribution

### Q3. What are the main types of generative models?
**Answer**: 

**1. Autoregressive Models**:
- Generate sequentially, one element at a time
- Examples: GPT, PixelCNN
```
P(x) = P(x₁) × P(x₂|x₁) × P(x₃|x₁,x₂) × ...
```

**2. Variational Autoencoders (VAEs)**:
- Encode to latent space, decode to generate
- Continuous latent space
- Good for interpolation

**3. Generative Adversarial Networks (GANs)**:
- Generator vs Discriminator
- High-quality images
- Training instability

**4. Diffusion Models**:
- Add noise, then denoise
- State-of-the-art image generation
- Examples: DALL-E 2, Stable Diffusion, Midjourney

**5. Transformer-based**:
- Attention mechanism
- Examples: GPT, BERT, T5

**6. Flow-based models**:
- Invertible transformations
- Exact likelihood computation

### Q4. Explain how GPT (Generative Pre-trained Transformer) works.
**Answer**: 

**Architecture**: Decoder-only Transformer

**Training**:
1. **Pre-training**: Predict next token
```
Input: "The cat sat on the"
Target: "mat"
```
2. Trained on massive text corpus (internet, books)
3. Self-supervised learning

**Key components**:

**1. Tokenization**:
```
"Hello world" → [15496, 995]
```

**2. Embeddings**:
- Token embeddings
- Positional embeddings

**3. Transformer blocks**:
- Multi-head self-attention
- Feed-forward networks
- Layer normalization

**4. Generation**:
```
Prompt → Token probabilities → Sample → Repeat
```

**Versions**:
- GPT-1: 117M parameters
- GPT-2: 1.5B parameters
- GPT-3: 175B parameters
- GPT-4: Estimated 1.7T+ parameters (rumored)

**Capabilities**:
- Text generation
- Translation
- Summarization
- Question answering
- Code generation
- Few-shot learning

### Q5. What are Generative Adversarial Networks (GANs)?
**Answer**: 

**Architecture**: Two neural networks competing

**Components**:

**1. Generator (G)**:
- Creates fake data
- Input: Random noise (latent vector)
- Output: Synthetic data
```
z (noise) → Generator → Fake image
```

**2. Discriminator (D)**:
- Distinguishes real from fake
- Input: Real or fake data
- Output: Probability (real or fake)
```
Image → Discriminator → [0, 1]
```

**Training** (Minimax game):
```
min_G max_D V(D,G) = E[log D(x)] + E[log(1 - D(G(z)))]
```

**Process**:
1. Generator creates fake data
2. Discriminator evaluates real vs fake
3. Both networks improve iteratively
4. Generator gets better at fooling discriminator
5. Discriminator gets better at detecting fakes

**Types**:
- **DCGAN**: Deep Convolutional GAN
- **StyleGAN**: Style-based generator
- **CycleGAN**: Image-to-image translation
- **Pix2Pix**: Paired image translation

**Applications**:
- Image generation
- Style transfer
- Super-resolution
- Data augmentation

**Challenges**:
- Training instability
- Mode collapse
- Vanishing gradients

### Q6. Explain diffusion models.
**Answer**: 

**Concept**: Add noise gradually, then learn to denoise

**Process**:

**Forward (Diffusion)**:
```
x₀ (clean) → x₁ → x₂ → ... → xₜ (pure noise)
```
Add Gaussian noise at each step

**Reverse (Denoising)**:
```
xₜ (noise) → ... → x₁ → x₀ (clean image)
```
Neural network learns to remove noise

**Training**:
1. Take real image
2. Add random amount of noise
3. Train model to predict noise
4. Loss: MSE between predicted and actual noise

**Generation**:
1. Start with pure noise
2. Iteratively denoise
3. 1000+ steps typically
4. Guided by text prompt (CLIP)

**Types**:
- **DDPM**: Denoising Diffusion Probabilistic Models
- **DDIM**: Faster sampling
- **Latent Diffusion**: Work in latent space (Stable Diffusion)

**Models**:
- DALL-E 2
- Stable Diffusion
- Midjourney
- Imagen

**Advantages**:
- High-quality images
- Stable training
- Diverse outputs

**Disadvantages**:
- Slow generation (many steps)
- Computationally expensive

### Q7. What is a Variational Autoencoder (VAE)?
**Answer**: 

**Architecture**: Encoder → Latent space → Decoder

**Components**:

**1. Encoder**:
- Maps input to latent distribution
- Outputs: μ (mean), σ (std deviation)
```
x → Encoder → [μ, σ]
```

**2. Latent space**:
- Sample z ~ N(μ, σ)
- Reparameterization trick: z = μ + σ × ε

**3. Decoder**:
- Reconstructs input from latent
```
z → Decoder → x'
```

**Loss function**:
```
Loss = Reconstruction loss + KL divergence
     = ||x - x'||² + KL(q(z|x) || p(z))
```

**Training**:
- Minimize reconstruction error
- Keep latent distribution close to N(0,1)

**Generation**:
1. Sample z from N(0,1)
2. Pass through decoder
3. Get new data point

**Properties**:
- **Continuous latent space**: Can interpolate
- **Smooth transitions**: Between data points
- **Interpretable dimensions**: Sometimes

**Applications**:
- Image generation
- Data compression
- Anomaly detection
- Drug discovery

**vs GAN**:
- VAE: Blurrier but stable training
- GAN: Sharper but unstable

### Q8. What is prompt engineering?
**Answer**: 

**Definition**: Crafting inputs to get desired outputs from LLMs

**Techniques**:

**1. Zero-shot**:
```
"Translate to French: Hello world"
```

**2. Few-shot**:
```
"dog → animal
car → vehicle
apple → ?"
```

**3. Chain-of-thought**:
```
"Let's solve this step by step:
1. First...
2. Then...
3. Finally..."
```

**4. Role prompting**:
```
"You are an expert Python developer.
Write a function to..."
```

**5. Instruction clarity**:
```
Bad: "Write about dogs"
Good: "Write a 200-word article about dog training for puppies, including 3 specific techniques"
```

**6. Constraints**:
```
"Answer in exactly 3 sentences.
Use simple language suitable for a 10-year-old."
```

**7. Format specification**:
```
"Respond in JSON format:
{
  "answer": "...",
  "confidence": 0.0-1.0
}"
```

**Best practices**:
- Be specific and clear
- Provide context
- Use examples
- Iterate and refine
- Test variations

### Q9. Explain text-to-image generation.
**Answer**: 

**How it works**:

**1. Text encoding** (CLIP):
- Text → Text encoder → Text embedding

**2. Image generation**:
- Text embedding → Image generator → Image
- Typically diffusion model

**3. Iterative refinement**:
- Start with noise
- Guided by text embedding
- Denoise step by step

**Architecture (Stable Diffusion)**:
```
Text → CLIP encoder → Conditioning →
Noise → U-Net (denoise) → Latent image →
VAE decoder → Final image
```

**Key components**:

**CLIP** (Contrastive Language-Image Pre-training):
- Aligns text and images
- Trained on 400M text-image pairs

**Latent Diffusion**:
- Work in compressed space
- Faster than pixel-space diffusion

**Classifier-free guidance**:
- Control image quality vs diversity
- Higher guidance = more faithful to prompt

**Prompting techniques**:
```
"A photorealistic portrait of a cat,
highly detailed, 8k, trending on artstation,
digital art, dramatic lighting"
```

**Models**:
- DALL-E 2/3: OpenAI
- Stable Diffusion: Stability AI
- Midjourney: Independent
- Imagen: Google

### Q10. What is Retrieval Augmented Generation (RAG)?
**Answer**: 

**Problem**: LLMs have knowledge cutoff, can hallucinate

**Solution**: Retrieve relevant info, then generate

**Architecture**:
```
Query → Retrieve docs → Augment prompt → LLM → Response
```

**Components**:

**1. Document processing**:
- Chunk documents (512-1024 tokens)
- Generate embeddings
- Store in vector database

**2. Retrieval**:
- Query → Embedding
- Semantic search
- Top-k most relevant chunks

**3. Augmentation**:
```
Prompt: "Answer based on context:
Context: {retrieved_docs}
Question: {question}
Answer:"
```

**4. Generation**:
- LLM generates with context

**Benefits**:
- Up-to-date information
- Reduced hallucinations
- Factual accuracy
- Transparency (cite sources)

**Challenges**:
- Retrieval quality
- Context length limits
- Latency
- Cost

**Tools**:
- LangChain
- LlamaIndex
- Vector DBs: Pinecone, Weaviate, Chroma

## Image Generation (Questions 11-20)

### Q11. Explain DALL-E and how it works.
**Answer**: 

**DALL-E 1**:
- Modified GPT-3
- Treats images as sequences of tokens
- Autoregressive generation

**DALL-E 2**:
- **CLIP**: Text-image alignment
- **Prior**: Text → Image embedding
- **Decoder**: Diffusion model
- High resolution (1024×1024)

**DALL-E 3**:
- Better prompt following
- Integrated with ChatGPT
- Improved quality and detail

**Process**:
1. Text prompt
2. CLIP encodes text
3. Prior predicts image embedding
4. Diffusion decoder generates image
5. Super-resolution upscaling

**Capabilities**:
- Object combinations
- Styles (photorealistic, painting, etc.)
- Variations on existing images
- Inpainting/outpainting

### Q12. What is Stable Diffusion?
**Answer**: 

**Key innovation**: Latent diffusion model

**Architecture**:

**1. VAE encoder**:
- Image → Compressed latent (8x smaller)

**2. U-Net**:
- Denoise in latent space
- Conditioned on text (CLIP)

**3. VAE decoder**:
- Latent → Image

**Advantages**:
- **Open-source**: Free to use
- **Efficient**: Runs on consumer GPUs
- **Fast**: ~50 steps vs 1000
- **Controllable**: Many parameters

**Versions**:
- SD 1.5: 512×512
- SD 2.0/2.1: 768×768
- SDXL: 1024×1024

**Techniques**:

**ControlNet**: Add spatial guidance
```
Pose, depth, canny edges → Control generation
```

**LoRA**: Fine-tune on specific styles

**DreamBooth**: Personalization

**Textual Inversion**: Learn new concepts

### Q13-20. [More image generation topics]

**Q13**: Midjourney and its features
**Q14**: Image inpainting and outpainting
**Q15**: Style transfer with GANs
**Q16**: Super-resolution models
**Q17**: Image-to-image translation
**Q18**: ControlNet and guidance
**Q19**: Negative prompts
**Q20**: Prompt engineering for images

## Text Generation (Questions 21-30)

### Q21. Explain ChatGPT and its training process.
**Answer**: 

**Training stages**:

**1. Pre-training** (GPT base model):
- Next token prediction
- Internet text corpus
- Unsupervised learning

**2. Supervised Fine-Tuning (SFT)**:
- Human-written conversations
- Instruction-following examples
- ~10K high-quality conversations

**3. Reward Model (RM)**:
- Human rankers compare outputs
- Train model to predict preferences
- Scalar reward for each response

**4. Reinforcement Learning (PPO)**:
- Optimize for reward
- Balance: High reward + stay close to SFT
- Proximal Policy Optimization

**Result**: Helpful, harmless, honest assistant

**Versions**:
- GPT-3.5-turbo: Fast, affordable
- GPT-4: More capable, reasoning
- GPT-4-turbo: Longer context (128K)

### Q22. What is instruction tuning?
**Answer**: 

**Process**: Fine-tune on diverse instruction-following tasks

**Dataset format**:
```json
{
  "instruction": "Translate to Spanish",
  "input": "Hello world",
  "output": "Hola mundo"
}
```

**Datasets**:
- **FLAN**: 1,800+ tasks
- **InstructGPT**: Human feedback
- **Alpaca**: 52K instructions from GPT-3.5
- **Dolly**: 15K human-generated

**Benefits**:
- Better zero-shot performance
- Follows instructions better
- Generalizes to new tasks
- More helpful outputs

**Models**:
- InstructGPT
- FLAN-T5
- Alpaca
- Vicuna

### Q23-30. [More text generation]

**Q23**: Few-shot learning in LLMs
**Q24**: Temperature and sampling strategies
**Q25**: Beam search vs sampling
**Q26**: Top-k and top-p (nucleus) sampling
**Q27**: Model fine-tuning vs prompting
**Q28**: LoRA for efficient fine-tuning
**Q29**: Model compression and quantization
**Q30**: Multi-turn conversation management

## Code Generation (Questions 31-35)

### Q31. Explain GitHub Copilot and code generation models.
**Answer**: 

**GitHub Copilot**:
- Powered by OpenAI Codex
- Trained on public code repositories
- Suggests code as you type

**Codex**:
- Based on GPT-3
- Fine-tuned on code (GitHub, Stack Overflow)
- Understands multiple languages

**Capabilities**:
- Autocomplete
- Generate functions from comments
- Explain code
- Fix bugs
- Write tests

**Other code models**:
- **Code Llama**: Meta's code LLM
- **StarCoder**: Open-source code model
- **AlphaCode**: DeepMind's competitive programming
- **Replit Ghostwriter**: AI pair programmer

### Q32-35. [More code generation]

**Q32**: Code LLaMA architecture
**Q33**: Prompt engineering for code
**Q34**: Code evaluation and HumanEval
**Q35**: AI-assisted debugging

## Applications & Ethics (Questions 36-45)

### Q36. What are the main applications of Generative AI?
**Answer**: 

**Content Creation**:
- Articles, blog posts
- Marketing copy
- Social media content
- Email drafts

**Creative Arts**:
- Digital art, illustrations
- Music composition
- Video generation
- Game assets

**Software Development**:
- Code generation
- Code review
- Documentation
- Bug fixing

**Business**:
- Customer service chatbots
- Report generation
- Data analysis
- Presentation creation

**Education**:
- Tutoring
- Quiz generation
- Personalized learning
- Homework help

**Research**:
- Literature review
- Hypothesis generation
- Drug discovery
- Protein folding

**Healthcare**:
- Medical imaging
- Drug design
- Diagnosis assistance
- Treatment planning

### Q37. What are the ethical concerns with Generative AI?
**Answer**: 

**1. Misinformation**:
- Fake news generation
- Deepfakes
- Propaganda

**2. Bias and Fairness**:
- Training data biases
- Demographic disparities
- Stereotypes

**3. Copyright and IP**:
- Training on copyrighted material
- Who owns generated content?
- Artist attribution

**4. Job Displacement**:
- Writers, artists, programmers
- Economic impact
- Skill devaluation

**5. Privacy**:
- Model memorization
- PII leakage
- Consent for training data

**6. Misuse**:
- Phishing emails
- Academic dishonesty
- Scams and fraud

**7. Environmental**:
- Energy consumption
- Carbon footprint
- Resource usage

**Mitigation**:
- Watermarking
- Detection tools
- Ethical guidelines
- Regulation
- Transparency

### Q38-45. [More applications and ethics]

**Q38**: Deepfakes and detection
**Q39**: Content moderation challenges
**Q40**: Watermarking generated content
**Q41**: AI detection tools
**Q42**: Copyright issues
**Q43**: Bias in generative models
**Q44**: Environmental impact
**Q45**: Regulation and governance

## Technical Deep Dives (Questions 46-50)

### Q46. How do you evaluate generative models?
**Answer**: 

**Image generation**:

**1. Quantitative**:
- **FID** (Fréchet Inception Distance): Lower is better
- **IS** (Inception Score): Higher is better
- **LPIPS**: Perceptual similarity
- **SSIM**: Structural similarity

**2. Qualitative**:
- Human evaluation
- Visual inspection
- User studies

**Text generation**:

**1. Automatic metrics**:
- **Perplexity**: Lower is better
- **BLEU/ROUGE**: For specific tasks
- **BERTScore**: Semantic similarity

**2. Human evaluation**:
- Coherence
- Relevance
- Fluency
- Factual accuracy

**Code generation**:
- **pass@k**: Percentage passing tests
- **HumanEval**: Benchmark dataset
- **MBPP**: Python programming problems

**General**:
- Diversity
- Novelty
- Faithfulness to prompt
- Safety

### Q47. What is the attention mechanism in Transformers?
**Answer**: 

**Purpose**: Focus on relevant parts of input

**Self-attention**:
```
Attention(Q, K, V) = softmax(QK^T / √d_k) × V
```

**Process**:
1. Create Query, Key, Value matrices
2. Compute attention scores (Q × K^T)
3. Scale by √d_k
4. Apply softmax
5. Multiply by Values

**Multi-head attention**:
- Multiple attention mechanisms in parallel
- Each "head" learns different patterns
- Concatenate and project

**Example**:
```
Input: "The cat sat on the mat"

Self-attention learns:
- "cat" attends to "sat" (subject-verb)
- "sat" attends to "mat" (verb-object)
- "on" attends to "mat" (preposition-object)
```

**Types**:
- **Encoder**: Bidirectional (BERT)
- **Decoder**: Causal (GPT)
- **Cross-attention**: Encoder-Decoder

### Q48-50. [Final technical topics]

**Q48**: Training large models (distributed, mixed precision)
**Q49**: Model compression and distillation
**Q50**: Future directions in Generative AI

---

## Quick Interview Tips

1. **Understand fundamentals**: GANs, VAEs, Transformers, Diffusion
2. **Know popular models**: GPT, DALL-E, Stable Diffusion, Midjourney
3. **Practical experience**: Mention tools used (OpenAI API, HuggingFace, Stable Diffusion)
4. **Ethics awareness**: Discuss bias, misuse, copyright
5. **Applications**: Real-world use cases
6. **Technical depth**: Attention, training processes
7. **Current trends**: LLMs, multimodal models, efficient training

---

**Good luck with your Generative AI interview! 🚀**
