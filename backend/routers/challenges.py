from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from ..models import CategoryResponse, ChallengeListItem, ChallengeDetailResponse
from ..database import get_db
from ..dependencies import get_current_user
import os
import math
from ..config import UPLOAD_FOLDER, MAX_FLAG_ATTEMPTS, MIN_POINTS, SOLVE_MIDPOINT, DECAY_STEEPNESS

router = APIRouter(prefix="/api", tags=["Challenges"])


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(cursor=Depends(get_db)):
    cursor.execute("SELECT id, name FROM categories ORDER BY id")
    return cursor.fetchall()


@router.get("/challenges", response_model=list[ChallengeListItem])
def list_challenges(
    category: int = Query(None),
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Base query for challenges
    base_query = """
        SELECT c.id, c.title, c.points, cat.name AS category
        FROM challenges c
        JOIN categories cat ON c.category_id = cat.id
    """
    params = []
    if category is not None:
        base_query += " WHERE c.category_id = %s"
        params.append(category)
    base_query += " ORDER BY c.id"
    cursor.execute(base_query, params)
    challenges = cursor.fetchall()

    # Get all challenge IDs
    challenge_ids = [ch["id"] for ch in challenges] if challenges else []
    if not challenge_ids:
        return []

    # Get solved status for all challenges for this user
    format_ids = ','.join(['%s'] * len(challenge_ids))
    cursor.execute(
        f"SELECT challenge_id FROM submissions WHERE user_id = %s AND is_correct = 1 AND challenge_id IN ({format_ids})",
        [current_user["id"]] + challenge_ids
    )
    solved_ids = {row["challenge_id"] for row in cursor.fetchall()}

    # Get incorrect attempt counts for unsolved challenges
    unsolved_ids = [cid for cid in challenge_ids if cid not in solved_ids]
    incorrect_counts = {}
    if unsolved_ids:
        format_unsolved = ','.join(['%s'] * len(unsolved_ids))
        cursor.execute(
            f"SELECT challenge_id, COUNT(*) AS cnt FROM submissions WHERE user_id = %s AND is_correct = 0 AND challenge_id IN ({format_unsolved}) GROUP BY challenge_id",
            [current_user["id"]] + unsolved_ids
        )
        for row in cursor.fetchall():
            incorrect_counts[row["challenge_id"]] = row["cnt"]

    # Fetch solve counts for all challenges (for dynamic scoring)
    solve_counts = {}
    if challenge_ids:
        cursor.execute(
            f"SELECT challenge_id, COUNT(*) AS cnt FROM submissions WHERE is_correct = 1 AND challenge_id IN ({format_ids}) GROUP BY challenge_id",
            challenge_ids
        )
        for row in cursor.fetchall():
            solve_counts[row["challenge_id"]] = row["cnt"]

    # Build result list with dynamic points
    result = []
    for ch in challenges:
        solved = ch["id"] in solved_ids
        attempts_remaining = None
        if not solved:
            used = incorrect_counts.get(ch["id"], 0)
            attempts_remaining = max(0, MAX_FLAG_ATTEMPTS - used)

        base_points = ch["points"]
        solve_count = solve_counts.get(ch["id"], 0)

        if solve_count ==0:
            current_points = base_points
        else:
        # Logistic current points = Min + (Max - Min) / (1 + exp(k * (solves - M)))
            exponent = DECAY_STEEPNESS * (solve_count - SOLVE_MIDPOINT)
            current_points = int(MIN_POINTS + (base_points - MIN_POINTS) / (1 + math.exp(exponent)))

        result.append(ChallengeListItem(
            id=ch["id"],
            title=ch["title"],
            points=base_points,            # base points from DB
            current_points=current_points, # dynamic points
            category=ch["category"],
            solved=solved,
            attempts_remaining=attempts_remaining
        ))

    return result


@router.get("/challenges/{challenge_id}", response_model=ChallengeDetailResponse)
def get_challenge(
    challenge_id: int,
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor.execute("""
        SELECT c.*, cat.name AS category
        FROM challenges c
        JOIN categories cat ON c.category_id = cat.id
        WHERE c.id = %s
    """, (challenge_id,))
    ch = cursor.fetchone()
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Solved?
    cursor.execute(
        "SELECT id FROM submissions WHERE user_id = %s AND challenge_id = %s AND is_correct = 1",
        (current_user["id"], challenge_id)
    )
    solved = cursor.fetchone() is not None

    attempts_remaining = None
    if not solved:
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM submissions WHERE user_id = %s AND challenge_id = %s AND is_correct = 0",
            (current_user["id"], challenge_id)
        )
        used = cursor.fetchone()["cnt"]
        attempts_remaining = max(0, MAX_FLAG_ATTEMPTS - used)

    # Compute dynamic points using logistic formula
    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM submissions WHERE challenge_id = %s AND is_correct = 1",
        (challenge_id,)
    )
    solve_count = cursor.fetchone()["cnt"]
    if solve_count == 0:
        current_points = ch["points"]
    else:
        exponent = DECAY_STEEPNESS * (solve_count - SOLVE_MIDPOINT)
        current_points = int(MIN_POINTS + (ch["points"] - MIN_POINTS) / (1 + math.exp(exponent)))

    return ChallengeDetailResponse(
        id=ch["id"],
        title=ch["title"],
        description=ch.get("description"),
        points=ch["points"],            # base points
        current_points=current_points,  # dynamic points
        category=ch["category"],
        file_exists=bool(ch.get("file_path")),
        solved=solved,
        attempts_remaining=attempts_remaining
    )


@router.get("/challenges/{challenge_id}/download")
def download_challenge(
    challenge_id: int,
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor.execute("SELECT file_path, title FROM challenges WHERE id = %s", (challenge_id,))
    ch = cursor.fetchone()
    if not ch or not ch.get("file_path"):
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(UPLOAD_FOLDER, ch["file_path"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(file_path, filename=ch["file_path"], media_type="application/octet-stream")