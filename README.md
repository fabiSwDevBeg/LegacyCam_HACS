# LegacyCam - Home Assistant Integration

LegacyCam is a HACS integration for an iPhone 4 running the LegacyCam backend. It treats the phone as one Home Assistant device with a camera entity, flash switch, online/motion binary sensors, lightweight status sensors, motion detection, and optional fragmented recording.

## Architecture Proposal

- `config_flow.py`: collects device name and IP address; options configure motion and recording.
- `coordinator.py`: polls `/status` every 30 seconds.
- `coordinator.py`: also supervises MJPEG motion analysis, flash-on-motion, FFmpeg recording, and retention cleanup.
- `camera.py`: exposes the MJPEG stream through Home Assistant camera architecture.
- `switch.py`: controls flash, motion detection, and recording.
- `sensor.py`: exposes uptime, stream clients, backend version, and motion score.
- `binary_sensor.py`: exposes online and motion status.
- `util.py` and `const.py`: centralize endpoint generation and constants.

## Folder Structure Proposal

```text
custom_components/legacycam/
  __init__.py
  binary_sensor.py
  camera.py
  config_flow.py
  const.py
  coordinator.py
  sensor.py
  switch.py
  util.py
  manifest.json
```

## Refactor Plan

1. Use `/ping` in the config flow for cheap connection testing.
2. Use one `DataUpdateCoordinator` for `/status` polling.
3. Make every entity share the same `device_info`.
4. Keep raw backend URLs out of user configuration.
5. Keep motion and recording in Home Assistant so the iOS 7 backend only has to stream frames and control the flash.

## Entities

- `camera.legacycam`
- `switch.legacycam_flash`
- `switch.legacycam_motion_detection`
- `switch.legacycam_recording`
- `binary_sensor.legacycam_online`
- `binary_sensor.legacycam_motion`
- `sensor.legacycam_uptime`
- `sensor.legacycam_stream_clients`
- `sensor.legacycam_version`
- `sensor.legacycam_motion_score`

## Motion Detection

Motion detection samples the MJPEG stream in Home Assistant, compares downscaled grayscale frames, and turns on the phone flash when motion is detected. The flash is turned off again after the configured hold time if LegacyCam was the component that turned it on.

Options:

- Motion threshold: default `6`, expressed as a 0-100 frame-difference score.
- Motion sample interval: default `1.0` second.
- Motion flash hold seconds: default `10`.

## Recording

Recording uses the local `ffmpeg` binary to save segmented MP4 files from the MJPEG stream.

Options:

- Fragment duration: `5` to `300` seconds, default `30`.
- Retention: minimum `1` hour, default `2`. There is no hard upper limit in the options schema.
- Recording path: default `www/legacycam`, resolved under Home Assistant's `/config` directory. In Docker this normally lives on the Home Assistant config volume; in Home Assistant OS/standalone it remains inside the persistent config directory. Absolute paths are accepted for advanced installs.

Generated files use this pattern:

```text
legacycam_YYYYMMDD_HHMMSS.mp4
```

## Breaking Changes

- Recording settings moved to the integration options flow.
- Motion detection and recording are controlled by switch entities.
- Flash switch state is no longer local; it is read from `/status`.
- The backend must expose `/ping`, `/status`, and `/flash/status`.

## Migration Steps

1. Update the iPhone backend first.
2. Update this HACS integration and restart Home Assistant.
3. If an existing config entry has old clip/retention fields, it can remain; they are ignored.
4. Update dashboards to use the camera and switch entities instead of raw backend URLs.

## Supported Backend Endpoints

```text
http://DEVICE_IP:8080/ping
http://DEVICE_IP:8080/status
http://DEVICE_IP:8080/stream
http://DEVICE_IP:8080/flash/on
http://DEVICE_IP:8080/flash/off
http://DEVICE_IP:8080/flash/status
```
