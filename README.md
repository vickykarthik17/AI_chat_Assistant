# Sadhana Mythri Support Chat Widget

> A responsive support chat for Sadhana Mythri, powered by Google Gemini and the We-Hive support knowledge base.

[![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB?logo=react&logoColor=20232a)](https://github.com/vickykarthik17/AI_chat_Assistant/tree/main/src)
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://github.com/vickykarthik17/AI_chat_Assistant/tree/main/backend)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)

This repository provides a reusable React support-chat widget and its FastAPI support API, Gemini integration, and curated knowledge base. The widget is bundled as an installable package; it does not require a separate widget server or iframe when used in the Sadhana Mythri app.

## Highlights

- Ask common support questions or enter a free-text question.
- Answer supported We-Hive FAQs locally or use relevant knowledge-base articles with Gemini.
- Stream only completed Gemini responses to the chat.
- Keep support responses grounded in approved We-Hive information.
- Use the responsive support chat on desktop and mobile.
- Run locally or with Docker Compose.

## Stack

| Layer | Technology |
| --- | --- |
| Frontend | React 18, JavaScript/JSX, Vite, Tailwind CSS |
| Content | React Markdown, Remark GFM |
| Backend | Python 3.12, FastAPI, Uvicorn, Pydantic |
| AI | Google Gemini API |
| Storage | SQLite |
| Deployment | Docker, Docker Compose, Nginx |

## Quick Start

The repository includes a standalone preview app and the reusable widget package. Run the support API and preview app in separate terminals.

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
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root. It is ignored by Git and must never be committed. Keep the Gemini API key private and configure it only for the backend.

```dotenv
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.6-flash
GEMINI_MAX_OUTPUT_TOKENS=4096
GEMINI_MAX_HISTORY_MESSAGES=40
SESSION_COOKIE_SECURE=false
CORS_ORIGINS=http://localhost:5173,http://localhost:5175
```

`GEMINI_MODEL`, `GEMINI_MAX_OUTPUT_TOKENS`, and `GEMINI_MAX_HISTORY_MESSAGES` are optional. The history limit defaults to 40 recent messages, bounding the conversation context sent to Gemini in long chats. New accounts can sign up with an email address and a password of at least 12 characters; there is no shared workspace password. Passwords are salted and hashed, and random session tokens expire after 12 hours and are stored as hashes in SQLite. Email verification and password recovery are not currently implemented. `SESSION_COOKIE_SECURE=false` is for local HTTP development only; set it to `true` behind HTTPS in production.

The database schema is created automatically at backend startup. Existing SQLite conversation data is not migrated automatically; it remains in the old database file and is not used by this version.

### 4. Start the support API

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --port 8001
```

### 5. Start the widget preview

In a second terminal, from the `project` folder:

```powershell
npm run dev
```

Open [http://localhost:5175](http://localhost:5175) for the full-screen preview or [http://localhost:5175/widget](http://localhost:5175/widget) for the compact widget preview.

### Install the widget in Sadhana Mythri

After pushing this repository to GitHub, install the widget package from the Sadhana Mythri frontend:

```powershell
npm install git+https://github.com/vickykarthik17/AI_chat_Assistant.git
```

The package build runs automatically during installation. In the Sadhana Mythri React app, import the component and its stylesheet:

```jsx
import { SupportChatWidget } from "ai-chat-assistant/widget";
import "ai-chat-assistant/widget.css";

// Mount once near the application router.
<SupportChatWidget apiUrl="/support-api" />
```

Keep the existing launcher and open the chat with:

```js
window.dispatchEvent(new Event("sadhana-support-widget:open"));
```

In the Sadhana Mythri Vite config, proxy `/support-api` to the support backend at `http://localhost:8001`, rewriting the prefix to `/api`. For production, set `VITE_SUPPORT_API_URL` to the support API's HTTPS base URL ending in `/api`, then allow the website origin in this backend's `CORS_ORIGINS`. Never put the Gemini API key in frontend code.

The widget also accepts `title`, `initialOpen`, `showLauncher`, and `mode="standalone"` props. The default `apiUrl` is `/api`.

### Support behavior

The widget offers starter questions for plans, getting started, and contacting support, while keeping free-text questions available. Changing or packaging the UI does not modify or retrain the model: the same support endpoint, curated knowledge base, Gemini instructions, and answer restrictions remain in effect. A curated backend knowledge base covers public We-Hive pages and workflows, including the home page, plans, FAQ, platform documentation, onboarding, KYC, payments, subscriptions, policies, careers, company details, and support. Its facts were reviewed against the live public pages on October 29, 2026; they are concise summaries, not a word-for-word copy or a live website crawl. Update the relevant articles and source URLs when the site changes. The backend ranks relevant articles and sends at most three to Gemini; common FAQs and broad overview questions are answered locally without a Gemini network round-trip. This supplies reference information at request time—it does not train or fine-tune Gemini. The knowledge base excludes private account records, uploaded ID documents, and administrator-only information. For Gemini answers, the backend buffers generated text and sends it to the chat only after Gemini confirms completion, so timeouts or incomplete streams never display a partial answer. The configured output-token limit applies, with a 60-second total timeout and bounded network timeouts to prevent requests from waiting indefinitely. The chat releases the input after the final completion or error event. The support endpoint does not store messages in SQLite. It refuses questions with no matching We-Hive information and instructs Gemini not to invent facts; this is a safeguard, not a guarantee against every off-topic answer. Local FAQ answers avoid Gemini network latency altogether.

The widget package is in `src/components/SupportChatWidget.jsx`; its public API is exported by `src/widget-entry.jsx`. Support data and Gemini instructions remain in `backend/support_knowledge.py` and `backend/main.py`.

## Docker

Create the root `.env` file with `GEMINI_API_KEY` and any optional settings. For local Docker over plain HTTP, set `SESSION_COOKIE_SECURE=false`; use `true` behind HTTPS in production. Then run:

```powershell
docker compose up --build
```

The application is available at [http://localhost:5173](http://localhost:5173). Accounts and conversations are persisted in the backend's SQLite database.

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

Authentication endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/auth/status` | Check whether the browser has an active session |
| `POST` | `/api/auth/register` | Create an account and sign in |
| `POST` | `/api/auth/login` | Sign in to an account |
| `POST` | `/api/auth/logout` | Clear the browser session |

Authenticated conversation endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/sessions` | List conversations |
| `POST` | `/api/sessions` | Create a conversation |
| `GET` | `/api/sessions/{id}` | Read a conversation and its messages |
| `PATCH` | `/api/sessions/{id}` | Rename a conversation |
| `DELETE` | `/api/sessions/{id}` | Delete a conversation |
| `POST` | `/api/sessions/{id}/chat` | Stream a Gemini response |
| `POST` | `/api/support/chat` | Answer supported We-Hive questions with Gemini |

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
python -m unittest discover -s backend -p "test_*.py"
```

## Project Structure

```text
src/                 React application and chat UI
backend/main.py      FastAPI API and Gemini streaming integration
backend/support_knowledge.py
                     Curated We-Hive articles and FAQ retrieval
SQLite               Accounts, conversations, and messages
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
