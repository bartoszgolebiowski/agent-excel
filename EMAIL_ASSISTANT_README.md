# Intelligent Correspondence Assistant

An autonomous AI-powered system that transforms unstructured email content into structured database records, ready for reporting and analysis.

## 📋 Overview

This system operates as a **Digital Worker** that:

- 📥 Monitors an inbox folder for email text files
- 🤖 Analyzes content using AI to extract structured data
- 📊 Saves results to an Excel report
- 📁 Archives processed emails automatically
- 🔄 Can run cyclically (e.g., every hour) or on-demand

## 🏗️ Architecture

The system follows a **state-driven, deterministic architecture**:

```
CHECK_INBOX → ANALYZE_EMAIL → SAVE_TO_EXCEL → ARCHIVE_EMAIL → CHECK_NEXT_EMAIL
     ↑                                                                  ↓
     └──────────────────────────────────────────────────────────────────┘
```

### State Machine Flow

1. **CHECK_INBOX**: Scans the inbox folder for `.txt` files
2. **ANALYZE_EMAIL**: AI analyzes email and extracts structured data:
   - Main Topic (e.g., "Login Error", "Quote Request")
   - Business Category (Sales, HR, Tech Support, Accounting, etc.)
   - Contact Data (emails/phone numbers)
   - Urgency Level (Low/Medium/High)
   - Sentiment (Positive/Neutral/Negative)
   - Summary (one-sentence abstract)
3. **SAVE_TO_EXCEL**: Appends analysis as new row in Excel report
4. **ARCHIVE_EMAIL**: Moves processed file to archive folder
5. **CHECK_NEXT_EMAIL**: Checks if more emails exist, loops or completes

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

This installs:

- `pydantic` - Data validation
- `jinja2` - Prompt templates
- `openai` - LLM integration
- `openpyxl` - Excel file handling
- `python-dotenv` - Environment configuration

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# OpenAI/OpenRouter API Key (required)
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini

# Email processing paths (optional - defaults shown)
INBOX_PATH=data/inbox
ARCHIVE_PATH=data/archive
EXCEL_PATH=data/email_report.xlsx

# Cyclic mode (optional)
CYCLIC_MODE=false              # Set to 'true' for continuous monitoring
CYCLE_INTERVAL_SECONDS=3600    # Run every hour (3600 seconds)
```

### 3. Add Sample Emails

Place email text files in the inbox folder:

```
data/inbox/
  ├── email_001.txt
  ├── email_002.txt
  └── email_003.txt
