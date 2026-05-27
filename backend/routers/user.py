from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..models import SolveEntry, MeScoreResponse, MessageResponse
from ..database import get_db
from ..dependencies import get_current_user
from ..auth import verify_password, hash_password

router = APIRouter(prefix="/api/me", tags=["User"])

@router.get("/solves", response_model=list[SolveEntry])
def my_solves(cursor=Depends(get_db), current_user: dict = Depends(get_current_user)):
    cursor.execute("""
        SELECT s.challenge_id, c.title, s.points_awarded AS points, s.submitted_at AS solved_at
        FROM submissions s
        JOIN challenges c ON s.challenge_id = c.id
        WHERE s.user_id = %s AND s.is_correct = 1
        ORDER BY s.submitted_at DESC
    """, (current_user["id"],))
    return cursor.fetchall()

@router.get("/score", response_model=MeScoreResponse)
def my_score(cursor=Depends(get_db), current_user: dict = Depends(get_current_user)):
    cursor.execute(
        "SELECT username, score, solve_count FROM users WHERE id = %s",
        (current_user["id"],)
    )
    user = cursor.fetchone()
    return MeScoreResponse(**user)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.put("/password", response_model=MessageResponse)
def change_password(
    req: ChangePasswordRequest,
    cursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verify current password
    cursor.execute("SELECT password_hash FROM users WHERE id = %s", (current_user["id"],))
    user = cursor.fetchone()
    if not verify_password(req.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Hash and update new password
    hashed = hash_password(req.new_password)
    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, current_user["id"]))

    return {"message": "Password changed successfully"}