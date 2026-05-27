from fastapi import APIRouter, Depends, HTTPException, status
from ..models import RegisterRequest, LoginRequest, TokenResponse, MessageResponse
from ..database import get_db
from ..auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
def register(req: RegisterRequest, cursor=Depends(get_db)):
    # Reject invalid roles early
    if req.role not in ("player", "admin"):
        raise HTTPException(status_code=400, detail="Role must be 'player' or 'admin'")

    # Check for duplicate username
    cursor.execute("SELECT id FROM users WHERE username = %s", (req.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Username already exists")

    # Hash password and insert user
    hashed = hash_password(req.password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
        (req.username, hashed, req.role)
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