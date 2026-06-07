# LegacyCam - Home Assistant Integration

LegacyCam is a HACS integration for an iPhone 4 running the LegacyCam backend. It treats the phone as one Home Assistant device with a camera entity, flash switch, online binary sensor, and lightweight status sensors.

## Architecture Proposal

- `config_flow.py`: collects only device name and IP address.
- `coordinator.py`: polls `/status` every 30 seconds.
- `camera.py`: exposes the MJPEG stream and snapshot through Home Assistant camera architecture.
- `switch.py`: controls flash through `/flash/on` and `/flash/off`; state comes from coordinator data.
- `sensor.py`: exposes uptime, stream clients, and backend version.
- `binary_sensor.py`: exposes online status.
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
5. Remove unused flash services, clip recording, and retention settings until there is a clear active workflow for them.

## Entities

- `camera.legacycam`
- `switch.legacycam_flash`
- `binary_sensor.legacycam_online`
- `sensor.legacycam_uptime`
- `sensor.legacycam_stream_clients`
- `sensor.legacycam_version`

## Breaking Changes

- Config flow no longer asks for clip duration or retention hours.
- Unused services and FFmpeg clip recording code were removed.
- Flash switch state is no longer local; it is read from `/status`.
- The backend must expose `/ping`, `/status`, and `/flash/status`.

## Migration Steps

1. Update the iPhone backend first.
2. Update this HACS integration and restart Home Assistant.
3. If an existing config entry has old clip/retention fields, it can remain; they are ignored.
4. Update dashboards to use the camera and switch entities instead of raw stream or snapshot URLs.

## Supported Backend Endpoints

```text
http://DEVICE_IP:8080/ping
http://DEVICE_IP:8080/status
http://DEVICE_IP:8080/stream
http://DEVICE_IP:8080/snapshot.jpg
http://DEVICE_IP:8080/flash/on
http://DEVICE_IP:8080/flash/off
http://DEVICE_IP:8080/flash/status
```
