import subprocess
from unittest.mock import MagicMock, patch

import pytest

from stt.vosk_stt import SttNotConfigured, _ffmpeg_path, transcribe_bytes


@pytest.mark.asyncio
async def test_ffmpeg_not_found():
    """Ensure error is raised if ffmpeg is missing."""
    with (
        patch("shutil.which", return_value=None),
        patch("os.path.isfile", return_value=False),
        patch.dict("os.environ", {}, clear=True),
    ):
        with pytest.raises(SttNotConfigured, match="FFmpeg not found"):
            _ffmpeg_path()


@pytest.mark.asyncio
async def test_transcribe_flow():
    """Test the transcription pipeline with mocked subprocess and model."""
    fake_audio = b"\x00" * 10

    # Mock ffmpeg path resolution
    with (
        patch("stt.vosk_stt._ffmpeg_path", return_value="/usr/bin/ffmpeg"),
        patch("stt.vosk_stt._get_model"),
        patch("subprocess.run") as mock_run,
    ):
        # Mock subprocess output (pcm data)
        mock_run.return_value.stdout = b"fake-pcm-data"

        # Mock Vosk Recognizer
        mock_rec_instance = MagicMock()
        mock_rec_instance.FinalResult.return_value = '{"text": "hello world"}'

        with patch("stt.vosk_stt.KaldiRecognizer", return_value=mock_rec_instance):
            result = await transcribe_bytes(fake_audio, "voice.ogg")

            assert result == "hello world"
            # Ensure ffmpeg was called with correct args
            args, _ = mock_run.call_args
            assert args[0][0] == "/usr/bin/ffmpeg"
            assert "-ar" in args[0] and "16000" in args[0]


@pytest.mark.asyncio
async def test_ffmpeg_path_with_env_var():
    """Test _ffmpeg_path with FFMPEG_BIN environment variable set."""
    with (
        patch.dict("os.environ", {"FFMPEG_BIN": "/custom/ffmpeg"}, clear=False),
        patch("os.path.isfile", return_value=True),
    ):
        from stt.vosk_stt import _ffmpeg_path

        path = _ffmpeg_path()
        assert path == "/custom/ffmpeg"


@pytest.mark.asyncio
async def test_ffmpeg_path_system_binary():
    """Test _ffmpeg_path finding system binary."""
    with patch.dict("os.environ", {}, clear=True), patch("shutil.which", return_value="/usr/bin/ffmpeg"):
        from stt.vosk_stt import _ffmpeg_path

        path = _ffmpeg_path()
        assert path == "/usr/bin/ffmpeg"


@pytest.mark.asyncio
async def test_ffmpeg_path_invalid_bin():
    """Test _ffmpeg_path with invalid FFMPEG_BIN."""
    with (
        patch.dict("os.environ", {"FFMPEG_BIN": "/invalid/path"}, clear=False),
        patch("os.path.isfile", return_value=False),
        patch("shutil.which", return_value=None),
    ):
        from stt.vosk_stt import SttNotConfigured, _ffmpeg_path

        with pytest.raises(SttNotConfigured, match="FFMPEG_BIN points to non-file"):
            _ffmpeg_path()


@pytest.mark.asyncio
async def test_get_model_invalid_path():
    """Test _get_model with invalid VOSK_MODEL_PATH."""
    with (
        patch.dict("os.environ", {"VOSK_MODEL_PATH": "/invalid/path"}, clear=False),
        patch("os.path.isdir", return_value=False),
        patch("stt.vosk_stt._model", None),
    ):
        from stt.vosk_stt import SttNotConfigured, _get_model

        with pytest.raises(SttNotConfigured, match="VOSK_MODEL_PATH invalid"):
            _get_model()


@pytest.mark.asyncio
async def test_decode_ffmpeg_file_not_found():
    """Test _decode_to_pcm16_mono16k_ffmpeg with FileNotFoundError."""
    with (
        patch("stt.vosk_stt._ffmpeg_path", return_value="/nonexistent/ffmpeg"),
        patch("subprocess.run", side_effect=FileNotFoundError()),
    ):
        from stt.vosk_stt import SttNotConfigured, _decode_to_pcm16_mono16k_ffmpeg

        with pytest.raises(SttNotConfigured, match="FFmpeg not found"):
            _decode_to_pcm16_mono16k_ffmpeg(b"data")


@pytest.mark.asyncio
async def test_decode_ffmpeg_process_error():
    """Test _decode_to_pcm16_mono16k_ffmpeg with CalledProcessError."""
    fake_error = subprocess.CalledProcessError(1, "ffmpeg")
    fake_error.stderr = b"Error: invalid input"

    with (
        patch("stt.vosk_stt._ffmpeg_path", return_value="/usr/bin/ffmpeg"),
        patch("subprocess.run", side_effect=fake_error),
    ):
        from stt.vosk_stt import SttNotConfigured, _decode_to_pcm16_mono16k_ffmpeg

        with pytest.raises(SttNotConfigured, match="FFmpeg decode error"):
            _decode_to_pcm16_mono16k_ffmpeg(b"data")


@pytest.mark.asyncio
async def test_transcribe_json_parse_error():
    """Test transcribe_bytes with JSON parse error."""
    fake_audio = b"\x00" * 10

    with (
        patch("stt.vosk_stt._ffmpeg_path", return_value="/usr/bin/ffmpeg"),
        patch("stt.vosk_stt._get_model"),
        patch("subprocess.run") as mock_run,
    ):
        mock_run.return_value.stdout = b"fake-pcm-data"

        mock_rec_instance = MagicMock()
        mock_rec_instance.FinalResult.return_value = "invalid json"

        with patch("stt.vosk_stt.KaldiRecognizer", return_value=mock_rec_instance):
            result = await transcribe_bytes(fake_audio, "voice.ogg")

            assert result == ""
