# 🎙️ Voice AI Architect Skill

An advanced Agent Skill designed to help developers architect, design, and code production-ready Voice AI conversational flows using **LangGraph**.

## 🎯 What it does
Voice interactions are vastly different from text chats. This skill guides the AI to avoid legacy "chatbot" monoliths and instead build robust, interruptible, state-driven Voice AI engines. 

It enforces a strict 4-step workflow:
1. **Brain Discovery:** Requirement gathering and business logic constraints.
2. **LangGraph Visualization:** Generates Mermaid.js diagrams with clear branching and state isolation.
3. **Behavioral Layer:** Crafts voice-optimized micro-prompts and structured output guardrails.
4. **Logic Implementation:** Generates clean, monolithic-free `graph.py` and `state.py` code.

## 📁 Repository Structure
```text
voice-ai-architect/
├── SKILL.md                 # The core brain, instructions, and constraints for the AI
├── README.md                # This documentation file
├── .cursorrules             # Pointer configuration for Cursor IDE
├── claude.md                # Pointer configuration for Claude Code CLI
├── references/              # Essential architectural guidelines (Anti-patterns, Think->Act, Guardrails)
└── assets/                  # Boilerplate code templates (base_state.py, base_graph.py)
```

## 🚀 How to use
This skill complies with the open Agent Skills Specification.

### Step 1: Setup
Clone or download this repository into your local development environment.

### Step 2: Choose your agent
* **In Cursor IDE:** Open the folder in Cursor. The included `.cursorrules` automatically routes the AI to use `SKILL.md`. Start a new Chat or Composer session and ask to build a voice agent.
* **With Claude Code (CLI):** Navigate to the folder in your terminal and run `claude`. The `claude.md` file ensures Claude understands its terminal execution abilities while following the architectural constraints.

## 🧠 Architectural Principles Enforced
* **No God Nodes:** Strict branch routing to prevent logic bloat.
* **The Wrapper Contract:** The graph strictly handles logic (The Brain); it does NOT handle TTFB, audio streaming, or database saves.
* **Three-Layer Guardrails:** Implementing a `pre_tts_validator` as a strict exit-filter to ensure output safety.