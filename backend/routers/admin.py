from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from ..models import (
    MessageResponse, UserResponse, SubmissionResponse
)
from ..database import get_db
from ..dependencies import get_current_user, admin_required
from ..auth import hash_password
from ..config import UPLOAD_FOLDER
import os
import shutil

router = APIRouter(prefix="/api/admin", tags=["Admin"])
class RoleUpdateRequest(BaseModel):
    role: str   # "player" or "admin"
class ResetPasswordRequest(BaseModel):
    new_password: str

# ── Challenge CRUD ──
@router.post("/challenges", status_code=201, response_model=dict)
async def create_challenge(
    title: str = Form(...),
    description: str = Form(""),
    category_id: int = Form(...),
    points: int = Form(...),
    flag: str = Form(...),
    file: UploadFile = File(None),
    cursor = Depends(get_db),
    _admin: dict = Depends(admin_required)
):
    file_path = None
    if file and file.filename:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = file.filename
        with open(os.path.join(UPLOAD_FOLDER, file_path), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    cursor.execute(
        "INSERT INTO challenges (title, description, category_id, points, flag, file_path) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (title, description, category_id, points, flag, file_path)
    )
    challenge_id = cursor.lastrowid
    return {"challenge_id": challenge_id, "message": "Challenge created"}

@router.put("/challenges/{challenge_id}", response_model=MessageResponse)
async def update_challenge(
    challenge_id: int,
    title: str = Form(None),
    description: str = Form(None),
    category_id: int = Form(None),
    points: int = Form(None),
    flag: str = Form(None),
    file: UploadFile = File(None),
    cursor = Depends(get_db),
    _admin: dict = Depends(admin_required)
):
    cursor.execute("SELECT * FROM challenges WHERE id = %s", (challenge_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Challenge not found")

    updates = {}
    if title is not None: updates["title"] = title
    if description is not None: updates["description"] = description
    if category_id is not None: updates["category_id"] = category_id
    if points is not None: updates["points"] = points
    if flag is not None: updates["flag"] = flag
    if file and file.filename:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = file.filename
        with open(os.path.join(UPLOAD_FOLDER, file_path), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        updates["file_path"] = file_path

    if updates:
        set_clause = ", ".join(f"{k} = %s" for k in updates)
        cursor.execute(
            f"UPDATE challenges SET {set_clause} WHERE id = %s",
            (*updates.values(), challenge_id)
        )

    return {"message": "Challenge updated"}

@router.delete("/challenges/{challenge_id}", response_model=MessageResponse)
def delete_challenge(
    challenge_id: int,
    cursor = Depends(get_db),
    _admin: dict = Depends(admin_required)
):
    cursor.execute("SELECT file_path FROM challenges WHERE id = %s", (challenge_id,))
    ch = cursor.fetchone()
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if ch.get("file_path"):
        file_path = os.path.join(UPLOAD_FOLDER, ch["file_path"])
        if os.path.exists(file_path):
            os.remove(file_path)
    cursor.execute("DELETE FROM challenges WHERE id = %s", (challenge_id,))
    return {"message": "Challenge deleted"}

# ── User Management ──
@router.get("/users", response_model=list[UserResponse])
def list_users(cursor = Depends(get_db), _admin: dict = Depends(admin_required)):
    cursor.execute("SELECT id, username, role, score, solve_count FROM users")
    return cursor.fetchall()

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    cursor = Depends(get_db),
    _admin: dict = Depends(admin_required)
):
    cursor.execute(
        "SELECT id, username, role, score, solve_count FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    cursor = Depends(get_db),
    _admin: dict = Depends(admin_required)
):
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    return {"message": "User deleted"}

@router.put("/users/{user_id}/role", response_model=MessageResponse)
def update_user_role(
    user_id: int,
    req: RoleUpdateRequest,
    cursor = Depends(get_db),
    _admin: dict = Depends(admin_required)
):
    if req.role not in ("player", "admin"):
        raise HTTPException(status_code=400, detail="Role must be 'player' or 'admin'")

    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("UPDATE users SET role = %s WHERE id = %s", (req.role, user_id))
    return {"message": f"User role updated to {req.role}"}

@router.post("/users/{user_id}/reset-password", response_model=MessageResponse)
def reset_user_password(
    user_id: int,
    req: ResetPasswordRequest,
    cursor = Depends(get_db),
    _admin: dict = Depends(admin_required)
):
    # Check user exists
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")

    # Hash the new password and update
    hashed = hash_password(req.new_password)
    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user_id))

    return {"message": "Password reset successfully"}

# ── Submissions ──
@router.get("/submissions", response_model=list[SubmissionResponse])
def list_submissions(
    user_id: int = Query(None),
    challenge_id: int = Query(None),
    cursor = Depends(get_db),
    _admin: dict = Depends(admin_required)
):
    query = """
        SELECT s.id, u.username, c.title AS challenge_title,
               s.submitted_flag, s.is_correct, s.points_awarded, s.submitted_at
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        JOIN challenges c ON s.challenge_id = c.id
        WHERE 1=1
    """
    params = []
    if user_id is not None:
        query += " AND s.user_id = %s"
        params.append(user_id)
    if challenge_id is not None:
        query += " AND s.challenge_id = %s"
        params.append(challenge_id)
    query += " ORDER BY s.submitted_at DESC"
    cursor.execute(query, params)
    return cursor.fetchall()

# ── Event Control ──
@router.put("/event/start", response_model=dict)
def start_event(cursor = Depends(get_db), _admin: dict = Depends(admin_required)):
    cursor.execute("UPDATE event_status SET status = 'running', updated_at = NOW() WHERE id = 1")
    return {"status": "running", "message": "Event started"}

@router.put("/event/stop", response_model=dict)
def stop_event(cursor = Depends(get_db), _admin: dict = Depends(admin_required)):
    cursor.execute("UPDATE event_status SET status = 'closed', updated_at = NOW() WHERE id = 1")
    return {"status": "closed", "message": "Event stopped"}

# ── Scoreboard Reset ──
@router.post("/scoreboard/reset", response_model=MessageResponse)
def reset_scoreboard(cursor = Depends(get_db), _admin: dict = Depends(admin_required)):
    cursor.execute("DELETE FROM submissions")
    cursor.execute("UPDATE users SET score = 0, solve_count = 0, last_solve_time = NULL")
    return {"message": "Scoreboard reset. All scores cleared."}