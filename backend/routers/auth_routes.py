from fastapi import APIRouter, Depends, HTTPException, status
from ..models import RegisterRequest, LoginRequest, TokenResponse, MessageResponse
from ..database import get_db
from ..auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
def register(req: RegisterRequest, cursor=Depends(get_db)):
    # Check for duplicate username
    cursor.execute("SELECT id FROM users WHERE username = %s", (req.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Username already exists")

    # Always register as a player – admin role cannot be self-assigned
    role = "player"

    hashed = hash_password(req.password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
        (req.username, hashed, role)
    )
    return {"message": "Account created successfully"}

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, cursor=Depends(get_db)):
    # Fetch user by username
    cursor.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = %s",
        (req.username,)
    )
    user = cursor.fetchone()

    # Validate password
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT with user info
    token = create_access_token({"user_id": user["id"], "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }