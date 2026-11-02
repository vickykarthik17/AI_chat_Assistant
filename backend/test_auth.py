import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import main


class SqliteTestConnection:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        return self.connection.execute(query.replace("%s", "?"), params)


class AuthenticationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_directory.name) / "test.db"
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE auth_sessions (
                token_hash TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                expires_at INTEGER NOT NULL
            );
            """
        )
        connection.commit()
        connection.close()
        self.database_path = database_path
        @contextmanager
        def test_connection():
            connection = sqlite3.connect(self.database_path, timeout=10)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            adapter = SqliteTestConnection(connection)
            try:
                yield adapter
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                connection.close()

        self.connection_factory = test_connection
        self.connection_patch = patch.object(main, "get_connection", self.connection_factory)
        self.connection_patch.start()
        self.schema_patch = patch.object(main, "initialize_database")
        self.schema_patch.start()
        main.rate_windows.clear()
        self.client = TestClient(main.app)
        self.client.__enter__()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)
        self.schema_patch.stop()
        self.connection_patch.stop()
        main.rate_windows.clear()
        self.temp_directory.cleanup()

    def create_account(self, email: str = "owner@example.com") -> None:
        response = self.client.post(
            "/api/auth/register",
            json={"email": email, "password": "test-owner-password"},
        )
        self.assertEqual(response.status_code, 201, response.text)

    def test_conversation_routes_require_an_account(self) -> None:
        response = self.client.get("/api/sessions")

        self.assertEqual(response.status_code, 401)

    def test_registration_login_cookie_and_logout(self) -> None:
        response = self.client.post(
            "/api/auth/register",
            json={"email": "owner@example.com", "password": "test-owner-password"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user"]["email"], "owner@example.com")
        copied_cookie = self.client.cookies.get(main.SESSION_COOKIE_NAME)
        cookie = response.headers["set-cookie"].lower()
        self.assertIn("httponly", cookie)
        self.assertIn("samesite=strict", cookie)
        self.assertTrue(self.client.get("/api/auth/status").json()["authenticated"])
        self.assertEqual(self.client.get("/api/sessions").status_code, 200)

        self.client.post("/api/auth/logout")
        self.assertEqual(self.client.get("/api/sessions").status_code, 401)
        replay_response = self.client.get(
            "/api/sessions",
            headers={"Cookie": f"{main.SESSION_COOKIE_NAME}={copied_cookie}"},
        )
        self.assertEqual(replay_response.status_code, 401)

        login_response = self.client.post(
            "/api/auth/login",
            json={"email": "OWNER@example.com", "password": "test-owner-password"},
        )
        self.assertEqual(login_response.status_code, 200)

    def test_duplicate_email_and_incorrect_password_are_rejected(self) -> None:
        self.create_account()
        duplicate = self.client.post(
            "/api/auth/register",
            json={"email": "OWNER@example.com", "password": "another-valid-password"},
        )
        self.assertEqual(duplicate.status_code, 409)

        self.client.post("/api/auth/logout")
        response = self.client.post(
            "/api/auth/login",
            json={"email": "owner@example.com", "password": "short"},
        )
        self.assertEqual(response.status_code, 422)

        response = self.client.post(
            "/api/auth/login",
            json={"email": "owner@example.com", "password": "incorrect-password-long"},
        )
        self.assertEqual(response.status_code, 401)

    def test_conversations_are_isolated_between_accounts(self) -> None:
        self.create_account()
        owner_session = self.client.post(
            "/api/sessions", json={"title": "Private chat"}
        ).json()
        self.client.post("/api/auth/logout")
        self.create_account("another@example.com")

        self.assertEqual(self.client.get("/api/sessions").json(), [])
        self.assertEqual(
            self.client.get(f"/api/sessions/{owner_session['id']}").status_code, 404
        )
        self.assertEqual(
            self.client.delete(f"/api/sessions/{owner_session['id']}").status_code, 404
        )
        self.assertEqual(
            self.client.patch(
                f"/api/sessions/{owner_session['id']}", json={"title": "Taken over"}
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                f"/api/sessions/{owner_session['id']}/messages",
                json={"role": "user", "content": "Not mine"},
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                f"/api/sessions/{owner_session['id']}/chat",
                json={"message": "Not mine"},
            ).status_code,
            404,
        )

    def test_authentication_attempts_are_rate_limited(self) -> None:
        for _ in range(5):
            self.client.post(
                "/api/auth/login",
                json={
                    "email": "missing@example.com",
                    "password": "incorrect-password-long",
                },
            )

        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "missing@example.com",
                "password": "incorrect-password-long",
            },
        )

        self.assertEqual(response.status_code, 429)

    def test_recent_chat_history_is_bounded_and_starts_with_user(self) -> None:
        self.create_account()
        session = self.client.post("/api/sessions", json={"title": "Long chat"}).json()
        message_count = 2 * main.GEMINI_MAX_HISTORY_MESSAGES + 1
        with self.connection_factory() as connection:
            for index in range(message_count):
                connection.execute(
                    "INSERT INTO messages (session_id, role, content, created_at) "
                    "VALUES (%s, %s, %s, %s)",
                    (
                        session["id"],
                        "user" if index % 2 == 0 else "assistant",
                        f"message-{index}",
                        main.now_iso(),
                    ),
                )
            history = main.load_recent_history(connection, session["id"])
        self.assertLessEqual(len(history), main.GEMINI_MAX_HISTORY_MESSAGES)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[-1]["content"], f"message-{message_count - 1}")


if __name__ == "__main__":
    unittest.main()
