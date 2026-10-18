# 🎙️ CodeVocalis AI – Intelligent Voice & AI Coding Assistant

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.0%2B-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-orange.svg)](https://www.mysql.com/)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-Google%20Gemini%20Flash-brightgreen.svg)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**CodeVocalis AI** is an advanced, production-style AI Voice Assistant and Autonomous Agent platform engineered **exclusively for Software Developers, Programmers, and CS Students**.

It empowers users to **speak or type programming questions** in natural language or regional languages (English, Marathi, Hindi) and receive accurate, syntactically correct code, deep technical explanations, and audio speech narration.

---

## 🌟 Key Features

### 1. 🎙️ Real-Time Voice Interaction (Speech-to-Text & Text-to-Speech)
- **Interactive Voice Input**: One-click glowing microphone with real-time browser transcription via Web Speech API and backend speech endpoints.
- **Audio Narration (TTS)**: Listens to executive summaries while keeping runnable code snippets visual, clean, and copyable. Audio can be toggled on/off with 1 click.

### 2. ⚡ Adaptive & Natural Code Generation
- **Beginner & Student Friendly**: When simple tasks are asked (e.g., *addition in python*, *swap two numbers*, *fibonacci*, *even/odd*, *factorial*), it generates clean, readable, textbook-standard code with interactive `input()` and sample output blocks without over-complication.
- **Production-Grade Frameworks**: When advanced framework tasks are asked (FastAPI, React, Next.js, Spring Boot, PyTorch, Docker, Django), it generates complete, enterprise-ready code with design patterns and best practices.
- **1-Click Copy**: Syntax-highlighted code blocks with a dedicated copy button.

### 3. 🛡️ Programming Domain Focus Guard
- Strictly dedicated to **Programming Languages, Frameworks, Software Engineering, Algorithms, and System Design**.
- Automatically filters out unrelated general queries (politics, movies, general trivia) and politely guides the user back to programming topics.

### 4. 🗄️ Dual Database Architecture (WAMP MySQL & SQLite)
- **WAMP Server MySQL**: Fully integrated with local WAMP / XAMPP MySQL server on `127.0.0.1:3306` (`voice_assistant_db`).
- **SQLite Fallback**: Zero-configuration local database support out-of-the-box.
- **Persistent Storage**: Securely stores Users, Conversations, Messages, and Uploaded Code Documents.

### 5. 🔑 Live AI Engine (Google Gemini 3.0 / 3.8 Flash)
- Direct integration with Google's latest **Gemini Flash models** (`gemini-3-flash-preview`, `gemini-3.8-flash`).
- **In-App AI Key Modal**: Users can paste their free Google AI Studio key directly in the dashboard UI without touching `.env` manually.
- **Curated Knowledge & Dynamic Fallback**: Robust offline technical dictionary and search fallback to ensure answers are provided even if the network is interrupted.

### 6. 📄 Codebase & Document Q&A
- Upload `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.sql`, `.pdf`, `.txt`, or `.docx` files.
- The assistant extracts function signatures, classes, and logic to answer questions directly about the uploaded codebase (e.g., *"What does calculate_tax function do?"*).

### 7. 🔐 Cryptographic Authentication
- User Registration and Login with modern cryptographic password hashing (`scrypt:32768:8:1` via Werkzeug).
- Session protection via Flask-Login `@login_required`.

---

## 💻 Supported Ecosystems

| Domain | Technologies Supported |
| :--- | :--- |
| **Programming Languages** | Python, JavaScript (ES6+), TypeScript, Java, C, C++, C#, Go, Rust, PHP, Dart, Kotlin, Swift, SQL, Bash/Shell, HTML5/CSS3 |
| **Frontend Frameworks** | React.js, Next.js (App Router, Server/Client components), Vue.js, Angular, Tailwind CSS, Bootstrap 5 |
| **Backend Frameworks** | FastAPI, Flask, Django, Node.js, Express.js, NestJS, Spring Boot, Laravel |
| **Mobile Development** | Flutter, React Native, Android, iOS |
| **Databases & ORMs** | MySQL, PostgreSQL, SQLite, MongoDB, Redis, SQLAlchemy, PyMySQL |
| **Data Science & AI** | PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy |
| **Core CS & DevOps** | Algorithms (Sorting, Binary Search, DP), Data Structures (Tree, BST, Graph, Stack, Queue), Docker, Git, REST APIs, GraphQL |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: MySQL (WAMP Server on port 3306) / SQLite
- **AI Models**: Google Gemini API (`gemini-3-flash-preview`, `gemini-3.8-flash`)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), TailwindCSS (CDN), FontAwesome 6, Prism.js
- **Audio APIs**: Web Speech API (`SpeechRecognition` & `SpeechSynthesis`)

