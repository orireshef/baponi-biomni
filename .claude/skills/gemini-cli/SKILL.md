# Gemini CLI Skill

## Purpose
Use Gemini CLI as a PhD-level research assistant for mathematical reasoning, formal proofs, literature review, and web research. Gemini excels at complex mathematical formulations, LaTeX notation, and multi-step analytical reasoning.

## When to Use

### Primary Use Cases
- **Mathematical Proofs**: Formal derivations, correctness proofs, theorem validation
- **Complex Formulations**: Translating algorithms to rigorous mathematical notation
- **Literature Review**: Academic paper analysis, citation tracking, related work
- **Statistical Validation**: Hypothesis testing, convergence analysis, complexity bounds
- **Multi-Step Reasoning**: Chain-of-thought problems requiring deep expertise
- **Web Research**: Current state-of-the-art methods, benchmark comparisons

### Specific Scenarios
- Validating Bayesian update rules (e.g., Oja's Rule formulation)
- Deriving convergence guarantees for iterative algorithms
- Analyzing distributional properties (e.g., categorical priors, embeddings)
- Comparing against academic literature (DreamCoder, Relational Embodiments, etc.)
- Formulating mathematical objectives (loss functions, scoring metrics)
- Proving equivalence between algorithm variants

## Basic Usage

### Headless Mode (Recommended for Automation)
```bash
# Basic query
gemini -p "Prove that the Oja's Rule update converges to the top eigenvector"

# With JSON output for parsing
gemini -p "Derive the gradient of the composite join scoring function" --output-format json

# Auto-approve mode (use with caution)
gemini -p "Analyze convergence properties" --yolo
```

### With Context Injection
```bash
# Pipe file content
cat docs/SCDIC\ Final\ Algorithm\ Spec\ v14.0.md | gemini -p "Validate the mathematical formulation of P_join initialization"

# Include multiple directories
gemini -p "Compare SCDIC's approach to DreamCoder's wake-sleep learning" --include-directories docs,docs/papers

# Reference specific files with @
gemini -p "Review the Hebbian learning section @docs/architecture.md"
```

### Interactive Mode
```bash
# Start conversation
gemini

# Use slash commands within session
/model gemini-2.0-flash-exp-google  # Switch to experimental model
/memory add "SCDIC uses two-level prior hierarchy"
/chat save scdic-analysis
```

## Advanced Features

### Session Management
```bash
# Save conversation for later
gemini -p "Initial analysis of composite join discovery"
# (In session): /chat save composite-joins-analysis

# Resume previous session
gemini /chat resume composite-joins-analysis

# List all saved sessions
gemini /chat list
```

### Shell Integration
```bash
# Execute commands within Gemini context
echo "Analyze this error log" | gemini -p "!cat /var/log/scdic.log"

# Combine with other tools
git diff | gemini -p "Review changes for mathematical correctness"
```

### Context Management (GEMINI.md)
Create a `GEMINI.md` file in your project root to provide persistent context:

```markdown
# SCDIC Project Context

## Core Algorithm
- Stochastic Contract-Driven Inverse Compilation
- Two-level prior: P_lat (table affinity) + P_join (column configurations)
- Hebbian learning via Oja's Rule with reality decay

## Key Mathematical Concepts
- DNA: 256-byte column signature (type, cardinality, embeddings)
- Composite joins: Multi-column configurations (e.g., tenant_id + entity_id)
- Physics-first validation: Execute queries for ground truth

## References
- DreamCoder (Ellis et al., 2021): Wake-sleep program synthesis
- Relational Embodiments: Additive tuple embeddings
```

Then Gemini will automatically use this context:
```bash
gemini -p "Does our Oja's Rule implementation match the literature?"
# Gemini automatically loads GEMINI.md context
```

## Output Formats

### JSON (for programmatic parsing)
```bash
gemini -p "List 3 convergence criteria for Bayesian updates" --output-format json
```

Output:
```json
{
  "response": "1. KL divergence < epsilon\n2. Weight change < threshold\n3. Maximum iterations reached",
  "metadata": { ... }
}
```

### Markdown (for documentation)
```bash
gemini -p "Explain Oja's Rule in LaTeX" --output-format markdown > docs/oja_rule_explained.md
```

## Best Practices

### 1. Be Specific
**Good**: "Derive the gradient of Score(S) = w_e^T * sum(DNA_i ⊕ DNA_j) with respect to w_e"
**Bad**: "How does the scoring function work?"

### 2. Provide Context
**Good**:
```bash
cat docs/SCDIC\ Final\ Algorithm\ Spec\ v14.0.md | gemini -p "Section 3.2 describes P_join initialization. Prove that the configuration weights form a valid categorical distribution."
```
**Bad**: "Is P_join valid?"

### 3. Request LaTeX for Precision
**Good**: "Express the Bayesian update rule in LaTeX with explicit prior and posterior terms"
**Bad**: "Explain Bayesian updates"

### 4. Ask for Step-by-Step Reasoning
**Good**: "Prove convergence using: 1) Show bounded updates 2) Demonstrate monotonicity 3) Apply contraction mapping"
**Bad**: "Does this converge?"

### 5. Validate Against Literature
**Good**: "Compare our composite join discovery to DreamCoder's abstraction phase from @docs/papers/DreamCoder/dreamcoder.tex"
**Bad**: "Is this similar to DreamCoder?"

## Common Patterns

### Mathematical Validation
```bash
# Validate algorithm correctness
gemini -p "Prove that DNA similarity s'_AB = s_AB / max(s) creates a valid probability distribution over column pairs"

# Convergence analysis
gemini -p "Show that Oja's Rule with learning rate η=0.05 and decay λ=0.01 converges for bounded DNA embeddings"

# Complexity bounds
gemini -p "Derive the time complexity of greedy composite key construction with MAX_K=3 and N candidate pairs"
```

### Literature Comparison
```bash
# Academic positioning
cat docs/papers/DreamCoder/dreamcoder.tex | gemini -p "How does SCDIC's physics-first approach differ from DreamCoder's type-driven synthesis?"

# Benchmark comparison
gemini -p "Research Spider 2.0 benchmark requirements and compare to our nested type handling strategy"

# Related work
gemini -p "Find papers on learned join discovery using embeddings (published 2020-2025)"
```

### Formulation Assistance
```bash
# Loss function design
gemini -p "Design a loss function for learning P_config that balances embedding orthogonality and cardinality collapse ratio"

# Metric definition
gemini -p "Formalize the Cardinality Collapse Ratio R = Card(single) / Card(composite) as a physics validation metric"

# Algorithm pseudocode
gemini -p "Write formal pseudocode for greedy composite key construction using additive embeddings"
```

## Integration with AI-Researcher Agent

When working on SCDIC research tasks:

1. **Delegate Mathematical Reasoning**: Use Gemini for proofs, derivations, and formal analysis
2. **Validate Formulations**: Confirm algorithm notation matches literature standards
3. **Literature Review**: Research state-of-the-art approaches and benchmark requirements
4. **Complexity Analysis**: Derive time/space bounds for algorithmic components

Example workflow:
```bash
# 1. Agent identifies need for mathematical validation
# 2. Prepare context and question
# 3. Invoke Gemini CLI
gemini -p "Validate that our two-level prior (P_lat + P_join) forms a valid hierarchical Bayesian model" --include-directories docs

# 4. Parse response and incorporate into research analysis
```

## Limitations

- **No Code Execution**: Gemini CLI cannot run Python/JAX code directly (use local environment)
- **No File Modification**: Read-only analysis (use Edit tool for changes)
- **Rate Limits**: Google API quotas apply (check usage with account dashboard)
- **Context Window**: Large papers may need chunking (use `head`/`tail` or excerpt key sections)

## Quick Reference

| Task | Command |
|------|---------|
| Mathematical proof | `gemini -p "Prove that X converges"` |
| Validate formulation | `cat spec.md \| gemini -p "Check Section 3.2 math"` |
| Literature review | `gemini -p "Find papers on topic X from 2020-2025"` |
| LaTeX notation | `gemini -p "Express algorithm Y in LaTeX"` |
| Compare approaches | `gemini -p "Compare A vs B from @paper.tex"` |
| Complexity analysis | `gemini -p "Derive time complexity of Z"` |
| Save session | `/chat save session-name` (in interactive mode) |
| Resume session | `gemini /chat resume session-name` |

## Example: SCDIC Mathematical Validation

```bash
# Validate the composite join scoring function
cat docs/SCDIC\ Final\ Algorithm\ Spec\ v14.0.md | gemini -p "
Section 8.7.2 defines Score(S) = w_e^T * (sum_{i=1}^k DNA_{c_A^(i)} ⊕ DNA_{c_B^(i)}).

1. Prove that this score function is:
   a) Permutation invariant (order of pairs doesn't matter)
   b) Monotonic in pair similarity (higher DNA_sim → higher score)
   c) Bounded for normalized DNA embeddings

2. Express the gradient ∇_w Score(S) in closed form for gradient-based optimization.

3. Compare to the additive embedding property from 'Relational Embodiments' paper.

Provide step-by-step proofs with LaTeX notation.
" --output-format markdown > docs/validation/composite_scoring_proof.md
```

This would generate a formal mathematical analysis suitable for research documentation.
