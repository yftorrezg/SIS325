"""
faster-whisper speech-to-text transcription.
Lazy-loaded to save VRAM when not in use.
faster-whisper uses CTranslate2 backend: 4x faster, less VRAM than openai-whisper.
"""
import asyncio
import logging
import time
import torch
from app.config import settings

logger = logging.getLogger(__name__)


class TranscriberModel:
    def __init__(self):
        self._model = None
        self.is_loaded = False
        self._last_used = 0
        self._idle_timeout = 120  # seconds before auto-unload
        self._device = "cuda" if (settings.use_gpu and torch.cuda.is_available()) else "cpu"
        self._compute_type = "float16" if self._device == "cuda" else "int8"

    def _load(self):
        from faster_whisper import WhisperModel
        logger.info(f"Loading faster-whisper {settings.whisper_model} on {self._device} ({self._compute_type})")
        self._model = WhisperModel(
            settings.whisper_model,
            device=self._device,
            compute_type=self._compute_type,
        )
        self.is_loaded = True
        logger.info("faster-whisper loaded")

    def _ensure_loaded(self):
        if not self.is_loaded:
            self._load()
        self._last_used = time.time()

    async def transcribe(self, audio_path: str) -> dict:
        """Transcribe audio file to text."""
        await asyncio.get_event_loop().run_in_executor(None, self._ensure_loaded)

        def _transcribe():
            segments, info = self._model.transcribe(
                audio_path,
                language="es",
                task="transcribe",
                beam_size=5,
            )
            segments_list = list(segments)  # consume generator
            text = " ".join(s.text.strip() for s in segments_list)
            duration = segments_list[-1].end if segments_list else 0.0
            return text, info.language, duration

        text, language, duration = await asyncio.get_event_loop().run_in_executor(None, _transcribe)
        return {
            "text": text.strip(),
            "language": language,
            "duration": round(duration, 2),
        }

    def maybe_unload(self):
        """Unload if idle for too long."""
        if self.is_loaded and (time.time() - self._last_used > self._idle_timeout):
            logger.info("Whisper idle timeout, unloading")
            self._model = None
            self.is_loaded = False
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


# Global singleton
transcriber_model = TranscriberModel()
