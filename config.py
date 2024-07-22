from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CHANNEL = int(os.getenv('CHANNEL'))
LOG_CHAT = int(os.getenv('LOG_CHAT'))
AI_GEN_API = os.getenv('AI_GEN_API')
IMGBBTOKEN = os.getenv('IMGBBTOKEN')
CHANNEL_LINK = os.getenv('CHANNEL_LINK')
DB_PATH = os.getenv('DB_PATH')
ADMIN_IDS = list(os.getenv('ADMIN_IDS'))
