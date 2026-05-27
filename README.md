# CordonCTF - Offline Local CTF Platform

CordonCTF is a **self-hosted, offline Capture The Flag (CTF) platform** designed to run entirely from a single laptop. It creates a local WiFi hotspot so that multiple participants can join the competition using just a web browser – **no internet connection required**.

The platform supports:

- **Public dashboard** with live scoreboard and event status
- **User registration & login** (secure password hashing + JWT)
- **Player portal** – browse challenges by category, download challenge files, submit flags
- **Automatic flag validation** – duplicate prevention, points awarding, and real-time ranking
- **Admin control panel** – full CRUD for challenges, user management, event start/stop, submission viewer, and scoreboard reset

## Technology Stack

| Layer    | Technology              |
| -------- | ----------------------- |
| Frontend | HTML5, CSS3, JavaScript |
| Backend  | Python (FastAPI)        |
| Server   | Uvicorn ASGI            |
| Database | MySQL / MariaDB         |
| Auth     | JWT + bcrypt            |

## Project Structure

cordonctf/
├── backend/ # FastAPI application (routers, auth, models)
├── database/ # SQL schema file
├── frontend/ # Static web files (HTML, CSS, JS)
├── uploads/ # Challenge files storage
├── docs/ # Documentation and diagrams
├── requirements.txt # Python dependencies
└── README.md

## Quick Start (Local Development)

### Prerequisites

- Python 3.8+
- MySQL / MariaDB (XAMPP or native)
- `pip` and `venv`

### Setup

1. **Clone the repository** and navigate into it.
2. **Create and activate a virtual environment**  
   `python3 -m venv venv`  
   `source venv/bin/activate` (Linux/macOS)
3. **Install dependencies**  
   `pip install -r requirements.txt`
4. **Start your database server** (example with XAMPP):  
   `sudo /opt/lampp/lampp startmysql`
5. **Create the database and tables**  
   `mysql -u root -p < database/schema.sql`  
   (If prompted for a password, press Enter – XAMPP’s default is blank)
6. **Seed the event status row**  
   `mysql -u root -p -e "USE cordonctf; INSERT INTO event_status (status) VALUES ('closed');"`
7. **Run the backend**  
   `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
8. **Open the frontend**  
   Visit `http://localhost:8000/frontend/index.html` in your browser.

### WiFi Hotspot Deployment

- Create a WiFi hotspot on your laptop.
- Find your laptop’s local IP (e.g., `192.168.1.x`).
- Other devices on the hotspot can access the platform at `http://<LAPTOP-IP>:8000/frontend/index.html`.
- Ensure firewall allows port 8000: `sudo ufw allow 8000` (if using ufw).

> This README is a work in progress. Detailed setup instructions and documentation will be added as the project evolves.
