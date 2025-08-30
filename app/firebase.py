import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

def initialize_firebase():
    # Check if the app is already initialized to prevent errors
    if not firebase_admin._apps:
        cred = None

        # 1. Try to get the service account key from an environment variable (best for deployment)
        service_account_key_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
        if service_account_key_json:
            try:
                cred_dict = json.loads(service_account_key_json)
                cred = credentials.Certificate(cred_dict)
            except json.JSONDecodeError as e:
                raise ValueError("The FIREBASE_SERVICE_ACCOUNT_KEY environment variable is not valid JSON.") from e
            except Exception as e:
                raise ValueError(f"Error initializing Firebase from environment variable: {e}") from e


        # 2. Try to load from a local file (good for local development)
        elif os.path.exists('serviceAccountKey.json'):
            cred = credentials.Certificate('serviceAccountKey.json')

        # 3. Fallback to Application Default Credentials (for Google Cloud environments)
        else:
            try:
                cred = credentials.ApplicationDefault()
            except Exception:
                raise RuntimeError(
                    "Firebase credentials not found. "
                    "Please set the FIREBASE_SERVICE_ACCOUNT_KEY environment variable, "
                    "provide a 'serviceAccountKey.json' file, or set up Application Default Credentials."
                )

        # Initialize the Firebase app
        firebase_admin.initialize_app(cred)

    return firestore.client()


def get_db():
    """Returns a Firestore database client instance."""
    return initialize_firebase()