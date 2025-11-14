from dotenv import load_dotenv 
import os
import sys

load_dotenv()

# Critical environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_KEY = os.getenv("MY_API_KEY")

# Validate critical variables
if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY environment variable is not set!")
    sys.exit(1)
if not API_KEY:
    print("ERROR: MY_API_KEY environment variable is not set!")
    sys.exit(1)



OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))  # Very low for data-focused, minimal hallucination
TOP_K = int(os.getenv("TOP_K", "5"))  # Retrieve more context for better data coverage

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "800"))  # Optimized for detailed, data-driven consultations

CHROMADB_API_KEY = os.getenv("CHROMADB_API_KEY", "")
CHROMADB_TENANT = os.getenv("CHROMADB_TENANT", "")
CHROMADB_DB_NAME = os.getenv("CHROMADB_DB_NAME", "Astrolozee")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "knowledge_base")




# LangSmith (optional)
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")



# # MongoDB for chat history
# MONGO_URI = os.getenv("MONGO_URI")
# MONGO_DB = os.getenv("MONGO_DB")
# MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
# # ------------------------------------------
# End of config.py