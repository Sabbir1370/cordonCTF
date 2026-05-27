from fastapi import APIRouter, Depends
from ..models import SolveEntry, MeScoreResponse
from ..database import get_db
from ..dependencies import get_current_user

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