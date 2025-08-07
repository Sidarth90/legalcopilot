# GitHub Scraper & Research Agent

## Agent Overview
Specialized agent for comprehensive GitHub repository research, analysis, and data extraction. Designed for finding, evaluating, and comparing open-source libraries, tools, and solutions for specific technical requirements.

## Agent Capabilities

### 🔍 Repository Discovery
- **Advanced search strategies** across multiple GitHub criteria
- **Trending and popular repository identification**
- **Language-specific library research**
- **Domain-specific tool discovery** (e.g., PDF, AI, legal tech)
- **Alternative and competitor analysis**

### 📊 Repository Analysis
- **Technical assessment** (stars, forks, issues, PRs)
- **Maintenance evaluation** (last commit, release frequency)
- **Community health metrics** (contributors, discussions)
- **Documentation quality review**
- **Code quality indicators**

### 🏗️ Integration Assessment
- **Dependency analysis** and compatibility checking
- **Framework integration complexity** evaluation
- **Performance and bundle size** considerations
- **Learning curve and implementation time** estimates
- **Migration path analysis** from existing solutions

### 📈 Comparative Analysis
- **Feature matrix comparison** across multiple libraries
- **Pros/cons evaluation** with use case recommendations
- **Best fit analysis** for specific project requirements
- **Risk assessment** for adoption decisions

## Usage Instructions

### When to Use This Agent
- Researching libraries for specific technical requirements
- Evaluating alternatives to current implementations
- Finding best practices and implementation examples
- Conducting technology stack decisions
- Competitive analysis of open-source solutions

### How to Invoke
```
Use Task tool with subagent_type: "general-purpose"
Description: "GitHub repository research"
Prompt: [Detailed research requirements following template below]
```

## Prompt Template

### Basic Research Request
```
I need comprehensive GitHub research for [SPECIFIC DOMAIN/TECHNOLOGY].

RESEARCH OBJECTIVES:
- [Primary goal, e.g., "Find PDF highlighting libraries"]
- [Secondary goals, e.g., "Evaluate integration complexity"]
- [Constraints, e.g., "Must work with React"]

SEARCH CRITERIA:
- Keywords: [relevant search terms]
- Language: [JavaScript/Python/etc]
- Minimum stars: [threshold]
- Last updated: [timeframe]
- License requirements: [if any]

EVALUATION CRITERIA:
- [Technical requirements]
- [Performance requirements]  
- [Integration requirements]
- [Maintenance requirements]

DELIVERABLES NEEDED:
- Top [X] recommendations with GitHub URLs
- Feature comparison matrix
- Integration difficulty ratings (1-5)
- Implementation examples
- Risk/benefit analysis
```

### Advanced Research Request
```
ADVANCED GITHUB RESEARCH REQUEST

PROJECT CONTEXT:
- Current tech stack: [details]
- Problem to solve: [specific issue]
- Timeline: [implementation timeframe]
- Team expertise: [skill levels]

COMPREHENSIVE ANALYSIS REQUIRED:

1. DISCOVERY PHASE:
   - Search strategies: [specific approaches]
   - Repository filtering: [criteria]
   - Trend analysis: [recent developments]

2. EVALUATION MATRIX:
   - Technical metrics: [performance, size, dependencies]
   - Community metrics: [activity, support, documentation]
   - Business metrics: [license, maintenance, longevity]

3. DEEP DIVE ANALYSIS:
   - Code quality assessment
   - Issue/PR analysis for stability
   - Performance benchmarking data
   - Security vulnerability scanning

4. INTEGRATION PLANNING:
   - Migration complexity assessment
   - Breaking change analysis
   - Learning curve evaluation
   - Implementation timeline estimation

5. RISK ASSESSMENT:
   - Dependency risks
   - Maintenance risks  
   - Performance risks
   - License/legal risks

DELIVERABLES:
- Executive summary with top 3 recommendations
- Detailed technical analysis report
- Integration roadmap and timeline
- Risk mitigation strategies
- Code examples and proof of concepts
```

## Research Categories

### 🎯 Frontend Libraries
- UI component libraries
- JavaScript frameworks and utilities
- CSS frameworks and tools
- Build tools and bundlers

### 🔧 Backend & API Tools
- Server frameworks
- Database libraries
- API development tools
- Authentication and security

### 🤖 AI & Machine Learning
- ML libraries and frameworks
- Natural language processing
- Computer vision tools
- AI model deployment

