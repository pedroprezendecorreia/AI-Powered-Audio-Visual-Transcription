"""
Transcription module using faster-whisper (CTranslate2 backend).

Chosen over openai-whisper because it is ~4x faster on CPU with int8
quantization, uses a fraction of the RAM, needs no PyTorch, and bundles
its own ffmpeg via PyAV. It also yields segments with timestamps, which
lets us report *real* progress instead of a fixed fake curve.
"""
import os
import threading
import time
from faster_whisper import WhisperModel

# UI passes "large"; faster-whisper's best large checkpoint is "large-v3".
_MODEL_ALIASES = {"large": "large-v3"}


class Transcriber:
    """
    Class for audio transcription using faster-whisper.
    """
    def __init__(self):
        self.transcription_thread = None
        self.is_transcribing = False
        self.model = None
        self.current_model_name = None
        self.current_device = None
        self.cancel_requested = False
        self.start_time = 0

    def transcribe(self, file_path, config, progress_callback=None, completion_callback=None, error_callback=None):
        """
        Starts transcription of an audio file (runs in a background thread).

        Args:
            file_path (str): Path to the audio file
            config (dict): Transcription settings (language, model, device)
            progress_callback (callable): called as (percent:int, status:str)
            completion_callback (callable): called as (text:str)
            error_callback (callable): called as (message:str)
        """
        if self.is_transcribing:
            if error_callback:
                error_callback("A transcription is already in progress.")
            return

        self.is_transcribing = True
        self.cancel_requested = False
        self.start_time = time.time()

        self.transcription_thread = threading.Thread(
            target=self._transcribe_thread,
            args=(file_path, config, progress_callback, completion_callback, error_callback)
        )
        self.transcription_thread.daemon = True
        self.transcription_thread.start()

    def _load_model(self, model_name, device):
        """
        Loads (and caches) a WhisperModel. On CPU we use int8 for speed and
        low memory; on CUDA we use float16. Falls back to CPU if a CUDA load
        fails (e.g. no NVIDIA runtime present).
        """
        resolved = _MODEL_ALIASES.get(model_name, model_name)

        if self.model is not None and self.current_model_name == model_name and self.current_device == device:
            return  # already loaded

        def _build(dev):
            compute_type = "float16" if dev == "cuda" else "int8"
            return WhisperModel(resolved, device=dev, compute_type=compute_type)

        try:
            self.model = _build(device)
            self.current_device = device
        except Exception:
            # CUDA requested but unavailable -> fall back to CPU int8.
            self.model = _build("cpu")
            self.current_device = "cpu"

        self.current_model_name = model_name

    def _transcribe_thread(self, file_path, config, progress_callback, completion_callback, error_callback):
        try:
            if not os.path.isfile(file_path):
                if error_callback:
                    error_callback(f"File not found: {file_path}")
                return

            model_name = config.get("model", "base")
            language = config.get("language", "auto")
            device = config.get("device", "cpu")

            if progress_callback:
                progress_callback(5, f"Loading model '{model_name}'...")

            self._load_model(model_name, device)

            if self.cancel_requested:
                return

            options = {
                "beam_size": 5,
                "vad_filter": True,  # skip silence -> faster + cleaner output
            }
            if language != "auto":
                options["language"] = language

            if progress_callback:
                progress_callback(10, "Analyzing audio...")

            # segments is a lazy generator; work happens as we iterate it.
            segments, info = self.model.transcribe(file_path, **options)
            duration = info.duration or 0

            text_parts = []
            for segment in segments:
                if self.cancel_requested:
                    return
                text_parts.append(segment.text)

                if progress_callback:
                    if duration > 0:
                        # Map audio position to the 10%..95% band.
                        pct = 10 + int((segment.end / duration) * 85)
                        pct = min(95, max(10, pct))
                        progress_callback(
                            pct,
                            f"Transcribing... {format_time(segment.end)} / {format_time(duration)}"
                        )
                    else:
                        progress_callback(50, "Transcribing...")

            if self.cancel_requested:
                return

            transcribed_text = "".join(text_parts).strip()

            if progress_callback:
                elapsed = time.time() - self.start_time
                progress_callback(100, f"Completed in {format_time(elapsed)}")

            if completion_callback:
                completion_callback(transcribed_text)

        except Exception as e:
            if error_callback:
                error_callback(f"Transcription error: {str(e)}")

        finally:
            self.is_transcribing = False

    def cancel(self):
        """
        Requests cancellation of the ongoing transcription.
        """
        if self.is_transcribing:
            self.cancel_requested = True
            return True
        return False


def format_time(seconds):
    """
    Formats a duration in seconds as a short human-readable string.
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}h {minutes}min {seconds}s"
    elif minutes > 0:
        return f"{minutes}min {seconds}s"
    else:
        return f"{seconds}s"


if __name__ == "__main__":
    # ponytail: smallest runnable check — timestamp->percent math must stay in band.
    def pct_for(end, duration):
        return min(95, max(10, 10 + int((end / duration) * 85)))
    assert pct_for(0, 100) == 10
    assert pct_for(100, 100) == 95
    assert pct_for(50, 100) == 52
    assert format_time(0) == "0s"
    assert format_time(65) == "1min 5s"
    assert format_time(3661) == "1h 1min 1s"
    print("transcriber self-check OK")
