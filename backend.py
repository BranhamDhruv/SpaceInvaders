import json
import os
import hashlib
import secrets
from datetime import datetime
from threading import Lock


class SpaceInvadersBackend:
    USERS_FILE = "Users.json"
    SCORES_FILE = "Scores.json"

    def __init__(self):
        # Locks to avoid race conditions if multiple requests hit at once
        self._user_lock = Lock()
        self._score_lock = Lock()
        self._ensure_files()

    # ---------- File helpers ----------

    def _ensure_files(self):
        """Create Users.json and Scores.json if they don't exist."""
        if not os.path.exists(self.USERS_FILE):
            with open(self.USERS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)  # { username: { ...user data... } }

        if not os.path.exists(self.SCORES_FILE):
            with open(self.SCORES_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)  # [ { username, score, timestamp }, ... ]

    def _load_users(self):
        with self._user_lock:
            with open(self.USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

    def _save_users(self, users):
        with self._user_lock:
            with open(self.USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=2)

    def _load_scores(self):
        with self._score_lock:
            with open(self.SCORES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

    def _save_scores(self, scores):
        with self._score_lock:
            with open(self.SCORES_FILE, "w", encoding="utf-8") as f:
                json.dump(scores, f, indent=2)

    # ---------- Password helpers ----------

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        pwd_salt = f"{password}{salt}".encode("utf-8")
        hashed = hashlib.sha256(pwd_salt).hexdigest()
        return hashed, salt

    # ---------- Public API ----------

    def sign_up(self, username, password):
        try:
            users = self._load_users()

            if username in users:
                return {"success": False, "message": "Username already exists"}

            hashed_pwd, salt = self._hash_password(password)

            users[username] = {
                "username": username,
                "password_hash": hashed_pwd,
                "salt": salt,
                "created_at": datetime.now().isoformat()
            }

            self._save_users(users)

            return {"success": True, "message": "Account created successfully"}

        except Exception as e:
            return {"success": False, "message": f"Error creating account: {str(e)}"}

    def login(self, username, password):
        try:
            users = self._load_users()

            if username not in users:
                return {"success": False, "message": "Invalid username or password"}

            user_data = users[username]
            hashed_pwd, _ = self._hash_password(password, user_data["salt"])

            if hashed_pwd == user_data["password_hash"]:
                return {
                    "success": True,
                    "message": "Login successful",
                    "username": username
                }
            else:
                return {"success": False, "message": "Invalid username or password"}

        except Exception as e:
            return {"success": False, "message": f"Error during login: {str(e)}"}

    def register_score(self, username, score):
        try:
            users = self._load_users()
            if username not in users:
                return {"success": False, "message": "User not found"}

            scores = self._load_scores()

            scores.append({
                "username": username,
                "score": int(score),
                "timestamp": datetime.now().isoformat()
            })

            self._save_scores(scores)

            return {"success": True, "message": "Score registered successfully"}

        except Exception as e:
            return {"success": False, "message": f"Error registering score: {str(e)}"}

    def get_leaderboard(self, limit=5):
        try:
            scores = self._load_scores()

            # Sort by score descending
            scores_sorted = sorted(scores, key=lambda s: s["score"], reverse=True)
            top_scores = scores_sorted[:limit]

            leaderboard = []
            for entry in top_scores:
                leaderboard.append({
                    "username": entry["username"],
                    "score": entry["score"],
                    "timestamp": entry["timestamp"]
                })

            return {"success": True, "leaderboard": leaderboard}

        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching leaderboard: {str(e)}",
                "leaderboard": []
            }


if __name__ == "__main__":
    backend = SpaceInvadersBackend()

    result = backend.sign_up("player1", "mypassword123")
    print("Sign Up:", result)

    result = backend.login("player1", "mypassword123")
    print("Login:", result)

    result = backend.register_score("player1", 15000)
    print("Register Score:", result)

    result = backend.get_leaderboard()
    print("Leaderboard:", result)