### 📄 Document Processing
- PDF manipulation libraries
- Document parsing tools
- Text extraction utilities
- Annotation and markup systems

### 🏢 Domain-Specific Tools
- Legal technology libraries
- Financial analysis tools
- Healthcare applications
- E-commerce solutions

### ⚡ Performance & DevOps
- Optimization libraries
- Monitoring and analytics
- CI/CD tools
- Testing frameworks

## Output Format Standards

### Repository Recommendation Structure
```markdown
## [Repository Name] ⭐️⭐️⭐️⭐️⭐️
**GitHub**: [owner/repo-name] ([stars] stars, [forks] forks)
**Last Updated**: [date]
**License**: [license type]

**Key Features:**
- [Feature 1 with technical details]
- [Feature 2 with technical details]
- [Feature 3 with technical details]

**Technical Specs:**
- Language: [primary language]
- Dependencies: [major dependencies]
- Bundle Size: [if applicable]
- Browser Support: [compatibility]

**Code Example:**
```[language]
[Working code example showing key usage]
```

**Integration Difficulty**: [1-5]/5 - [Brief explanation]
**Best Use Case**: [Specific scenario where this excels]
**Pros**: [Advantages]
**Cons**: [Limitations or drawbacks]

**Community Health:**
- Contributors: [number] 
- Issues: [open/total]
- Pull Requests: [recent activity]
- Documentation: [quality assessment]
```

### Comparison Matrix Format
```markdown
| Feature | Library A | Library B | Library C |
|---------|-----------|-----------|-----------|
| GitHub Stars | 2.5k ⭐️ | 1.2k ⭐️ | 890 ⭐️ |
| Last Update | 2024-01 ✅ | 2023-12 ✅ | 2023-06 ⚠️ |
| TypeScript | ✅ Full | ✅ Partial | ❌ No |
| Bundle Size | 45KB | 78KB | 23KB |
| React Support | ✅ Native | 🔧 Plugin | 🔧 Wrapper |
| Documentation | ⭐️⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️ | ⭐️⭐️ |
```

## Advanced Features

### 🔍 Trend Analysis
- **Emerging technology identification**
- **Growth trajectory analysis**
- **Adoption pattern recognition**
- **Future roadmap assessment**

### 📱 Ecosystem Analysis
- **Related library discovery**
- **Plugin and extension ecosystems**
- **Integration compatibility matrices**
- **Community contribution patterns**

### 🛡️ Security & Compliance
- **Vulnerability database checks**
- **License compatibility analysis**
- **Supply chain risk assessment**
- **Security best practices review**

### 📊 Performance Benchmarking
- **Performance comparison data**
- **Benchmark result analysis**
- **Real-world performance metrics**
- **Optimization recommendations**

## Best Practices

### Research Methodology
1. **Start broad, narrow down systematically**
2. **Use multiple search strategies**
3. **Cross-reference findings**
4. **Verify information currency**
5. **Test key functionality claims**

### Quality Assessment
1. **Prioritize active maintenance**
2. **Evaluate community engagement**
3. **Check real-world usage examples**
4. **Assess documentation completeness**
5. **Review issue resolution patterns**

### Risk Mitigation
1. **Identify single points of failure**
2. **Assess maintainer bus factor**
3. **Evaluate alternative options**
4. **Plan migration strategies**
5. **Document decision rationale**

## Integration with LegalCopilot Project

### Specialized Use Cases
- **Legal technology library research**
- **PDF processing tool evaluation**
- **Document analysis framework comparison**
- **Contract processing solution assessment**
- **AI/ML legal application research**

### Domain-Specific Criteria
- **Legal compliance requirements**
- **Document security considerations**
- **Professional-grade reliability**
- **Enterprise scalability needs**
- **Audit trail capabilities**

## Usage History Template

Keep track of research requests and outcomes:

```markdown
## Research Request Log

### [Date] - [Project/Feature Name]
**Objective**: [What was researched]
**Key Findings**: [Summary of discoveries]
**Chosen Solution**: [Final decision]
**Implementation Status**: [Current status]
**Lessons Learned**: [Insights for future research]
```

---

## Example Usage

```
Task: Use GitHub scraper agent to research "React component libraries for data visualization"

The agent will:
1. Search GitHub for popular React + data visualization libraries
2. Analyze top repositories for features, maintenance, and community
3. Provide detailed comparison matrix
4. Recommend best options with integration examples
5. Assess migration complexity from current solutions
```

This agent is designed to save significant research time and provide comprehensive, actionable intelligence for technical decision-making processes.