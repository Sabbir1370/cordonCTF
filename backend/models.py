from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ── Auth ──
class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "player"          # "player" or "admin"

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

# ── Public ──
class ScoreboardEntry(BaseModel):
    rank: int
    username: str
    score: int
    solve_count: int
    last_solve_time: Optional[datetime] = None

class EventStatusResponse(BaseModel):
    status: str
    updated_at: Optional[datetime] = None

class StatsResponse(BaseModel):
    total_participants: int
    total_challenges: int
    total_solves: int

# ── Categories & Challenges ──
class CategoryResponse(BaseModel):
    id: int
    name: str

class ChallengeListItem(BaseModel):
    id: int
    title: str
    points: int
    category: str
    solved: bool

class ChallengeDetailResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    points: int
    category: str
    file_exists: bool
    solved: bool

# ── Flag Submission ──
class SubmitRequest(BaseModel):
    challenge_id: int
    flag: str

class SubmitResponse(BaseModel):
    correct: bool
    points_awarded: int
    message: str

# ── User / Me ──
class SolveEntry(BaseModel):
    challenge_id: int
    title: str
    points: int
    solved_at: Optional[datetime] = None

class MeScoreResponse(BaseModel):
    username: str
    score: int
    solve_count: int

# ── Admin ──
class ChallengeCreateRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    category_id: int
    points: int
    flag: str

class ChallengeUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    points: Optional[int] = None
    flag: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    score: int
    solve_count: int

class SubmissionResponse(BaseModel):
    id: int
    username: str
    challenge_title: str
    submitted_flag: str
    is_correct: bool
    points_awarded: int
    submitted_at: Optional[datetime] = None

class MessageResponse(BaseModel):
    message: str