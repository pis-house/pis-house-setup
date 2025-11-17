import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

SERVICE_ACCOUNT_KEY_PATH = '/Users/tanakawatarudai/python_gui/pis-house-3612e-firebase-adminsdk-fbsvc-c8fa206f3b.json'

cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection('tests').add({
    'first': 'Ada',
    'last': 'Lovelace',
    'born': 1815
})

print(f"追加されたドキュメントID: {doc_ref[1].id}")