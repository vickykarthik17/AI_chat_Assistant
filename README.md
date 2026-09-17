# AI Chat Assistant

> A full-stack conversational AI application that uses Google Gemini to generate contextual, natural-language responses through a responsive React chat interface.

[![Build Status](https://img.shields.io/badge/build-[Build%20Status]-informational)]([Insert CI URL])
[![License](https://img.shields.io/badge/license-[License]-lightgrey)]([Insert License URL])
[![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB)]([Insert Project URL])
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)]([Insert Project URL])

[Insert Image Here]

## Table of Contents

- [About The Project](#about-the-project)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## About The Project

AI Chat Assistant provides a practical interface for asking questions and continuing multi-turn conversations with an AI model. The project separates the user experience from model access: the React frontend manages conversations and streaming UI updates, while the FastAPI backend maintains session state and communicates with the Google Gemini API.

This architecture makes the application easy to run locally and gives developers a clear foundation for adding authentication, durable storage, model configuration, observability, and production deployment later.

### Technology Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, React Markdown, Remark GFM
- **Backend:** Python 3.12, FastAPI, Uvicorn, Pydantic, HTTPX
- **AI provider:** Google Gemini API
- **Communication:** REST APIs with Server-Sent Events (SSE) for streamed assistant responses
- **Deployment tooling:** Docker, Docker Compose, Nginx

## Features

- Real-time AI conversations powered by the Google Gemini API
- Context-aware responses across multi-turn conversations
- Full-stack chat application with a React frontend and FastAPI backend
- REST API integration between the frontend and AI backend
- Incremental streaming of assistant responses using Server-Sent Events
- Create, select, rename, and delete conversations
- In-memory session history for quick local development
- Markdown and GitHub Flavored Markdown rendering for assistant messages
- Stop an in-progress response from the chat interface
- Responsive layout for desktop and mobile screens
- Health-check endpoint for confirming backend availability

## Getting Started

### Prerequisites

Install the following before starting:

- **Node.js 20 or later** and npm
- **Python 3.12 or later**
- **A Google Gemini API key** with access to the configured model
- **Git**
- **Docker Desktop** (optional, for containerized development)

The default Gemini model is `gemini-3.6-flash`. Set `GEMINI_MODEL` if your API key uses a different available model.

### Installation

1. Clone the repository and enter the project directory:

   ```powershell
   git clone [Insert Repository URL]
   cd project
   ```

2. Install the frontend dependencies:

   ```powershell
   npm ci
   ```

3. Create a Python virtual environment and install the backend dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r backend\requirements.txt
   ```

   On macOS or Linux, activate the environment with:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

4. Create a `.env` file in the project root. Do not commit this file or expose the API key in frontend code.

   ```dotenv
   GEMINI_API_KEY=[Insert Google Gemini API key]
   GEMINI_MODEL=gemini-3.6-flash
   API_BEARER_TOKEN=[Long random shared API token]
   VITE_API_TOKEN=[Same token for this trusted deployment]
   DATABASE_PATH=./data/chat.db
   CORS_ORIGINS=http://localhost:5173
   ```

   `GEMINI_MODEL` is optional and defaults to `gemini-3.6-flash`. `API_BEARER_TOKEN` protects the API, and `VITE_API_TOKEN` is embedded in the frontend bundle to send that token. This shared-token mode is appropriate for trusted internal deployments only; it is not per-user authentication.

   Generate a strong token with:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   Rotate the Gemini key in Google AI Studio or Google Cloud, revoke the old key, and place only the replacement in `.env`. Never commit `.env` or expose the Gemini key to the frontend.

5. Start the backend in one terminal:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

6. Start the frontend in a second terminal from the project root:

   ```powershell
   cd [Path to project]
   npm run dev
   ```

   Open [http://localhost:5173](http://localhost:5173) in your browser. Vite proxies `/api` requests to `http://localhost:8001` by default.

   To use a different backend URL, set `VITE_API_TARGET` before starting Vite:

   ```powershell
   $env:VITE_API_TARGET = "http://localhost:8001"
   npm run dev
   ```

### Optional Docker Setup

The repository includes Dockerfiles and a Compose configuration. Create a root `.env` file with the Gemini settings, then build the images with:

```powershell
GEMINI_API_KEY=[Insert Google Gemini API key]
GEMINI_MODEL=gemini-3.6-flash
API_BEARER_TOKEN=[Long random shared API token]
VITE_API_TOKEN=[Same token for this trusted deployment]
DATABASE_PATH=/app/data/chat.db
CORS_ORIGINS=http://localhost:5173
```

```powershell
docker compose up --build
```

The frontend is exposed at [http://localhost:5173](http://localhost:5173). The backend is available to the frontend through the internal Compose network and is not published directly to the host.

For a deployed frontend origin, set `CORS_ORIGINS` to a comma-separated list of trusted origins. The backend container includes a healthcheck, and the frontend's Nginx configuration proxies `/api` requests to it.

## Usage

### Chat Through The Web Interface

1. Start the backend and frontend using the installation steps above.
2. Open the frontend in a browser.
3. Create a conversation or send a message from the empty chat screen.
4. Continue sending messages to preserve context within the active session.
5. Use the stop control to cancel a streamed response.

Press `Enter` to send a message. Press `Shift+Enter` to add a new line.

### Check Backend Health

Use the health endpoint to confirm that the FastAPI service is running:

```powershell
Invoke-RestMethod http://localhost:8001/api/health
```

Expected response:

```json
{
  "status": "ok"
}
```

### Use The REST API

Create a session:

```powershell
$headers = @{ Authorization = "Bearer $env:API_BEARER_TOKEN" }
$session = Invoke-RestMethod `
  -Uri http://localhost:8001/api/sessions `
  -Method Post `
   -Headers $headers `
  -ContentType "application/json" `
  -Body '{"title":"Gemini API Notes"}'

$session
```

List sessions:

```powershell
Invoke-RestMethod http://localhost:8001/api/sessions -Headers $headers
```

Retrieve a session and its messages:

```powershell
Invoke-RestMethod "http://localhost:8001/api/sessions/$($session.id)" -Headers $headers
```

Send a message and receive a streamed SSE response:

```powershell
Invoke-WebRequest `
  -Uri "http://localhost:8001/api/sessions/$($session.id)/chat" `
  -Method Post `
   -Headers $headers `
  -ContentType "application/json" `
  -Body '{"message":"Explain REST APIs in simple terms."}'
```

The chat endpoint returns events in this format:

```text
data: {"text":"Partial response"}

data: {"stop":true}
```

Errors are returned as SSE events with an `error` property. Authenticated session data is stored in SQLite. The Docker deployment persists it in the named `chat_data` volume. API requests are limited to 60 per minute per client, and chat requests are limited to 10 per minute per client.

### Development Commands

Run the frontend linter, type checker, production build, or local preview with:

```powershell
npm run lint
npm run typecheck
npm run build
npm run preview
```

## Roadmap

- [x] Persist sessions and messages in SQLite
- [x] Add shared bearer-token protection
- [x] Add baseline per-client rate limits
- [x] Restrict CORS origins for deployed environments
- [ ] Replace shared-token access with per-user authentication and session ownership
- [ ] Move rate limiting to Redis for multi-instance deployments
- [ ] Add automated frontend and backend tests
- [ ] Add configurable Gemini generation settings
- [ ] Improve structured error handling and request validation
- [ ] Add observability and request tracing
- [ ] Add clickable suggested prompts and richer conversation management

## Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch:

   ```powershell
   git checkout -b feature/[short-description]
   ```

3. Install dependencies and make your changes.
4. Run the available checks:

   ```powershell
   npm run lint
   npm run typecheck
   npm run build
   ```

5. Review your changes and commit them:

   ```powershell
   git add .
   git commit -m "Describe your change"
   ```

6. Push the branch and open a pull request:

   ```powershell
   git push origin feature/[short-description]
   ```

Please include a clear description of the change, steps to reproduce or verify it, and screenshots for user-interface changes. Never include API keys or other secrets in commits or pull requests.

## License

This project is currently distributed under **[Insert License Name]**.

Add the complete license text to a `LICENSE` file and update this section with the chosen license and copyright holder:

```text
[Insert license notice and copyright holder]
```

## Contact

**[Your Name]**

- GitHub: [Insert GitHub profile URL]
- Twitter/X: [Insert Twitter/X profile URL]
- Portfolio: [Insert portfolio URL]
- Project repository: [Insert repository URL]

For bugs and feature requests, open an issue at [Insert Issues URL].
