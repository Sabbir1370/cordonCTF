from fastapi import APIRouter, Depends, HTTPException
from ..models import SubmitRequest, SubmitResponse
from ..database import get_db
from ..dependencies import get_current_user
from ..config import MAX_FLAG_ATTEMPTS, MIN_POINTS, SOLVE_MIDPOINT, DECAY_STEEPNESS
import math

router = APIRouter(prefix="/api", tags=["Submission"])


@router.post("/submit", response_model=SubmitResponse)
def submit_flag(
    req: SubmitRequest,
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 1. Event must be running
    cursor.execute("SELECT status FROM event_status WHERE id = 1")
    event = cursor.fetchone()
    if event["status"] != "running":
        raise HTTPException(status_code=403, detail="Event is not active")

    # 2. Already solved?
    cursor.execute(
        "SELECT id FROM submissions WHERE user_id = %s AND challenge_id = %s AND is_correct = 1",
        (current_user["id"], req.challenge_id)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Already solved")

    # 3. Get challenge info
    cursor.execute("SELECT flag, points FROM challenges WHERE id = %s", (req.challenge_id,))
    challenge = cursor.fetchone()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    is_correct = (req.flag.strip() == challenge["flag"].strip())

    # ── CORRECT FLAG ──────────────────────────────────────────
    if is_correct:
        # Count how many correct submissions already exist for this challenge
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM submissions WHERE challenge_id = %s AND is_correct = 1",
            (req.challenge_id,)
        )
        row = cursor.fetchone()
        # Safely extract count (works for dict or tuple cursors)
        if row is None:
            solve_count_before = 0
        elif isinstance(row, dict):
            solve_count_before = row["cnt"]
        else:
            solve_count_before = row[0]

        # Logistic dynamic score
        if solve_count_before == 0:
            points_awarded = challenge["points"]
        else:
            exponent = DECAY_STEEPNESS * (solve_count_before - SOLVE_MIDPOINT)
            points_awarded = MIN_POINTS + (challenge["points"] - MIN_POINTS) / (1 + math.exp(exponent))
            points_awarded = int(points_awarded)
        # Insert one single correct submission
        cursor.execute(
            "INSERT INTO submissions (user_id, challenge_id, submitted_flag, is_correct, points_awarded) "
            "VALUES (%s, %s, %s, %s, %s)",
            (current_user["id"], req.challenge_id, req.flag, True, points_awarded)
        )

        # Update user score
        cursor.execute(
            "UPDATE users SET score = score + %s, solve_count = solve_count + 1, "
            "last_solve_time = NOW() WHERE id = %s",
            (points_awarded, current_user["id"])
        )

        return SubmitResponse(
            correct=True,
            points_awarded=points_awarded,
            message="Correct flag!"
        )

    # ── INCORRECT FLAG ────────────────────────────────────────
    else:
        # Check attempt limit
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM submissions WHERE user_id = %s AND challenge_id = %s AND is_correct = 0",
            (current_user["id"], req.challenge_id)
        )
        row = cursor.fetchone()
        if row is None:
            incorrect_attempts = 0
        elif isinstance(row, dict):
            incorrect_attempts = row["cnt"]
        else:
            incorrect_attempts = row[0]

        if incorrect_attempts >= MAX_FLAG_ATTEMPTS:
            raise HTTPException(status_code=429, detail=f"Too many attempts. Max {MAX_FLAG_ATTEMPTS} incorrect tries allowed.")

        # Record the incorrect submission
        cursor.execute(
            "INSERT INTO submissions (user_id, challenge_id, submitted_flag, is_correct, points_awarded) "
            "VALUES (%s, %s, %s, %s, %s)",
            (current_user["id"], req.challenge_id, req.flag, False, 0)
        )

        return SubmitResponse(
            correct=False,
            points_awarded=0,
            message="Incorrect flag"
        )