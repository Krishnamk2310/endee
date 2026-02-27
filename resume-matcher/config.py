import os

# endee config
ENDEE_HOST = os.getenv("ENDEE_HOST", "http://localhost:8080")
ENDEE_API_URL = f"{ENDEE_HOST}/api/v1"
ENDEE_INDEX_NAME = os.getenv("ENDEE_INDEX_NAME", "resume_index")
ENDEE_AUTH_TOKEN = os.getenv("ENDEE_AUTH_TOKEN", "") # auth token
ENDEE_USER = os.getenv("ENDEE_USER", "default")

# ai model config
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
VECTOR_DIMENSION = 384 # model dimensions
