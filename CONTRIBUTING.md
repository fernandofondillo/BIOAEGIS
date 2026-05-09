# Contributing to BioFish AI

Thank you for your interest in contributing to BioFish AI! 🎉

## How to Contribute

### 1. Reporting Bugs

- Use the [GitHub Issues](https://github.com/fernandofondillo/BIOFISH-AI/issues) tab
- Search for existing issues first
- Include: Python version, error message, minimal reproduction steps
-标签 preferidas: `bug`, `enhancement`, `question`

### 2. Proposing New Agents or Interventions

BioFish AI is extendable. To add a new biological agent:

```python
# 1. Define the agent profile in src/agent.py
AgentProfile(
    id="new_agent",
    name="Dr. New",
    role="Especialista en...",
    specialty="...",
    biomarkers=["biomarker1", "biomarker2"],
    signal_receives=["SIGNAL_NAME"],
    signal_emits=["SIGNAL_EMIT"],
    avatar_color="#COLOR",
    icon="🔬",
)

# 2. Add the assessment method in src/orchestrator.py
def _assess_new_agent(self, b: Dict, d: Dict):
    concerns, actions = [], []
    # Your logic here
    return assessment, concerns, actions

# 3. Add system prompt in src/agent_llm.py if using LLM
SYSTEM_PROMPTS["new_agent"] = """Your system prompt..."""

# 4. Add intervention effects in src/interventions.py if applicable
```

### 3. Adding Interventions

Interventions must include:
- Effect size based on published meta-analysis or RCT
- Confidence level (A/B/C based on evidence quality)
- Ceiling effect (maximum possible change)
- Contraindications and risks
- Time to effect (months)

### 4. Code Style

```bash
# Format code
black src/ tests/ examples/

# Lint
ruff src/ tests/

# Type check
mypy src/
```

### 5. Pull Request Process

1. Fork the repo and create your branch from `main`
2. Add tests for new functionality
3. Ensure all tests pass: `pytest tests/ -v`
4. Update documentation if needed
5. Request review from a maintainer

## Development Setup

```bash
git clone https://github.com/fernandofondillo/BIOFISH-AI.git
cd BIOFISH-AI
pip install -r requirements.txt
pip install -r requirements-dev.txt
export GROQ_API_KEY=your_test_key
pytest tests/ -v
```

## Commit Convention

```
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
test:     Adding or updating tests
refactor: Code refactoring
chore:    Maintenance tasks
```

## Questions?

- Open a GitHub Discussion
- Tag us in an Issue

## Code of Conduct

Be respectful, inclusive, and constructive. We follow the [Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).