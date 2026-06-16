# CordonCTF — Offline Local CTF Platform

CordonCTF is a **self-hosted, offline Capture The Flag (CTF) platform** designed to run entirely from a single laptop. It creates a local Wi-Fi hotspot so participants can join using just a browser — **no internet connection required**.

> **Hotspot management is handled by [CordonNet](https://github.com/Sabbir1370/cordonnet)** — a companion tool that creates a virtual AP on your existing Wi-Fi card without dropping your own internet connection.

---

## Features

- **Public dashboard** — live scoreboard and event status
- **User registration & login** — secure password hashing + JWT
- **Player portal** — browse challenges by category, download files, submit flags
- **Automatic flag validation** — duplicate prevention, dynamic scoring, real-time ranking
- **Admin control panel** — full CRUD for challenges, user management, event start/stop, submission viewer, scoreboard reset
- **Single-laptop deployment** — runs fully offline via CordonNet virtual AP
- **Custom domain access** — participants use `https://ctf.local` or `https://play.ctf` instead of raw IPs
- **HTTPS** — self-signed TLS via Nginx reverse proxy; prevents credential/flag sniffing on the LAN
- **Fully offline assets** — Bootstrap and all static files served locally, no internet required

---

## Technology Stack

| Layer      | Technology                                              |
| ---------- | ------------------------------------------------------- |
| Frontend   | HTML5, CSS3, JavaScript (Bootstrap 5, local)            |
| Backend    | Python (FastAPI)                                        |
| App Server | Uvicorn ASGI (localhost:8000, behind Nginx)             |
| Web Server | Nginx (reverse proxy + TLS termination, port 443)       |
| Database   | MariaDB                                                 |
| Auth       | JWT + bcrypt                                            |
| Hotspot    | [CordonNet](https://github.com/Sabbir1370/cordonnet)    |
| DNS        | dnsmasq (via CordonNet) — resolves ctf.local / play.ctf |

---

## Project Structure

```
cordonctf/
├── backend/          # FastAPI application (routers, auth, models, config)
├── database/         # SQL schema file
├── frontend/         # Static web files (HTML, CSS, JS + local vendor assets)
│   ├── css/vendor/   # Bootstrap CSS (local, no CDN)
│   └── js/vendor/    # Bootstrap JS (local, no CDN)
├── scripts/          # One-time setup scripts (init_admin.py)
├── uploads/          # Challenge files storage
├── requirements.txt  # Python dependencies
└── README.md
```

---

## Installation & Setup (First Time)

### Prerequisites

- Python 3.12+
- MariaDB (system service, not XAMPP)
- Nginx
- [CordonNet](https://github.com/Sabbir1370/cordonnet) — for hotspot deployment

### 1. Clone and install

```bash
git clone https://github.com/Sabbir1370/cordonCTF.git
cd cordonCTF
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Database setup

```bash
# Start MariaDB
sudo systemctl start mariadb
sudo systemctl enable mariadb   # auto-start on boot

# Create database and tables
sudo mysql -u root < database/schema.sql

# Create the MySQL user (match password to backend/config.py DB_PASSWORD)
sudo mysql -u root -e "
  CREATE USER IF NOT EXISTS \'ctfadmin\'@\'localhost\' IDENTIFIED BY \'your_password\';
  GRANT ALL PRIVILEGES ON cordonctf.* TO \'ctfadmin\'@\'localhost\';
  FLUSH PRIVILEGES;
"

# Create the first admin user (interactive)
python scripts/init_admin.py
```

### 3. Nginx setup

```bash
sudo apt install -y nginx

# Generate self-signed TLS certificate
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/cordonctf.key \
  -out /etc/nginx/ssl/cordonctf.crt \
  -subj "/CN=ctf.local" \
  -addext "subjectAltName=DNS:ctf.local,DNS:play.ctf,IP:192.168.50.1"

# Write Nginx config
sudo tee /etc/nginx/sites-available/cordonctf << \'EOF\'
server {
    listen 80;
    server_name ctf.local play.ctf 192.168.50.1;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name ctf.local play.ctf 192.168.50.1;

    ssl_certificate     /etc/nginx/ssl/cordonctf.crt;
    ssl_certificate_key /etc/nginx/ssl/cordonctf.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    root /home/<YOUR_USERNAME>/cordonCTF/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000;
    }
}
EOF

# Enable and allow Nginx to read frontend files
sudo ln -s /etc/nginx/sites-available/cordonctf /etc/nginx/sites-enabled/
chmod o+x ~
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
```

> Replace `<YOUR_USERNAME>` in the Nginx config `root` path with your actual Linux username.

### 4. CordonNet setup (one time)

```bash
git clone https://github.com/Sabbir1370/cordonnet.git
cd cordonnet
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Set your Wi-Fi interface
cordonnet hotspot set-interface wlp1s0   # replace with yours (run: iw dev)

# Set SSID and password
cordonnet hotspot set-ssid "CordonCTF"
cordonnet hotspot set-password "ctfpassword"
```

---

## Running the Platform (Every Session)

```bash
# Terminal 1 — Start hotspot (isolated: participants get LAN only, no internet)
cd ~/cordonnet && source venv/bin/activate
sudo $(which python) -m cordonnet.main hotspot start --isolated

# Terminal 2 — Start backend
cd ~/cordonCTF && source venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Nginx starts automatically on boot — if not running:
sudo systemctl start nginx
```

---

## Participant Instructions

1. Connect to Wi-Fi: **CordonCTF** (or your configured SSID)
2. Open **Firefox**
3. Go to: `https://ctf.local` or `https://play.ctf`
4. Click **Advanced** → **Accept the Risk and Continue** (self-signed cert warning, one time only)
5. Register an account and start hacking

> Chrome and Edge may auto-upgrade to HTTPS and behave unpredictably with self-signed certs. **Firefox is strongly recommended.**

---

## Stopping the Platform

```bash
# Stop the hotspot (restores your Wi-Fi fully)
sudo $(which python) -m cordonnet.main hotspot stop

# Stop the backend
# Ctrl+C in the uvicorn terminal

# Nginx runs as a system service — leave it running or:
sudo systemctl stop nginx
```

---

## Scoring

CordonCTF uses **dynamic/decaying points** — each challenge has a base point value that decreases as more participants solve it, following a logistic decay curve. Early solvers are rewarded more. Points awarded at solve time are permanent — editing a challenge's base value later only affects future solvers.

---

## Related

- **[CordonNet](https://github.com/Sabbir1370/cordonnet)** — the virtual AP hotspot tool that powers CordonCTF's network layer
