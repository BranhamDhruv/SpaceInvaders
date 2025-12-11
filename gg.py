import firebase_admin
from firebase_admin import credentials, firestore

print("Before cred")
cred = credentials.Certificate("space-invaders-f6406-firebase-adminsdk-fbsvc-ed36518219.json")
print("After cred, before init")
firebase_admin.initialize_app(cred)
print("After init, before client")
db = firestore.client()
print("After client, before query")
