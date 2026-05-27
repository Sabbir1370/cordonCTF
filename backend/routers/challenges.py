from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from ..models import CategoryResponse, ChallengeListItem, ChallengeDetailResponse
from ..database import get_db
from ..dependencies import get_current_user
import os
from ..config import UPLOAD_FOLDER

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
    if category is not None:
        cursor.execute("""
            SELECT c.id, c.title, c.points, cat.name AS category
            FROM challenges c
            JOIN categories cat ON c.category_id = cat.id
            WHERE c.category_id = %s
            ORDER BY c.id
        """, (category,))
    else:
        cursor.execute("""
            SELECT c.id, c.title, c.points, cat.name AS category
            FROM challenges c
            JOIN categories cat ON c.category_id = cat.id
            ORDER BY c.id
        """)
    challenges = cursor.fetchall()

    result = []
    for ch in challenges:
        cursor.execute(
            "SELECT id FROM submissions WHERE user_id = %s AND challenge_id = %s AND is_correct = 1",
            (current_user["id"], ch["id"])
        )
        solved = cursor.fetchone() is not None
        result.append(ChallengeListItem(
            id=ch["id"],
            title=ch["title"],
            points=ch["points"],
            category=ch["category"],
            solved=solved
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

    cursor.execute(
        "SELECT id FROM submissions WHERE user_id = %s AND challenge_id = %s AND is_correct = 1",
        (current_user["id"], challenge_id)
    )
    solved = cursor.fetchone() is not None

    return ChallengeDetailResponse(
        id=ch["id"],
        title=ch["title"],
        description=ch.get("description"),
        points=ch["points"],
        category=ch["category"],
        file_exists=bool(ch.get("file_path")),
        solved=solved
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