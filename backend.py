import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import secrets
from datetime import datetime

# Embed credentials directly
firebase_config = {
  "type": "service_account",
  "project_id": "space-invaders-f6406",
  "private_key_id": "ed3651821990d62fe8aec5ed216984d663ca75de",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDYP4H+Oa8tuYNl\n+CIhVGQr61xNiyJiBTnn+j/y7NRorhZbwRzbEy1twTpgGqyJjBzzGZSXE+xxSmRx\nG7vo5pYE030AypfjzIQzr2tS8VFl+nEdhiNVdJCmRx6tGTwoihUnf7jQQJMDoWHx\n409J3plRUTvU/u4e2lZlSEitY9GmL+KwUe1uvsGH8laL+JonrKMEtxFg9VDHNu8J\nMoVtlihcyWZ/SBAWpbtNfvzrHuHhcs+eXtVESVaZt40YqRkmgRLNHhhNLeB5ePU2\n+ysd1o2TVYiXHRglmpiJCHzkGrZf03N95cG94vJwoo9llpWgnqXB1oMMwUEpyRY6\ngb1xxE6rAgMBAAECggEAALJNLnMxb+WB/BP8B7mBX1wjTD1Jx3Cp8z51a5EYrkIs\nF/BRZcyI4N5t3CLJbOG3kL9dlnMW5aZMgBYquh9qfXgVc3jgi9IlnvdfrE7S/dv1\nO8vQDHTYQAupn06CT7AyKm+Jod/quG/JVOsj90NEOU++ermFhz/pNbQjkpjMhKiq\nR9ujY44MYij3Yel14qSOa7TDtcgUhtfYLd9B3KtgJxwcQQ8dDl9tCxyPgU6g1Hc0\nUOIpgPG+to7xSVnD+dNd83Iy9y2zRYZJpC9wj01Uga20Y/SFV8SeY7KVtwCZjmHT\nYaMNG4BXHi7uS9GrDGV+4qlxFl+XSpyI+sseaQ4G8QKBgQD0XmxY1LZlNVqtoVvp\nWAIMA5nxTNts+yhfm21h1sm3hTk9h+39xCrkKrri/JQkwERmDLd/1PyhvpUmXemr\nA5hiaRqxow7vCfHbK9wst92xK0ceFHS69kTk7vNLAs9fsaHNdXLVnBnFVjQgyLDv\nREOEYJr3SBTa40wDv65MJMSofwKBgQDiinCOkNDon8FA3Hp0HHzq/gmThIYDQlSU\nsHgreq53qUneH8fe9WTuaYX99+LP7c7/MdHN1QmZJp1gq6OqBtxffZhfKMGRjFE9\n/CyUBH3Hx0BJbGCk0Onue1XCimCfcBMO2tIxFVggRkuhOzHjtZMif/mz+3FpTsMw\niFenPYVj1QKBgHt3GZboIh+QjXgchqum46HeT/Eyu8qcOxHTHbjJJLGshfcorn4A\nlwsg67uzkcXfvq8wzaWwntO5zvHLkTvuXRebsvj9QZZUl/X8ewm8/C1/iDcSbsfn\nlXd1o0bK7KuUvANqy9JRRFQH8d5+h6bb/qDrjmBR8veEz+s09YNTMGlRAoGAIV/R\n2z78d/jpKJwSsj5sLNaGJKR2dc501X72BTnKsDhReJboBDHUz8beBZ9aW9WmFDSL\nuy4yfsyQjOhccTUXjD3dj89aTQ4F/gLDsn7C5Qa2stpzlnRsskSbStDGEVcah6q3\nIqIJXJ/ejn9BB1H9vixqZhiaCbCf0uuTNkE7AI0CgYAJlLuw10UWonjLa9UBt4WZ\nT0UrvXCdcA+dO5CFZ1o6jtTKR5OIKlNMomjVmKvuuLYMbJ+3LaVkGNEcbL+DJk5S\n2k+XEh++1GH6GvSoRzMKPQwM0flXEHf0J08KInH9BfoJY+oYMU2XRg+vdfuRaUVN\nkldrVqS6faMVeJhOACqgXg==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@space-invaders-f6406.iam.gserviceaccount.com",
  "client_id": "110276854241053568275",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40space-invaders-f6406.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)


class SpaceInvadersBackend:
    def __init__(self):
        self.db = firestore.client()
        self.users_collection = self.db.collection('Users')
        self.scores_collection = self.db.collection('Scores')

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        pwd_salt = f"{password}{salt}".encode('utf-8')
        hashed = hashlib.sha256(pwd_salt).hexdigest()
        return hashed, salt

    def sign_up(self, username, password):
        try:
            user_doc = self.users_collection.document(username).get()
            if user_doc.exists:
                return {'success': False, 'message': 'Username already exists'}

            hashed_pwd, salt = self._hash_password(password)

            self.users_collection.document(username).set({
                'username': username,
                'password_hash': hashed_pwd,
                'salt': salt,
                'created_at': datetime.now()
            })

            return {'success': True, 'message': 'Account created successfully'}

        except Exception as e:
            return {'success': False, 'message': f'Error creating account: {str(e)}'}

    def login(self, username, password):
        try:
            user_doc = self.users_collection.document(username).get()

            if not user_doc.exists:
                return {'success': False, 'message': 'Invalid username or password'}

            user_data = user_doc.to_dict()
            hashed_pwd, _ = self._hash_password(password, user_data['salt'])

            if hashed_pwd == user_data['password_hash']:
                return {'success': True, 'message': 'Login successful', 'username': username}
            else:
                return {'success': False, 'message': 'Invalid username or password'}

        except Exception as e:
            return {'success': False, 'message': f'Error during login: {str(e)}'}

    def register_score(self, username, score):
        try:
            user_doc = self.users_collection.document(username).get()
            if not user_doc.exists:
                return {'success': False, 'message': 'User not found'}

            self.scores_collection.add({
                'username': username,
                'score': int(score),
                'timestamp': datetime.now()
            })

            return {'success': True, 'message': 'Score registered successfully'}

        except Exception as e:
            return {'success': False, 'message': f'Error registering score: {str(e)}'}

    def get_leaderboard(self):
        try:
            scores_query = self.scores_collection.order_by(
                'score', direction=firestore.Query.DESCENDING
            ).limit(5)

            scores = scores_query.stream()

            leaderboard = []
            for doc in scores:
                score_data = doc.to_dict()
                leaderboard.append({
                    'username': score_data['username'],
                    'score': score_data['score'],
                    'timestamp': score_data['timestamp']
                })

            return {'success': True, 'leaderboard': leaderboard}

        except Exception as e:
            return {'success': False, 'message': f'Error fetching leaderboard: {str(e)}', 'leaderboard': []}


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