import asyncio
import contextlib
import io
import logging
import os
import shutil
import time
from datetime import timedelta
from pathlib import Path

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_MOTION_FLASH_HOLD_SECONDS,
    CONF_MOTION_SAMPLE_INTERVAL,
    CONF_MOTION_THRESHOLD,
    CONF_RECORDING_PATH,
    CONF_RECORDING_RETENTION_HOURS,
    CONF_RECORDING_SEGMENT_SECONDS,
    DEFAULT_MOTION_FLASH_HOLD_SECONDS,
    DEFAULT_MOTION_SAMPLE_INTERVAL,
    DEFAULT_MOTION_THRESHOLD,
    DEFAULT_RECORDING_PATH,
    DEFAULT_RECORDING_RETENTION_HOURS,
    DEFAULT_RECORDING_SEGMENT_SECONDS,
    DEFAULT_TIMEOUT,
    ENDPOINT_FLASH_OFF,
    ENDPOINT_FLASH_ON,
    ENDPOINT_STATUS,
    ENDPOINT_STREAM,
    UPDATE_INTERVAL_SECONDS,
)
from .util import endpoint_url

_LOGGER = logging.getLogger(__name__)


class LegacyCamCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, ip, entry):
        self.hass = hass
        self.ip = ip
        self.entry = entry
        self.session = async_get_clientsession(hass)

        self.motion_detection_enabled = False
        self.motion_detected = False
        self.motion_score = 0
        self.recording_enabled = False
        self.recording_error = ""

        self._motion_task = None
        self._recording_task = None
        self._retention_task = None
        self._recording_process = None
        self._motion_flash_owned = False
        self._flash_until = 0

        super().__init__(
            hass,
            logger=_LOGGER,
            name="legacycam",
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

    async def async_shutdown(self):
        await self.async_set_motion_detection_enabled(False)
        await self.async_set_recording_enabled(False)

    async def async_options_updated(self):
        if self.recording_enabled:
            await self.async_set_recording_enabled(False)
            await self.async_set_recording_enabled(True)

    async def async_set_motion_detection_enabled(self, enabled):
        enabled = bool(enabled)

        if enabled == self.motion_detection_enabled:
            return

        self.motion_detection_enabled = enabled

        if enabled:
            self._motion_task = self.hass.loop.create_task(self._motion_loop())
        else:
            await self._cancel_task("_motion_task")
            self.motion_detected = False
            self.motion_score = 0

            if self._motion_flash_owned:
                await self._set_flash(False)
                self._motion_flash_owned = False

        self._publish_runtime_state()

    async def async_set_recording_enabled(self, enabled):
        enabled = bool(enabled)

        if enabled == self.recording_enabled:
            return

        self.recording_enabled = enabled
        self.recording_error = ""

        if enabled:
            if not shutil.which("ffmpeg"):
                self.recording_enabled = False
                self.recording_error = "ffmpeg_not_found"
                self._publish_runtime_state()
                return

            self._recording_task = self.hass.loop.create_task(self._recording_loop())
            self._retention_task = self.hass.loop.create_task(self._retention_loop())
        else:
            await self._cancel_task("_recording_task")
            await self._cancel_task("_retention_task")
            await self._stop_recording_process()

        self._publish_runtime_state()

    async def _async_update_data(self):
        url = endpoint_url(self.ip, ENDPOINT_STATUS)

        try:
            async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status != 200:
                    return self._with_runtime_data(self._offline_data())

                payload = await response.json(content_type=None)

                return self._with_runtime_data({
                    "online": bool(payload.get("online", True)),
                    "flash": bool(payload.get("flash", False)),
                    "uptime": payload.get("uptime"),
                    "version": payload.get("version", ""),
                    "device": payload.get("device", ""),
                    "stream_clients": int(payload.get("stream_clients", 0)),
                })
        except Exception as err:
            _LOGGER.debug("LegacyCam status update failed: %s", err)
            return self._with_runtime_data(self._offline_data())

    def _offline_data(self):
        return {
            "online": False,
            "flash": False,
            "uptime": None,
            "version": "",
            "device": "",
            "stream_clients": 0,
        }

    def _with_runtime_data(self, data):
        return {
            **data,
            "motion_detection": self.motion_detection_enabled,
            "motion_detected": self.motion_detected,
            "motion_score": self.motion_score,
            "recording": self.recording_enabled,
            "recording_path": str(self.recording_path),
            "recording_error": self.recording_error,
        }

    def _publish_runtime_state(self):
        base = self.data or self._offline_data()
        self.async_set_updated_data(self._with_runtime_data(base))

    async def _motion_loop(self):
        previous = None
        buffer = bytearray()
        last_sample = 0

        while self.motion_detection_enabled:
            try:
                async with self.session.get(
                    endpoint_url(self.ip, ENDPOINT_STREAM),
                    timeout=None,
                ) as response:
                    async for chunk in response.content.iter_chunked(4096):
                        if not self.motion_detection_enabled:
                            return

                        buffer.extend(chunk)

                        for frame in self._extract_jpeg_frames(buffer):
                            now = time.monotonic()
                            if now - last_sample < self.motion_sample_interval:
                                continue

                            last_sample = now
                            signature = await self.hass.async_add_executor_job(
                                _frame_signature,
                                bytes(frame),
                            )

                            if signature is None:
                                continue

                            if previous is not None:
                                await self._handle_motion_score(
                                    _frame_difference(previous, signature)
                                )

                            previous = signature
            except asyncio.CancelledError:
                raise
            except Exception as err:
                _LOGGER.debug("LegacyCam motion stream failed: %s", err)
                await asyncio.sleep(5)

    async def _handle_motion_score(self, score):
        threshold = self.motion_threshold
        detected = score >= threshold
        changed = detected != self.motion_detected or int(score) != self.motion_score

        self.motion_score = int(score)
        self.motion_detected = detected

        if detected:
            self._flash_until = time.monotonic() + self.motion_flash_hold_seconds

            if not self._motion_flash_owned and not bool((self.data or {}).get("flash")):
                await self._set_flash(True)
                self._motion_flash_owned = True

        if (
            self._motion_flash_owned
            and not detected
            and time.monotonic() >= self._flash_until
        ):
            await self._set_flash(False)
            self._motion_flash_owned = False

        if changed:
            self._publish_runtime_state()

    @staticmethod
    def _extract_jpeg_frames(buffer):
        frames = []

        while True:
            start = buffer.find(b"\xff\xd8")
            if start < 0:
                if len(buffer) > 1024 * 1024:
                    del buffer[:-2]
                break

            end = buffer.find(b"\xff\xd9", start + 2)
            if end < 0:
                if start > 0:
                    del buffer[:start]
                break

            frame_end = end + 2
            frames.append(bytes(buffer[start:frame_end]))
            del buffer[:frame_end]

        return frames

    async def _recording_loop(self):
        ffmpeg = shutil.which("ffmpeg")

        if not ffmpeg:
            self.recording_error = "ffmpeg_not_found"
            self.recording_enabled = False
            self._publish_runtime_state()
            return

        while self.recording_enabled:
            try:
                await self.hass.async_add_executor_job(self._ensure_recording_path)
                await self.hass.async_add_executor_job(self._cleanup_old_recordings)

                output_pattern = str(self.recording_path / "legacycam_%Y%m%d_%H%M%S.mp4")
                args = [
                    ffmpeg,
                    "-hide_banner",
                    "-loglevel",
                    "warning",
                    "-i",
                    endpoint_url(self.ip, ENDPOINT_STREAM),
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-pix_fmt",
                    "yuv420p",
                    "-f",
                    "segment",
                    "-segment_time",
                    str(self.recording_segment_seconds),
                    "-reset_timestamps",
                    "1",
                    "-strftime",
                    "1",
                    output_pattern,
                ]

                self._recording_process = await asyncio.create_subprocess_exec(
                    *args,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                self.recording_error = ""
                self._publish_runtime_state()

                return_code = await self._recording_process.wait()
                self._recording_process = None

                if self.recording_enabled:
                    self.recording_error = f"ffmpeg_exited_{return_code}"
                    self._publish_runtime_state()
                    await asyncio.sleep(5)
            except asyncio.CancelledError:
                raise
            except Exception as err:
                _LOGGER.warning("LegacyCam recording failed: %s", err)
                self.recording_error = "recording_failed"
                self._publish_runtime_state()
                await asyncio.sleep(10)

    async def _retention_loop(self):
        while self.recording_enabled:
            try:
                await self.hass.async_add_executor_job(self._cleanup_old_recordings)
            except Exception as err:
                _LOGGER.debug("LegacyCam retention cleanup failed: %s", err)

            await asyncio.sleep(300)

    def _cleanup_old_recordings(self):
        path = self.recording_path
        if not path.exists():
            return

        cutoff = time.time() - (self.recording_retention_hours * 3600)

        for clip in path.glob("legacycam_*.mp4"):
            with contextlib.suppress(OSError):
                if clip.stat().st_mtime < cutoff:
                    clip.unlink()

    def _ensure_recording_path(self):
        self.recording_path.mkdir(parents=True, exist_ok=True)

    async def _set_flash(self, enabled):
        path = ENDPOINT_FLASH_ON if enabled else ENDPOINT_FLASH_OFF

        try:
            async with self.session.get(endpoint_url(self.ip, path), timeout=DEFAULT_TIMEOUT):
                pass

            base = self.data or self._offline_data()
            self.async_set_updated_data(self._with_runtime_data({
                **base,
                "flash": enabled,
            }))
        except Exception as err:
            _LOGGER.debug("LegacyCam flash update failed: %s", err)

    async def _cancel_task(self, attribute):
        task = getattr(self, attribute)
        setattr(self, attribute, None)

        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def _stop_recording_process(self):
        process = self._recording_process
        self._recording_process = None

        if not process or process.returncode is not None:
            return

        process.terminate()

        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(process.wait(), timeout=5)
            return

        process.kill()
        await process.wait()

    @property
    def recording_segment_seconds(self):
        return int(self.entry.options.get(
            CONF_RECORDING_SEGMENT_SECONDS,
            DEFAULT_RECORDING_SEGMENT_SECONDS,
        ))

    @property
    def recording_retention_hours(self):
        return int(self.entry.options.get(
            CONF_RECORDING_RETENTION_HOURS,
            DEFAULT_RECORDING_RETENTION_HOURS,
        ))

    @property
    def recording_path(self):
        configured = self.entry.options.get(CONF_RECORDING_PATH, DEFAULT_RECORDING_PATH)
        expanded = os.path.expanduser(configured)

        if os.path.isabs(expanded):
            return Path(expanded)

        return Path(self.hass.config.path(expanded))

    @property
    def motion_threshold(self):
        return int(self.entry.options.get(CONF_MOTION_THRESHOLD, DEFAULT_MOTION_THRESHOLD))

    @property
    def motion_sample_interval(self):
        return float(self.entry.options.get(
            CONF_MOTION_SAMPLE_INTERVAL,
            DEFAULT_MOTION_SAMPLE_INTERVAL,
        ))

    @property
    def motion_flash_hold_seconds(self):
        return int(self.entry.options.get(
            CONF_MOTION_FLASH_HOLD_SECONDS,
            DEFAULT_MOTION_FLASH_HOLD_SECONDS,
        ))


def _frame_signature(frame):
    try:
        from PIL import Image

        with Image.open(io.BytesIO(frame)) as image:
            grayscale = image.convert("L").resize((32, 24))
            return grayscale.tobytes()
    except Exception as err:
        _LOGGER.debug("LegacyCam frame decode failed: %s", err)
        return None


def _frame_difference(previous, current):
    if len(previous) != len(current) or not previous:
        return 0

    total = sum(abs(a - b) for a, b in zip(previous, current))
    return (total / len(previous)) / 255 * 100
