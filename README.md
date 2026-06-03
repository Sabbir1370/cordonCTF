# CordonCTF — Offline Local CTF Platform

CordonCTF is a **self-hosted, offline Capture The Flag (CTF) platform** designed to run entirely from a single laptop. It creates a local Wi-Fi hotspot so participants can join using just a browser — **no internet connection required**.

> **Hotspot management is handled by [CordonNet](https://github.com/Sabbir1370/cordonnet)** — a companion tool that creates a virtual AP on your existing Wi-Fi card without dropping your own internet connection.

---

## Features

- **Public dashboard** — live scoreboard and event status
- **User registration & login** — secure password hashing + JWT
- **Player portal** — browse challenges by category, download files, submit flags
- **Automatic flag validation** — duplicate prevention, points awarding, real-time ranking
- **Admin control panel** — full CRUD for challenges, user management, event start/stop, submission viewer, scoreboard reset
- **Single-laptop deployment** — runs fully offline via CordonNet virtual AP

---

## Technology Stack

| Layer    | Technology                                           |
| -------- | ---------------------------------------------------- |
| Frontend | HTML5, CSS3, JavaScript                              |
| Backend  | Python (FastAPI)                                     |
| Server   | Uvicorn ASGI                                         |
| Database | MySQL / MariaDB                                      |
| Auth     | JWT + bcrypt                                         |
| Hotspot  | [CordonNet](https://github.com/Sabbir1370/cordonnet) |

---

## Project Structure

```
cordonctf/
├── backend/          # FastAPI application (routers, auth, models)
├── database/         # SQL schema file
├── frontend/         # Static web files (HTML, CSS, JS)
├── uploads/          # Challenge files storage
├── docs/             # Documentation and diagrams
├── requirements.txt  # Python dependencies
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.8+
- MySQL / MariaDB (XAMPP or native)
- [CordonNet](https://github.com/Sabbir1370/cordonnet) — for hotspot deployment

### Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/Sabbir1370/cordonctf.git
cd cordonctf

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start your database server (example with XAMPP)
sudo /opt/lampp/lampp startmysql

# 5. Create the database and tables
mysql -u root -p < database/schema.sql

# 6. Seed the event status row
mysql -u root -p -e "USE cordonctf; INSERT INTO event_status (status) VALUES ('closed');"

# 7. Run the backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 8. Open in browser
# http://localhost:8000/frontend/index.html
```

---

## Hotspot Deployment (CTF Mode)

In a real CTF, participants connect to your laptop's Wi-Fi hotspot and access the platform through their browsers. **[CordonNet](https://github.com/Sabbir1370/cordonnet)** handles this automatically — it creates a virtual AP on your existing Wi-Fi card so your own internet stays alive while the hotspot runs.

### 1. Install CordonNet

```bash
git clone https://github.com/Sabbir1370/cordonnet.git
cd cordonnet
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 2. Configure (once)

```bash
# Check your Wi-Fi card name
iw dev

# Set it in CordonNet
cordonnet hotspot set-interface wlp1s0   # replace with your interface

# Optionally set a custom SSID and password
cordonnet hotspot set-ssid "CordonCTF"
cordonnet hotspot set-password "ctfpassword"
```

### 3. Start the hotspot

```bash
# Isolated mode — participants get LAN access only (recommended for CTF)
sudo $(which python) -m cordonnet.main hotspot start --isolated

# Or with internet sharing enabled
sudo $(which python) -m cordonnet.main hotspot start
```

### 4. Start CordonCTF backend

```bash
cd cordonctf
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 5. Participants connect

- Join the `CordonCTF` Wi-Fi network
- Open browser → `http://192.168.50.1:8000/frontend/index.html`
- The gateway IP `192.168.50.1` is CordonNet's default — change it in `cordonnet/config/default.yaml` if needed

### 6. Stop everything

```bash
sudo $(which python) -m cordonnet.main hotspot stop
# Your Wi-Fi is fully restored, no reboot needed
```

---

## Related

- **[CordonNet](https://github.com/Sabbir1370/cordonnet)** — the virtual AP hotspot tool that powers CordonCTF's network layer

---

> This README is a work in progress. Detailed setup instructions and documentation will be added as the project evolves.
