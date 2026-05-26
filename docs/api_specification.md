# CordonCTF API Specification v1.0

**Base URL:** `http://<host-laptop-ip>:8000`  
**Authentication:** Bearer `<JWT>` in `Authorization` header for protected routes.
+===================================================================================================+
| CordonCTF API ENDPOINTS – Full Documentation |
+===================================================================================================+
| Base URL: http://<host-laptop-ip>:8000 |
| Authentication: Bearer <JWT> in Authorization header (if required) |
+===================================================================================================+
================================================================================================
AUTHENTICATION (No Auth Required)
================================================================================================

    POST /api/auth/register – Register a new account

    POST /api/auth/login – Login and receive JWT token

Details:
[1] POST /api/auth/register
Request : { "username": "...", "password": "...", "role": "player"|"admin" }
Success: 201 { "message": "Account created successfully" }
Error : 409 { "detail": "Username already exists" }

[2] POST /api/auth/login
Request : { "username": "...", "password": "..." }
Success: 200 { "access_token": "eyJ...", "token_type": "bearer", "role": "player"|"admin" }
Error : 401 { "detail": "Invalid credentials" }
================================================================================================
PUBLIC ENDPOINTS (No Auth Required)
================================================================================================

    GET /api/scoreboard – View current scoreboard/rankings

    GET /api/event/status – Get event status (running/closed)

    GET /api/stats – Get platform statistics (optional)

Details:
[3] GET /api/scoreboard
Response 200: [ { "rank": 1, "username": "...", "score": 300, "solve_count": 3, "last_solve_time": "..." } ]

[4] GET /api/event/status
Response 200: { "status": "running", "updated_at": "..." }

[5] GET /api/stats
Response 200: { "total_participants": 12, "total_challenges": 10, "total_solves": 45 }
================================================================================================
PLAYER ENDPOINTS (Auth Required: player / admin)
================================================================================================

    GET /api/categories – List all challenge categories

    GET /api/challenges – List challenges (optional ?category=id)

    GET /api/challenges/{id} – View challenge details

    GET /api/challenges/{id}/download – Download challenge file

    POST /api/submit – Submit flag for a challenge

    GET /api/me/solves – View challenges solved by current user

    GET /api/me/score – Get personal score & solve count

Details:
[6] GET /api/categories
Response 200: [ { "id": 1, "name": "Web" }, { "id": 2, "name": "Crypto" } ]

[7] GET /api/challenges?category=1
Response 200: [ { "id": 1, "title": "BabyWeb", "points": 100, "category": "Web", "solved": false } ]

[8] GET /api/challenges/{id}
Response 200: {
"id": 1, "title": "BabyWeb", "description": "...", "points": 100,
"category": "Web", "file_exists": true, "solved": false
}

[9] GET /api/challenges/{id}/download
Response 200: file stream (Content-Disposition: attachment)

[10] POST /api/submit
Request : { "challenge_id": 1, "flag": "FLAG{...}" }
Success (correct) : 200 { "correct": true, "points_awarded": 100, "message": "Correct flag!" }
Success (incorrect): 200 { "correct": false, "points_awarded": 0, "message": "Incorrect flag" }
Error: 403 { "detail": "Event is not active" }
Error: 409 { "detail": "Already solved" }

[11] GET /api/me/solves
Response 200: [ { "challenge_id": 1, "title": "BabyWeb", "points": 100, "solved_at": "..." } ]

[12] GET /api/me/score
Response 200: { "username": "player1", "score": 300, "solve_count": 3 }
================================================================================================
ADMIN ENDPOINTS (Auth Required: admin only)
================================================================================================

    POST /api/admin/challenges – Create a new challenge

    PUT /api/admin/challenges/{id} – Update a challenge

    DELETE /api/admin/challenges/{id} – Delete a challenge

    GET /api/admin/users – List all users

    GET /api/admin/users/{id} – Get user details

    DELETE /api/admin/users/{id} – Delete a user

    GET /api/admin/submissions – View all submissions (?user_id= & ?challenge_id=)

    PUT /api/admin/event/start – Set event status to "running"

    PUT /api/admin/event/stop – Set event status to "closed"

    POST /api/admin/scoreboard/reset – Reset all scores & submissions

Details:
[13] POST /api/admin/challenges
Request : { "title": "...", "description": "...", "category_id": 1, "points": 100, "flag": "FLAG{...}", "file": (upload) }
Success: 201 { "challenge_id": 1, "message": "Challenge created" }

[14] PUT /api/admin/challenges/{id}
Request : { "title": "...", "points": 150, ... } (partial update)
Success: 200 { "message": "Challenge updated" }

[15] DELETE /api/admin/challenges/{id}
Response: 200 { "message": "Challenge deleted" }

[16] GET /api/admin/users
Response: [ { "id": 1, "username": "player1", "role": "player", "score": 100, "solve_count": 1 } ]

[17] GET /api/admin/users/{id}
Response: { "id": 1, "username": "...", "role": "...", "score": ..., "solve_count": ... }

[18] DELETE /api/admin/users/{id}
Response: 200 { "message": "User deleted" }

[19] GET /api/admin/submissions?user_id=1&challenge_id=2
Response: [ {
"id": 1, "username": "player1", "challenge_title": "BabyWeb",
"submitted_flag": "FLAG{...}", "is_correct": true, "points_awarded": 100, "submitted_at": "..."
} ]

[20] PUT /api/admin/event/start
Response: 200 { "status": "running", "message": "Event started" }

[21] PUT /api/admin/event/stop
Response: 200 { "status": "closed", "message": "Event stopped" }

[22] POST /api/admin/scoreboard/reset
Response: 200 { "message": "Scoreboard reset. All scores cleared." }
