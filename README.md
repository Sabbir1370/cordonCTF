# CordonCTF - Offline Local CTF Platform

CordonCTF is a **self-hosted, offline Capture The Flag (CTF) platform** designed to run entirely from a single laptop. It creates a local WiFi hotspot so that multiple participants can join the competition using just a web browser – **no internet connection required**.

The platform supports:
- **Public dashboard** with live scoreboard and event status
- **User registration & login** (secure password hashing + JWT)
- **Player portal** – browse challenges by category, download challenge files, submit flags
- **Automatic flag validation** – duplicate prevention, points awarding, and real-time ranking
- **Admin control panel** – full CRUD for challenges, user management, event start/stop, submission viewer, and scoreboard reset

## Technology Stack
| Layer    | Technology |
|----------|------------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend  | Python (FastAPI) |
| Server   | Uvicorn ASGI |
| Database | MySQL / MariaDB |
| Auth     | JWT + bcrypt |

## Project Structure
cordonctf/
├── backend/ # FastAPI application (routers, auth, models)
├── database/ # SQL schema file
├── frontend/ # Static web files (HTML, CSS, JS)
├── uploads/ # Challenge files storage
├── docs/ # Documentation and diagrams
├── requirements.txt # Python dependencies
└── README.md

> This README is a work in progress. Detailed setup instructions and documentation will be added as the project evolves.
