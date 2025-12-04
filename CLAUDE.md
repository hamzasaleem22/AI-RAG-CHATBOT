# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## High-Level Code Architecture and Structure

### RAG Chatbot System (`starting-ragchatbot-codebase/`)
*   **Purpose**: A full-stack Retrieval-Augmented Generation (RAG) system designed to answer questions about course materials using semantic search and AI-powered responses.
*   **Technologies**: Python (backend), FastAPI, Uvicorn, ChromaDB (vector storage), Anthropic's Claude (AI generation). The frontend is a static web interface.
*   **Backend (`backend/`)**:
    *   Built with FastAPI, defining API endpoints in `app.py`.
    *   Key modules include `document_processor.py` for handling course materials, `vector_store.py` for ChromaDB interactions and vector embeddings, `rag_system.py` for orchestrating retrieval and generation, `ai_generator.py` for interfacing with Anthropic Claude, `session_manager.py` for session management, `search_tools.py` for search functionalities, `models.py` for data models, and `config.py` for configuration.
*   **Frontend (`frontend/`)**:
    *   A static web interface comprising `index.html` (main page), `script.js` (JavaScript logic for interacting with the backend API), and `style.css` (styling).
    *   The frontend is served directly by the backend at `http://localhost:8000`.

## Commonly Used Commands

### RAG Chatbot System (`starting-ragchatbot-codebase/`)
*   **Install Dependencies**: Navigate to the `starting-ragchatbot-codebase/` directory and run `uv sync`.
*   **Run Application (Quick Start)**: Navigate to the `starting-ragchatbot-codebase/` directory and run `chmod +x run.sh && ./run.sh`. This script will start the backend server and serve the frontend.
*   **Run Backend Only (Manual Start)**: Navigate to the `starting-ragchatbot-codebase/backend/` directory and run `uv run uvicorn app:app --reload --port 8000`.
*   **Linting**: No explicit linting commands are currently defined in `pyproject.toml` or `run.sh`.
*   **Testing**: No explicit testing commands are currently defined in `pyproject.toml` or `run.sh`.

## Flow Diagram: Frontend to Backend Query Handling

```
[User Action on Frontend]
      ↓
[Frontend Application]
  - Captures user input/event
  - Constructs API request (HTTP/HTTPS)
    - Request Method (GET, POST, etc.)
    - Headers (Content-Type, Authorization)
    - Body (JSON data)
      ↓
[Network / Internet]
      ↓
[Backend Infrastructure]
  ┌─────────────────────────┐
  │   [Load Balancer]       │ (Optional, distributes requests)
  └─────────────────────────┘
      ↓
  ┌─────────────────────────┐
  │      [Web Server]       │ (e.g., Nginx, Apache)
  │    - Routes request     │
  └─────────────────────────┘
      ↓
  ┌─────────────────────────┐
  │ [Application Server]    │ (e.g., Node.js, Django, Spring)
  │    - **Routing**        │ (Matches URL to handler)
  │    - **Controller/Handler**
  │      - Parses request   │
  │      - Validates input  │
  │      - Authenticates/Authorizes
  │      - Invokes Business Logic
  │        ↓
  │      [Business Logic]   │ (Performs core tasks)
  │        ↓
  │   ┌────────────────────┐
  │   │     [Database]     │ (Query, store, update data)
  │   └────────────────────┘
  │        ↓
  │      [Error Handling]   │ (If issues occur)
  └─────────────────────────┘
      ↓
[Backend Application]
  - Constructs API response
    - HTTP Status Code (200, 400, 500, etc.)
    - Headers
    - Body (JSON data)
      ↓
[Network / Internet]
      ↓
[Frontend Application]
  - Receives API response
  - Checks HTTP Status Code
  - Parses Response Body
  - **Updates UI** (Displays data, shows messages)
  - **Handles Errors** (Displays error messages)
      ↓
[User sees updated Frontend]
```