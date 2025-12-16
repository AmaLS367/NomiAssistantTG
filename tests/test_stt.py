import pytest
import subprocess
from unittest.mock import patch, MagicMock
from stt.vosk_stt import transcribe_bytes, SttNotConfigured, _ffmpeg_path

@pytest.mark.asyncio
async def test_ffmpeg_not_found():
    """Ensure error is raised if ffmpeg is missing."""
    with patch("shutil.which", return_value=None), \
         patch("os.path.isfile", return_value=False), \
         patch.dict("os.environ", {}, clear=True):
        
        with pytest.raises(SttNotConfigured, match="FFmpeg not found"):
            _ffmpeg_path()

@pytest.mark.asyncio
async def test_transcribe_flow():
    """Test the transcription pipeline with mocked subprocess and model."""
    fake_audio = b"\x00" * 10
    
    # Mock ffmpeg path resolution
    with patch("stt.vosk_stt._ffmpeg_path", return_value="/usr/bin/ffmpeg"), \
         patch("stt.vosk_stt._get_model") as mock_model_loader, \
         patch("subprocess.run") as mock_run:
         
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

