> [!IMPORTANT]
> **This project has moved.** Active development of DEJA.js and the Track & Trestle model
> railroad platform now happens in private repositories under
> [**Track and Trestle Technology, LLC**](https://github.com/trackandtrestle).
> This repository stays public as a historical snapshot and is no longer maintained.
>
> **Current product, docs, and downloads → [dejajs.com](https://dejajs.com)**

# 🐍 Layout Conductor — Python API

**Flask REST API that drives model railroad hardware from a Raspberry Pi.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/MQTT-660066?style=for-the-badge&logo=mqtt&logoColor=white" />
  <img src="https://img.shields.io/badge/Raspberry_Pi-A22846?style=for-the-badge&logo=raspberrypi&logoColor=white" />
</p>

The hardware bridge for [`layout-conductor-app`](https://github.com/jmcdannel/layout-conductor-app).
Runs on a Raspberry Pi wired to a DCC++ command station, Arduinos, and GPIO accessories,
and exposes the whole railroad as a small REST surface.

## 🛣️ API surface

Each domain is a Flask blueprint registered against a shared device configuration:

| Blueprint | Controls |
|-----------|----------|
| `locos/` | Locomotive speed, direction, and functions |
| `turnouts/` | Servo and relay turnout throws |
| `sensors/` | Block occupancy and detection inputs |
| `signals/` | Signal aspects |
| `effects/` | Lighting, sound, and accessory outputs |
| `routes/` | Named multi-turnout paths thrown as one call |
| `config/` | Per-layout device definitions (`layouts.json`, per-site folders) |

`GET /` returns the active layout configuration, so a client can discover the railroad's
capabilities at startup rather than hard-coding them.

## 🏗️ How it works

```
Browser (React)  ──HTTP──▶  Flask API  ──┬── serial ──▶  DCC++ command station
                                         ├── serial ──▶  Arduino accessory boards
                                         ├── MQTT   ──▶  Pico W / ESP nodes
                                         └── GPIO   ──▶  relays, servos, signals
```

`mclient.py` and `mpub.py` handle the MQTT side; `ports.py` manages serial device discovery
so the API keeps working when USB enumeration order changes between boots.

## 🧑‍💻 Running it

```bash
pip install flask flask-cors pyserial paho-mqtt
python api.py           # serves on 0.0.0.0
```

Set `device_id` in `api.py` to select which entry in `config/layouts.json` to load.

## 📌 Status

Retired in favour of Node and Deno backends, then MQTT throughout. Kept public because the
per-layout configuration model it introduced — describe the hardware in data, not in code —
carried all the way into [DEJA.js](https://github.com/jmcdannel/DEJA.js).

## 🧭 Where this fits

This repo is one step in a long-running line of model railroad control software:

| Era | Project | What changed |
|-----|---------|--------------|
| 2020 | [`train-control`](https://github.com/jmcdannel/train-control) | First React throttle, JMRI + Arduino over HTTP |
| 2021 | [`dctc`](https://github.com/jmcdannel/dctc) | Standalone Arduino DC controller (no computer required) |
| 2022–23 | [`layout-conductor-*`](https://github.com/jmcdannel?tab=repositories&q=layout-conductor) | Split into app + API; Python, Node, and Deno backends explored |
| 2024 | [`Track-and-Trestle-Technology-Suite`](https://github.com/jmcdannel/Track-and-Trestle-Technology-Suite) | MQTT-based monorepo: dispatcher, throttle, dashboard, action API |
| 2024–25 | [`DEJA.js`](https://github.com/jmcdannel/DEJA.js) | TypeScript/Turborepo rewrite, Firebase realtime backbone |
| 2025– | **[dejajs.com](https://dejajs.com)** (private) | Commercial cloud platform for DCC-EX |

---

<sub>Built by [Josh McDannel](https://github.com/jmcdannel) · [dejajs.com](https://dejajs.com) · [LinkedIn](https://www.linkedin.com/in/jmcdannel)</sub>
