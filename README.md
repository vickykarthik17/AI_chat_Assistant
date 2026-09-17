# AI Chat Assistant

> A fast, full-stack conversational AI workspace powered by Google Gemini, with streamed responses, persistent conversations, and a clean responsive interface.

[![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB?logo=react&logoColor=20232a)](https://github.com/vickykarthik17/AI_chat_Assistant/tree/main/src)
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://github.com/vickykarthik17/AI_chat_Assistant/tree/main/backend)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)

AI Chat Assistant keeps the conversation experience simple while giving the application a solid full-stack foundation. The React client handles the chat experience and live token updates; the FastAPI service manages sessions, SQLite persistence, authentication, and Gemini communication.

## Highlights

- Stream Gemini responses progressively over Server-Sent Events.
- Create, select, rename, and delete conversations.
- Preserve conversation history in SQLite.
- Render Markdown and GitHub Flavored Markdown in assistant messages.
- Stop an in-progress response at any time.
- Use the responsive layout on desktop and mobile.
- Protect API routes with a shared bearer token for trusted deployments.
- Run locally or with Docker Compose.

## Stack

| Layer | Technology |
| --- | --- |
| Frontend | React 18, JavaScript/JSX, Vite, Tailwind CSS |
| Content | React Markdown, Remark GFM |
| Backend | Python 3.12, FastAPI, Uvicorn, Pydantic |
| AI | Google Gemini API |
| Storage | SQLite with WAL mode |
| Deployment | Docker, Docker Compose, Nginx |

## Quick Start

### Prerequisites

- Node.js 20 or later
- Python 3.12 or later
- A Google Gemini API key

### 1. Install frontend dependencies

```powershell
npm ci
```

### 2. Install backend dependencies

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root. It is ignored by Git and must never be committed.

```dotenv
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.6-flash
GEMINI_MAX_OUTPUT_TOKENS=4096
API_BEARER_TOKEN=your-long-random-token
VITE_API_TOKEN=your-long-random-token
DATABASE_PATH=./data/chat.db
CORS_ORIGINS=http://localhost:5173
```

`GEMINI_MODEL` and `GEMINI_MAX_OUTPUT_TOKENS` are optional. `VITE_API_TOKEN` is included in the frontend bundle, so this shared-token mode is intended for trusted internal deployments rather than user authentication.

Generate a token with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Start the backend

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 5. Start the frontend

Open a second terminal from the project root:

```powershell
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api` requests to the backend at `http://localhost:8001`.

## Docker

Create the root `.env` file with the Gemini and authentication settings, then run:

```powershell
docker compose up --build
```

The application is available at [http://localhost:5173](http://localhost:5173). Conversation data is persisted in the Docker `chat_data` volume.

## API

Check backend health:

```powershell
Invoke-RestMethod http://localhost:8001/api/health
```

Expected response:

```json
{
  "status": "ok"
}
```

Authenticated session endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/sessions` | List conversations |
| `POST` | `/api/sessions` | Create a conversation |
| `GET` | `/api/sessions/{id}` | Read a conversation and its messages |
| `PATCH` | `/api/sessions/{id}` | Rename a conversation |
| `DELETE` | `/api/sessions/{id}` | Delete a conversation |
| `POST` | `/api/sessions/{id}/chat` | Stream a Gemini response |

The chat endpoint returns SSE events such as:

```text
data: {"text":"Partial response"}

data: {"stop":true}
```

## Development Commands

```powershell
npm run lint
npm run build
npm run preview
```

## Project Structure

```text
src/                 React application and chat UI
backend/main.py      FastAPI API and Gemini streaming integration
data/                Local SQLite data directory
docker-compose.yml   Local container orchestration
nginx.conf           Production frontend routing and API proxy
```

## Contributing

1. Create a feature branch.
2. Make the change and keep secrets out of commits.
3. Run `npm run lint` and `npm run build`.
4. Open an issue or pull request with reproduction steps and verification details.

For bugs and feature requests, open an issue at [GitHub Issues](https://github.com/vickykarthik17/AI_chat_Assistant/issues).

## Contact

**Vikram Karthik**

- GitHub: [vickykarthik17](https://github.com/vickykarthik17)
- Portfolio: [my-portfolio-tan-delta-72.vercel.app](https://my-portfolio-tan-delta-72.vercel.app/)
- Repository: [AI_chat_Assistant](https://github.com/vickykarthik17/AI_chat_Assistant)
