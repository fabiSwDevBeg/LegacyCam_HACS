# LegacyCam - Home Assistant HACS Integration

LegacyCam is a custom Home Assistant integration designed for simple IP cameras exposing:
- MJPEG stream
- Snapshot endpoint
- Flash control (on/off via HTTP)
- Video clip recording with retention management

---

## 📌 Features

- 📹 MJPEG live stream support
- 📸 Snapshot support
- 💡 Flash ON/OFF switch via HTTP endpoints
- 🎥 FFmpeg-based clip recording
- 🧠 Automatic retention management (based on hours + clip duration)
- ⚙️ Fully configurable via Home Assistant UI (Config Flow)

---

## 📷 Supported Camera Endpoints

Your device must expose:

```
http://DEVICE_IP:8080/stream
http://DEVICE_IP:8080/snapshot.jpg
http://DEVICE_IP:8080/flash/on
http://DEVICE_IP:8080/flash/off
```

---

## ⚙️ Installation (HACS)

### 1. Add custom repository
- Go to HACS → Integrations
- Add custom repository
- URL: your GitHub repo
- Category: Integration

### 2. Install LegacyCam
- Search "LegacyCam"
- Install
- Restart Home Assistant

---

## 🧩 Configuration

When adding the integration, you must provide:

### Required
- **IP Address** of the camera

### Advanced options
- Clip duration (seconds): `5 - 300`
- Retention time (hours): `1 - 168`

---

## 🧠 Retention Logic

LegacyCam automatically calculates how many video snippets to keep:

```
snippets = ceil(retention_seconds / clip_seconds)
```

Example:
- Clip duration: 190 seconds
- Retention: 1 hour (3600 seconds)

```
3600 / 190 = 18.94 → 19 clips retained
```

Older clips are automatically deleted.

---

## 📁 Storage

All recordings are stored in:

```
/config/www/legacycam/
```

---

## 🎥 Recording

You can trigger clip recording via service:

```yaml
service: legacycam.record_clip
data:
  duration: 10
```

---

## 💡 Flash Control

A switch is created:

- `switch.legacycam_flash`

It calls:
- ON → `/flash/on`
- OFF → `/flash/off`

---

## 📸 Snapshot

Snapshot is available via camera entity or service:

```
legacycam.snapshot
```

---

## 📹 Camera Entity

```
camera.legacycam
```

Supports MJPEG streaming.

---

## ⚠️ Requirements

- Home Assistant 2024+
- FFmpeg installed in HA
- Device reachable via HTTP

---

## 🚀 Roadmap

- Stream proxy optimization
- Rotation filter support (90/180/270)
- Motion detection events
- Continuous recording mode (NVR-like)
- Lovelace custom card

---

## ❤️ Notes

This integration is designed for lightweight IP cameras exposing simple HTTP endpoints.