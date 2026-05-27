from fastapi import APIRouter, Depends, HTTPException
from ..models import SubmitRequest, SubmitResponse
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["Submission"])

@router.post("/submit", response_model=SubmitResponse)
def submit_flag(
    req: SubmitRequest,
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check event is running
    cursor.execute("SELECT status FROM event_status WHERE id = 1")
    event = cursor.fetchone()
    if event["status"] != "running":
        raise HTTPException(status_code=403, detail="Event is not active")

    # Check for duplicate solve
    cursor.execute(
        "SELECT id FROM submissions WHERE user_id = %s AND challenge_id = %s AND is_correct = 1",
        (current_user["id"], req.challenge_id)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Already solved")

    # Get challenge
    cursor.execute("SELECT flag, points FROM challenges WHERE id = %s", (req.challenge_id,))
    challenge = cursor.fetchone()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    is_correct = (req.flag.strip() == challenge["flag"].strip())
    points_awarded = challenge["points"] if is_correct else 0

    # Record submission
    cursor.execute(
        "INSERT INTO submissions (user_id, challenge_id, submitted_flag, is_correct, points_awarded) "
        "VALUES (%s, %s, %s, %s, %s)",
        (current_user["id"], req.challenge_id, req.flag, is_correct, points_awarded)
    )

    if is_correct:
        cursor.execute(
            "UPDATE users SET score = score + %s, solve_count = solve_count + 1, "
            "last_solve_time = NOW() WHERE id = %s",
            (points_awarded, current_user["id"])
        )

    return SubmitResponse(
        correct=is_correct,
        points_awarded=points_awarded,
        message="Correct flag!" if is_correct else "Incorrect flag"
    )