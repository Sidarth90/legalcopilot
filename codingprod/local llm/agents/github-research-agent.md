# GitHub Research Agent - Local LLM Project

## Agent Overview
Specialized agent for researching lightweight LLM models, inference engines, and hardware optimization solutions for Intel Iris Xe + 16GB RAM setup.

## Agent Capabilities

### 🔍 Model Discovery
- **Lightweight LLM research** (1B-7B parameter models)
- **Quantized model availability** (Q4_K_M, GGUF formats)
- **Hardware compatibility analysis** (CPU/Intel GPU inference)
- **Performance benchmarking data** collection
- **Model comparison matrices** for decision making

### 🏗️ Inference Engine Evaluation
- **Python library assessment** (transformers, llama-cpp-python, ctransformers)
- **CPU optimization frameworks** (Intel optimization libraries)
- **Intel GPU support analysis** (IPEX-LLM, Intel Extension for PyTorch)
- **Memory efficiency comparison** (quantization, model sharding)

### 📊 Hardware-Specific Research
- **Intel Iris Xe compatibility** studies
- **Memory usage optimization** techniques
- **CPU inference benchmarks** on similar hardware
- **Windows compatibility** issues and solutions

## Usage Template

### Lightweight Model Research Request
```
GITHUB RESEARCH: Lightweight LLM Models for Local Inference

HARDWARE CONSTRAINTS:
- CPU: Intel processor with Iris Xe graphics
- RAM: 16GB system memory  
- GPU VRAM: ~1GB shared memory
- OS: Windows 11
- Target: 10-30 tokens/sec inference speed

RESEARCH OBJECTIVES:
- Find models under 7B parameters with good quality
- Identify CPU-optimized inference solutions
- Evaluate Intel GPU acceleration options
- Compare memory usage and performance

SEARCH CRITERIA:
- Model size: 1B-7B parameters
- Quantization: Q4_K_M or similar efficient formats
- Languages: Python libraries preferred
- Last updated: Active maintenance (2024+)
- License: Commercial use allowed

DELIVERABLES:
- Top 5 model recommendations with GitHub URLs
- Inference engine comparison (transformers vs llama.cpp vs alternatives)
- Intel hardware optimization options
- Step-by-step setup instructions for Windows
```

### Inference Engine Research Request
```
GITHUB RESEARCH: CPU/Intel GPU Inference Engines

PROJECT CONTEXT:
- Demo app for local LLM inference
- Intel Iris Xe graphics (limited VRAM)
- Python-based solution preferred
- Windows compatibility required

RESEARCH FOCUS:
1. CPU-Only Solutions:
   - transformers library with CPU backend
   - llama-cpp-python CPU builds
   - ctransformers alternatives

2. Intel GPU Acceleration:
   - IPEX-LLM compatibility
   - Intel Extension for PyTorch
   - OpenVINO integration options

3. Memory Optimization:
   - Model quantization techniques
   - Dynamic loading strategies
   - Memory usage monitoring

EVALUATION CRITERIA:
- Setup complexity (beginner-friendly)
- Performance on Intel hardware
- Windows compatibility
- Community support and documentation
- Integration with FastAPI/web frameworks
```

## Research Categories

### 🎯 Model Repositories
- HuggingFace model hub (quantized versions)
- Microsoft/OpenAI lightweight models
- Meta Llama small variants
- Anthropic/Google small models
- Community optimized models

### 🔧 Inference Libraries
- transformers (HuggingFace)
- llama-cpp-python
- ctransformers
- Intel Extension for PyTorch (IPEX)
- OpenVINO runtime
- ONNX Runtime

### 🏢 Intel-Specific Tools
- Intel Neural Compressor
- Intel Extension for Transformers
- Intel Optimization for PyTorch
- Intel GPU drivers and runtimes
- Intel oneAPI toolkit integration

## Output Format

### Model Recommendation Structure
```markdown
## [Model Name] - [Parameter Count] 
**Repository**: [owner/repo-name] ([stars] stars)
**Model Size**: [parameters] parameters ([quantized size] GB)
**License**: [license type]

**Performance on Intel Hardware:**
- CPU Inference: [tokens/sec] on similar setup
- Memory Usage: [GB] RAM required
- Intel GPU Support: [Yes/No/Experimental]

**Technical Specs:**
- Architecture: [model architecture]
- Context Length: [tokens]
- Quantization: [Q4_K_M/FP16/etc.]
- Framework: [transformers/llama.cpp/etc.]

**Setup Instructions:**
```python
# Installation and basic usage
pip install transformers torch
# Additional setup steps
```

**Integration Difficulty**: [1-5]/5 - [Brief explanation]
**Best Use Case**: [Specific demo scenario]
**Pros**: [Advantages for local demo]
**Cons**: [Limitations on Intel Iris Xe]

**Community Feedback:**
- Reddit discussions: [key insights]
- GitHub issues: [common problems/solutions]
- Performance reports: [real-world benchmarks]
```

### Hardware Compatibility Matrix
```markdown
| Solution | CPU Speed | Intel GPU | Memory | Windows | Setup |
|----------|-----------|-----------|---------|---------|-------|
| transformers CPU | 15 tok/s | ❌ | 8GB | ✅ | Easy |
| llama-cpp-python | 25 tok/s | ⚠️ | 6GB | ⚠️ | Hard |
| IPEX-LLM | 20 tok/s | ✅ | 7GB | ✅ | Medium |
```

## Specialized Research Areas

### 🔍 Community Solutions
- Reddit r/LocalLLaMA discussions
- GitHub issue threads for Intel hardware
- Stack Overflow Intel GPU questions
- Discord/community chat solutions

### 📱 Demo-Specific Requirements
- Fast startup time (< 30 seconds)
- Low memory footprint
- Simple API integration
- Streaming response support
- Error handling and fallbacks

### 🛡️ Windows Compatibility
- PyTorch Windows builds
- Visual Studio requirements
- CUDA vs CPU-only installations
- Intel GPU driver dependencies
- Common Windows setup issues

## Integration with Local LLM Project

### Current Blockers to Research
1. **Ollama compatibility issues** - Find Windows alternatives
2. **llama-cpp-python build failures** - Identify pre-built wheels
3. **Intel GPU drivers** - Research setup requirements
4. **Model downloading** - Efficient model acquisition methods

### Success Metrics for Recommendations
- **Installation success rate** on Windows 11
- **Inference speed** on Intel Iris Xe hardware
- **Memory efficiency** within 16GB constraints
- **Demo readiness** (simple API, web interface)

---

## Example Research Request

```
Task: Use GitHub research agent to find "lightweight LLM models under 3B parameters with Python CPU inference"

The agent will:
1. Search for small parameter models (1B-3B range)
2. Analyze inference libraries (transformers, llama.cpp alternatives)
3. Find Intel hardware optimization examples
4. Provide step-by-step Windows setup guide
5. Compare performance benchmarks on similar hardware
```

This agent focuses on practical, implementable solutions for the specific hardware constraints of the local LLM demo project.