---

## 📁 Directory Structure

```text
Voice_Assistant/
│
├── app.py                      # Flask application factory & database init
├── requirements.txt            # Python dependencies
├── .env.example                # Configuration template
├── .gitignore                  # Git ignore rules (protects .env, .venv, uploads)
├── README.md                   # Project documentation
│
├── models/                     # SQLAlchemy database models
│   ├── __init__.py
│   ├── user.py                 # User authentication model
│   ├── conversation.py         # Chat conversation model
│   ├── message.py              # Message model with tool metadata
│   └── document.py             # Document/code file attachment model
│
├── routes/                     # Modular Flask Blueprints
│   ├── __init__.py
│   ├── auth_routes.py          # /login, /register, /logout
│   ├── main_routes.py          # / (landing), /dashboard, /api/settings/apikey
│   ├── chat_routes.py          # /api/chat, /api/chat/conversations
│   └── document_routes.py      # /api/document/upload
│
├── services/                   # Core business logic & AI orchestration
│   ├── ai_service.py           # Gemini AI engine, intent routing & domain guard
│   ├── knowledge_service.py    # Curated programming definitions & CS engine
│   └── web_search_service.py   # Developer search fallback
│
├── tools/                      # Deterministic code & document engines
│   ├── code_tool.py            # High-performance code generators & patterns
│   └── document_tool.py        # Code and document parser
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base layout with navigation and scripts
│   ├── index.html              # High-conversion landing page
│   ├── login.html              # User login screen
│   ├── register.html           # User registration screen
│   └── dashboard.html          # Interactive AI voice assistant workspace
│
└── static/                     # Assets & frontend logic
    ├── css/style.css           # Glassmorphism dark/light theme styles
    ├── js/chat.js              # Real-time chat & API key settings modal
    └── js/voice.js             # Speech recognition & synthesis integration
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11 or higher installed
- WAMP Server or XAMPP (for MySQL, port 3306)
- Free Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

### 2. Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Voice_Assistant.git
   cd Voice_Assistant
   ```

2. **Create and activate a virtual environment:**
   - **Windows:**
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

### 3. Database & Environment Configuration

1. **Create the MySQL Database (WAMP Server):**
   - Make sure your WAMP Server is running (Green icon).
   - Open phpMyAdmin (`http://localhost/phpmyadmin`) or MySQL CLI and run:
     ```sql
     CREATE DATABASE IF NOT EXISTS voice_assistant_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     ```

2. **Configure your `.env` file:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and configure your credentials:
     ```env
     SECRET_KEY=your-secure-random-secret-key-2026

     # WAMP MySQL Database URL:
     DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/voice_assistant_db?charset=utf8mb4

     # Google Gemini Free API Key (from https://aistudio.google.com/app/apikey):
     GEMINI_API_KEY=your_actual_gemini_api_key_here
     ```

---

### 4. Running the Application

```bash
python app.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5001/
```

- **Landing Page**: `http://127.0.0.1:5001/`
- **Register**: `http://127.0.0.1:5001/register`
- **Login**: `http://127.0.0.1:5001/login`
- **Dashboard Workspace**: `http://127.0.0.1:5001/dashboard`

---

## 🧪 Testing

A complete automated test suite is provided to verify all end-to-end user journeys:

```bash
python scratch/test_e2e_developer_flow.py
```

**Verified Test Scenarios:**
- [x] Landing page rendering and responsive CTAs
- [x] Route protection (unauthenticated users safely redirected)
- [x] User registration with salted `scrypt` cryptographic password hash
- [x] User login, session persistence, and logout
- [x] Specialized programming queries (Theory & Code generation)
- [x] WAMP MySQL database persistence (Conversations, Messages, Users)
- [x] Code file upload & contextual codebase Q&A
- [x] Domain Focus Guard (intercepting non-technical topics)

---

## 🔒 Security Best Practices

1. **Secrets Isolation**: `.env` is ignored in `.gitignore` and never committed to version control.
2. **Password Security**: Passwords are cryptographically salted and hashed using `scrypt:32768:8:1` (via Werkzeug security).
3. **Protected APIs**: All chat, history, upload, and dashboard endpoints require `@login_required`.
4. **Defensive Validation**: Strict sanitization and defensive exception handling across all service layers.

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
