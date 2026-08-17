# STELAR INTERIORS — AGNO MULTI-AGENT DESIGN CONSULTANT

A luxury multi-agent AI application for **Stelar Interiors**, an interior design company. Built using the **Agno** (`agno`) framework with modular enterprise architecture (`agent/`, `tools/`, `ui/`), a slim entry point (`app.py` under **75 lines**), a deterministic **Multi-Agent Orchestrator Pipeline**, **Zero Default Values** for live spec extraction, **Real-Time MX Email Deliverability Verification**, a standalone CLI **Scheduler Daemon (`run_scheduler.py`)**, direct **Mailtrap HTTPS REST API** delivery (`https://send.api.mailtrap.io/api/send`), custom chat avatars (`👤` / `✨`), a humble persuasive concierge persona with **strict 2-3 sentence brevity rules** for **Site Visit Consultation Slot Booking**, visual web image inspiration search, scraped physical design materials, and interactive 2D SVG floor plan layouts.

---

## 📚 Project Documentation

- **[understanding.md](understanding.md)**: Detailed project knowledge base, architectural analysis, Multi-Agent Orchestrator Pipeline, Mailtrap REST API implementation, persona & brevity guidelines, email deliverability validation, and chronological change log.

---

## 🏗️ Directory & Package Architecture

```text
stelar-interiors-ai/
│
├── app.py                      # Slim Main Entry Point (75 lines) with Intent Router & MX Verification
├── scheduler.py                # Core Scheduler Module & Queue Manager
├── run_scheduler.py            # Standalone CLI 2:00 PM Mailtrap Batch Dispatch Daemon
├── test_mail.py                # Dedicated Mailtrap Email Diagnostic Script
├── understanding.md            # Comprehensive project knowledge base & change log
│
├── ui/                         # Modular UI Package
│   ├── __init__.py
│   ├── styles.py              # CSS styles & brand header
│   ├── components.py          # SVG renderer & visual image cards (custom avatars)
│   └── sidebar.py             # Live Client Specs tracker & Standalone Dispatcher badge
│
├── agent/                      # Modular Agno Agent Definitions
│   ├── __init__.py
│   ├── root_agent.py          # Root Client Gathering Concierge Agent (Humble, Persuasive & Concise)
│   ├── requirement_agent.py   # Project Specification Extractor Agent
│   ├── research_agent.py      # Web Search & Material Scraper Agent
│   ├── layout_agent.py        # Spatial Geometry & 2D Floor Plan Agent
│   └── design_agent.py        # Color Palette & Final Concept Advisor
│
├── tools/                      # Modular Agentic Tools
│   ├── __init__.py
│   ├── web_tools.py           # web_search (images), fetch_page, fetch_materials
│   ├── design_tools.py        # generate_palette, calculate_layout
│   └── storage_tools.py       # verify_email_deliverability, save_consultation, send_email_consultation
│
├── consultations/              # Stores session .txt briefs & pending_queue.json
├── .env                        # LLM & Mailtrap Credentials
├── .env.example                # Configuration template
├── .gitignore                  # Git exclusion rules
├── requirements.txt            # Project dependencies
├── test_tools.py               # Automated unit test suite
└── README.md                   # Complete architectural documentation
```

---

## 🖥️ Running the Standalone Scheduler Daemon

Run the scheduler daemon in a separate terminal:
```bash
python run_scheduler.py
```

---

## 🔒 Email Deliverability Verification

`verify_email_deliverability` performs DNS MX record verification before accepting or sending emails. Invalid domains (e.g. `@fake12345domain.xyz`) are rejected automatically.

---

## 🚀 Quickstart

```bash
# Terminal 1: Run Standalone 2:00 PM Mailtrap Dispatcher
python run_scheduler.py

# Terminal 2: Run Streamlit Application
streamlit run app.py
```
