from fastapi import APIRouter, Depends
from ..models import ScoreboardEntry, EventStatusResponse, StatsResponse
from ..database import get_db

router = APIRouter(prefix="/api", tags=["Public"])

@router.get("/scoreboard", response_model=list[ScoreboardEntry])
def get_scoreboard(cursor=Depends(get_db)):
    cursor.execute("""
        SELECT username, score, solve_count, last_solve_time
        FROM users
        WHERE role = 'player'
        ORDER BY score DESC, last_solve_time ASC
    """)
    rows = cursor.fetchall()
    return [
        ScoreboardEntry(
            rank=i + 1,
            username=row["username"],
            score=row["score"],
            solve_count=row["solve_count"],
            last_solve_time=row.get("last_solve_time")
        )
        for i, row in enumerate(rows)
    ]

@router.get("/event/status", response_model=EventStatusResponse)
def get_event_status(cursor=Depends(get_db)):
    cursor.execute("SELECT status, updated_at FROM event_status WHERE id = 1")
    row = cursor.fetchone()
    return {"status": row["status"], "updated_at": row.get("updated_at")}

@router.get("/stats", response_model=StatsResponse)
def get_stats(cursor=Depends(get_db)):
    cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'player'")
    participants = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) AS cnt FROM challenges")
    challenges = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) AS cnt FROM submissions WHERE is_correct = 1")
    solves = cursor.fetchone()["cnt"]
    return {
        "total_participants": participants,
        "total_challenges": challenges,
        "total_solves": solves
    }