```

Each file should contain email content (subject, body, signature).

### 4. Run the Agent

**Single Run Mode:**

```bash
python src/main.py
```

**Cyclic Mode:**

```bash
# Set CYCLIC_MODE=true in .env, then:
python src/main.py
```

## 📂 Project Structure

```
agent-excel/
├── src/
│   ├── main.py                          # Entry point
│   ├── agent.py                         # Agent orchestration
│   ├── engine/
│   │   ├── coordinator.py               # State machine coordinator
│   │   ├── workflow_transitions.py      # State transition map
│   │   ├── executor.py                  # LLM executor
│   │   └── types.py                     # Workflow stages, action types
│   ├── memory/
│   │   ├── models.py                    # State data models
│   │   └── state_manager.py             # State update handlers
│   ├── skills/
│   │   ├── definitions.py               # Skill registry
│   │   ├── models.py                    # Skill output models
│   │   └── base.py                      # Skill base classes
│   ├── tools/
│   │   ├── email_tools.py               # File system operations
│   │   ├── executor.py                  # Tool dispatcher
│   │   └── models.py                    # Tool request/response models
│   ├── prompting/
│   │   └── jinja/
│   │       └── skills/
│   │           └── analyze_email.j2     # Email analysis prompt template
│   └── llm/
│       ├── client.py                    # LLM client wrapper
│       └── config.py                    # LLM configuration
├── data/
│   ├── inbox/                           # Input: Email files go here
│   ├── archive/                         # Output: Processed emails moved here
│   └── email_report.xlsx                # Output: Excel report (auto-created)
├── pyproject.toml                       # Project dependencies
└── .env.example                         # Environment configuration template
```

## 📊 Output Format

The system creates an Excel file (`data/email_report.xlsx`) with the following columns:

| Main Topic    | Business Category | Contact Data              | Urgency | Sentiment | Summary                                                   | Event Date          | Source File   |
| ------------- | ----------------- | ------------------------- | ------- | --------- | --------------------------------------------------------- | ------------------- | ------------- |
| Login Error   | Tech Support      | sarah.johnson@company.com | High    | Negative  | Authentication service down, blocking client presentation | 2026-01-17T10:30:00 | email_001.txt |
| Quote Request | Sales             | m.chen@techcorp.com       | Medium  | Neutral   | Enterprise package quote requested for 50 users           | 2026-01-17T10:31:00 | email_002.txt |

## 🔧 Configuration Options

### Paths

- **INBOX_PATH**: Where to look for email files (default: `data/inbox`)
- **ARCHIVE_PATH**: Where to move processed files (default: `data/archive`)
- **EXCEL_PATH**: Where to save the report (default: `data/email_report.xlsx`)

### Cyclic Mode

- **CYCLIC_MODE**: Enable continuous monitoring (`true`/`false`)
- **CYCLE_INTERVAL_SECONDS**: Time between cycles (default: 3600 = 1 hour)

### LLM Settings

- **OPENROUTER_API_KEY**: Your API key
- **OPENROUTER_MODEL**: Model to use (e.g., `openai/gpt-4o-mini`)
- **OPENROUTER_TEMPERATURE**: Creativity level (0-1, default: 0.2)
- **OPENROUTER_MAX_OUTPUT_TOKENS**: Max response length (default: 1200)

## 🎯 Use Cases

### Customer Support Triage

- Automatically classify incoming support tickets
- Identify urgent issues requiring immediate attention
- Route requests to appropriate departments

### Sales Lead Qualification

- Extract contact information from inquiries
- Assess lead quality based on sentiment and urgency
- Generate summary reports for sales team review

### Compliance & Auditing

- Archive all correspondence with timestamps
- Maintain structured records for regulatory compliance
- Enable quick searching and reporting

## 🔍 How It Works

### 1. Email Analysis (AI-Powered)

The system uses an LLM to intelligently extract:

- **Main Topic**: Identifies the core subject (e.g., "Login Error", "Quote Request")
- **Business Category**: Maps to departments based on content context
- **Contact Data**: Extracts emails/phones using pattern recognition
- **Urgency**: Detects keywords like "ASAP", "urgent", "critical"
- **Sentiment**: Analyzes emotional tone (positive/neutral/negative)
- **Summary**: Generates concise one-sentence abstract

### 2. Deterministic Workflow

Unlike LLM-driven control flow, this system uses a **state machine**:

```python
# Workflow transitions defined in workflow_transitions.py
TRANSITIONS = {
    WorkflowStage.CHECK_INBOX: (ActionType.TOOL, ToolName.CHECK_INBOX, "..."),
    WorkflowStage.ANALYZE_EMAIL: (ActionType.LLM_SKILL, SkillName.ANALYZE_EMAIL, "..."),
    # ... etc
}
```

This ensures:

- ✅ Predictable execution
- ✅ Easy debugging
- ✅ Reliable error handling
- ✅ No hallucinated control flow

### 3. State-Driven Memory

All data flows through a 7-layer memory architecture:

```python
AgentState
├── core: ConstitutionalMemory       # Ethical guardrails
├── working: WorkingMemory           # Current session context
│   └── email_processing: EmailProcessingState
├── workflow: WorkflowMemory         # State machine position
├── episodic: EpisodicMemory         # Event history
├── semantic: SemanticMemory         # Knowledge base
├── procedural: ProceduralMemory     # Tool definitions
└── resource: ResourceMemory         # System status
```

## 🛠️ Extending the System

### Adding a New Business Category

Edit [analyze_email.j2](src/prompting/jinja/skills/analyze_email.j2):

```jinja
2. **Business Category**: Assign the email to:
   - Sales
   - HR
   - Tech Support
   - Accounting
   - Customer Service
   - Legal  {# ← Add new category #}
   - Other
```

### Adding a New Field

1. **Update Output Model** ([skills/models.py](src/skills/models.py)):

   ```python
   class AnalyzeEmailSkillOutput(BaseModel):
       # ... existing fields ...
       priority_score: int = Field(..., description="Priority 1-10")
   ```

2. **Update Template** ([analyze_email.j2](src/prompting/jinja/skills/analyze_email.j2)):

   ```jinja
   7. **Priority Score**: Rate 1-10 based on urgency and sentiment.
   ```

3. **Update State Model** ([memory/models.py](src/memory/models.py)):

   ```python
   class EmailAnalysisResult(BaseModel):
       # ... existing fields ...
       priority_score: int
   ```

4. **Update Excel Tool** ([tools/models.py](src/tools/models.py), [tools/email_tools.py](src/tools/email_tools.py)):
   Add column and data handling.

## 🧪 Testing

```bash
# Process sample emails
python src/main.py

# Check output
ls data/archive/        # Should contain processed files
open data/email_report.xlsx  # Should have analysis rows
```

## 🐛 Troubleshooting

### No emails processed

- Check `INBOX_PATH` points to correct directory
- Ensure files have `.txt` extension
- Verify inbox folder exists and is readable

### LLM errors

- Confirm `OPENROUTER_API_KEY` is set correctly
- Check API key has sufficient credits
- Try a different model (e.g., `openai/gpt-3.5-turbo`)

### Excel file locked

- Close Excel if open during processing
- Check file permissions on `EXCEL_PATH`
- Try different output path

## 📝 License

See [licence.md](licence.md)

## 🤝 Contributing

This project follows a strict architectural pattern. Before contributing:

1. Read [.github/copilot-instructions.md](.github/copilot-instructions.md)
2. Follow the state-driven design principles
3. Never add LLM-based control flow
4. Use Pydantic models for all data structures
5. Add handlers to `state_manager.py` for new outputs

## 📚 Related Documentation

- [Architecture Guide](.github/instructions/architecture.instructions.md)
- [Memory System](.github/instructions/memory.instructions.md)
- [Skills Layer](.github/instructions/skills.instructions.md)
- [Tools Layer](.github/instructions/tools.instructions.md)
