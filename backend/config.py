# backend/config.py
DB_HOST = "127.0.0.1"
DB_USER = "ctfadmin"
DB_PASSWORD = "ctf_pass_2025"
DB_NAME = "cordonctf"
DB_PORT = 3306

SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

UPLOAD_FOLDER = "uploads"
MAX_FLAG_ATTEMPTS = 5  # Maximum incorrect flag submissions per user per challenge
MIN_POINTS = 50
SOLVE_MIDPOINT = 5
DECAY_STEEPNESS = 0.5