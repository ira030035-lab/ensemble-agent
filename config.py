import os
from dotenv import load_dotenv
load_dotenv("/opt/ensemble-agent/.env")
class Config:
    BITGET_API_KEY = os.getenv("BITGET_API_KEY")
    BITGET_SECRET = os.getenv("BITGET_SECRET")
    BITGET_PASSPHRASE = os.getenv("BITGET_PASSPHRASE")
    BITGET_BASE_URL = "https://api.bitget.com"
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROK_API_KEY = os.getenv("GROK_API_KEY")
    BULL_MODEL = "gemini-1.5-flash"
    BEAR_MODEL = "grok-beta"
    JUDGE_MODEL = "claude-sonnet-4-20250514"
    TOP_N_SYMBOLS = 50
    SCAN_INTERVAL = 60
    MAX_POSITIONS = 5
    MIN_CONFIDENCE = 75
    MEMORY_FILE = "/opt/ensemble-agent/memory.json"
    TRADE_LOG = "/opt/ensemble-agent/trade_log.json"
    STATE_FILE = "/opt/ensemble-agent/state.json"
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
