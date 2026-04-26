# Baseline — Self-Hosted Health & Fitness Tracker

A personal health and fitness tracker built to run on your own hardware.
No cloud. No subscriptions. Your data stays on your device.

![Baseline](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![Flask](https://img.shields.io/badge/flask-3.x-lightgrey)
![Pi Compatible](https://img.shields.io/badge/raspberry%20pi-compatible-red)

---

## Features

- **Multi-profile support** — Netflix-style profile picker with optional PIN per profile
- **BMI calculator** — with personalized advice based on your result
- **Sleep schedule** — bedtime recommendations based on age, BMI, and stress level
- **Workout plans** — 6 goal-based plans (fat loss, muscle, cardio, flexibility, athletic, maintenance) with exercises for home or gym
- **Meal plans** — timed meal schedules with macros scaled to your calorie target
- **Calorie tracker** — log food with protein/carb/fat breakdown
- **Daily log** — weight, steps, sleep, water, heart rate, mood, workout
- **Health app import** — paste CSV or JSON from Apple Health, Fitbit, Garmin, etc.
- **History & charts** — weight, steps, sleep, and calorie trends over time
- **Auto-populate** — enter your data once in Profile; it fills everywhere else automatically
- **Light/dark mode** — per-device theme preference
- **Export** — download all your data as JSON anytime
- **Mobile-friendly** — responsive layout with slide-out nav on phones

---

## Self-Hosting on Raspberry Pi

### Requirements
- Raspberry Pi (any model — tested on Pi B+, 3, 4, 5)
- Raspberry Pi OS (Lite recommended)
- Python 3.9+

### Quick Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/baseline.git
cd baseline

# 2. Run the setup script
bash setup.sh
```

The setup script will:
- Install Flask
- Create the data directory
- Register Baseline as a systemd service (auto-starts on boot)
- Print your Pi's IP address

### Access

Open on any device on your home network:
```
http://<YOUR_PI_IP>:3000
```

---

## Remote Access (Optional)

For access outside your home network, use [Tailscale](https://tailscale.com) — a free, zero-config private VPN.

```bash
# On your Pi
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip  # note this address
```

Install Tailscale on your phone/laptop, sign in with the same account, then access Baseline from anywhere at `http://<TAILSCALE_IP>:3000`.

---

## Docker (Recommended for most users)

The easiest way to run Baseline on any machine with Docker installed.

### Quick start

```bash
git clone https://github.com/dzshafer/baseline.git
cd baseline/baseline
docker compose up -d
```

Then open http://localhost:3000

### Update to latest version

```bash
git pull
docker compose up -d --build
```

Your data in the `./data` folder is never touched during updates.

### Stop / restart

```bash
docker compose stop      # stop
docker compose start     # start again
docker compose down      # stop and remove container (data is safe)
```

### Change port

Edit `docker-compose.yml` and change `3000:3000` to e.g. `8080:3000`.

---

## Running Locally without Docker (Mac/PC)

```bash
pip3 install flask
python3 server.py
```

Then open http://localhost:3000

---

## Data Storage

All data is stored in `data/baseline.json` — a single plain JSON file on your device. It is **never sent anywhere**.

Back it up anytime:
```bash
cp data/baseline.json data/baseline.json.bak
```

---

## Updating

```bash
git pull
sudo systemctl restart baseline
```

---

## API

Baseline exposes a simple REST API for integrations:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profiles` | List all profiles |
| POST | `/api/profiles` | Create a profile |
| GET | `/api/profiles/:id/data` | Get all data for a profile |
| POST | `/api/profiles/:id/profile` | Save profile health data |
| POST | `/api/profiles/:id/logs` | Save a daily log entry |
| GET | `/api/profiles/:id/logs` | Get all log entries |
| POST | `/api/profiles/:id/food` | Add a food log entry |
| GET | `/api/profiles/:id/export` | Export profile data as JSON |
| GET | `/api/export` | Export all profiles as JSON |
| GET | `/api/health` | Server health check |

---

## License

MIT — free to use, modify, and share.
