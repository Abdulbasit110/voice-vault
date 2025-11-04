import os
import requests
import base64
import io
import uuid
from io import BytesIO
from typing import Optional
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

load_dotenv()

class ElevenLabsSDK:
    """
    ElevenLabs SDK wrapper for Speech-to-Text (STT) and Text-to-Speech (TTS)
    Uses the official elevenlabs Python package
    """
    
    def __init__(self):
        # self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.api_key = "sk_e1358deb38395e1619c9ee899292379eee9df6fc30c7cdd9"
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
        
        # Initialize the official ElevenLabs client
        self.client = ElevenLabs(api_key=self.api_key)
        
        # Keep base_url for STT requests (if needed)
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key
        }
    
    def speech_to_text(self, audio_data: bytes, model_id: Optional[str] = None) -> str:
        """
        Convert audio to text using ElevenLabs STT via official SDK.
        
        Args:
            audio_data: Audio file bytes (wav, mp3, webm, etc.)
            model_id: Model ID to use (default: "scribe_v1")
        
        Returns:
            Transcribed text
        """
        if isinstance(audio_data, str):
            audio_data = base64.b64decode(audio_data)
        print("audio_data")
        # 1) Save incoming audio to local directory for debugging/auditing
        # try:
        #     save_path = self._save_incoming_audio(audio_data)
        #     print("save_path",save_path)
        #     # Optional: print or log path; avoid noisy logs in production
        #     # print(f"Saved incoming audio to {save_path}")
        # except Exception as e:
        #     # Don't fail STT if saving fails
        #     print(f"Error saving incoming audio: {e}")
        #     pass

        model = model_id or "scribe_v1"

        # Use file-like object as required by SDK
        file_like = BytesIO(audio_data)
        print("file_like",file_like)
        transcription = self.client.speech_to_text.convert(
            file=file_like,
            model_id=model,
            tag_audio_events=True,
            language_code="eng",  # auto-detect
            diarize=True,
        )
        print("transcription",transcription)

        # SDK may return a dict-like or object; try common accessors
        try:
            # Pydantic model style
            if hasattr(transcription, "text"):
                return transcription.text or ""
            if hasattr(transcription, "model_dump"):
                data = transcription.model_dump()
                return data.get("text", "")
        except Exception:
            pass

        # Fallback if it's a dict
        if isinstance(transcription, dict):
            return transcription.get("text", "")

        # Last resort: string cast
        return str(transcription) or ""

    def _save_incoming_audio(self, audio_bytes: bytes) -> str:
        """
        Save received audio bytes to a local uploads directory and return the file path.

        The method tries to infer a reasonable file extension from magic bytes.
        """
        # Detect extension from magic bytes
        ext = self._detect_audio_extension(audio_bytes)
        uploads_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "audio")
        os.makedirs(uploads_root, exist_ok=True)

        filename = f"incoming_{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(uploads_root, filename)

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        return file_path

    def _detect_audio_extension(self, audio_bytes: bytes) -> str:
        """
        Best-effort detection of audio type based on common magic bytes.
        Defaults to 'bin' if unknown.
        """
        if len(audio_bytes) < 12:
            return "bin"

        header = audio_bytes[:12]

        # WAV: 'RIFF' .... 'WAVE'
        if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
            return "wav"

        # MP3: 'ID3' or 0xFF 0xFB frame sync
        if header[:3] == b"ID3" or (header[0] == 0xFF and (header[1] & 0xE0) == 0xE0):
            return "mp3"

        # WebM/Matroska: 0x1A45DFA3
        if header[:4] == bytes([0x1A, 0x45, 0xDF, 0xA3]):
            return "webm"

        # Ogg: 'OggS'
        if header[:4] == b"OggS":
            return "ogg"

        # AAC ADTS: 0xFF 0xF1 or 0xFF 0xF9
        if header[0] == 0xFF and header[1] in (0xF1, 0xF9):
            return "aac"

        return "bin"
    
    def text_to_speech(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.8,
        style: float = 0.0,
        use_speaker_boost: bool = True,
        speed: float = 1.0,
        output_format: str = "mp3_22050_32"
    ) -> bytes:
        """
        Convert text to speech using ElevenLabs TTS API
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (defaults to Adam voice: pNInz6obpgDQGcFmaJgB)
            model_id: Model ID (default: eleven_multilingual_v2)
            stability: Stability setting (0.0-1.0)
            similarity_boost: Similarity boost (0.0-1.0)
            style: Style setting (0.0-1.0)
            use_speaker_boost: Whether to use speaker boost
            speed: Speech speed (0.25-4.0)
            output_format: Audio output format (default: mp3_22050_32)
        
        Returns:
            Audio bytes (MP3 format)
        """
        if not voice_id:
            # Default to Adam voice (pNInz6obpgDQGcFmaJgB) if not provided
            voice_id = "pNInz6obpgDQGcFmaJgB"
        
        # Convert text to speech using official SDK
        response = self.client.text_to_speech.convert(
            voice_id=voice_id,
            output_format=output_format,
            text=text,
            model_id=model_id,
            voice_settings=VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost,
                speed=speed,
            ),
        )
        
        # Collect all audio chunks into bytes
        audio_bytes = io.BytesIO()
        for chunk in response:
            if chunk:
                audio_bytes.write(chunk)
        
        return audio_bytes.getvalue()
    
    def get_voices(self) -> list:
        """
        Get list of available voices
        
        Returns:
            List of voice objects
        """
        voices = self.client.voices.get_all()
        # Convert to list of dictionaries if needed
        return [voice.model_dump() if hasattr(voice, 'model_dump') else voice for voice in voices.voices]
    
    def get_default_voice_id(self) -> str:
        """
        Get the default voice ID (Adam voice: pNInz6obpgDQGcFmaJgB)
        
        Returns:
            Voice ID string
        """
        # Return default Adam voice
        return "pNInz6obpgDQGcFmaJgB"
    
    def convert_base64_audio_to_text(self, base64_audio: str) -> str:
        """
        Helper method to convert base64 encoded audio string to text
        
        Args:
            base64_audio: Base64 encoded audio string
        
        Returns:
            Transcribed text
        """
        audio_bytes = base64.b64decode(base64_audio)
        return self.speech_to_text(audio_bytes)
    
    def text_to_speech_base64(self, text: str, voice_id: Optional[str] = None) -> str:
        """
        Convert text to speech and return as base64 encoded string
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (optional)
        
        Returns:
            Base64 encoded audio string
        """
        audio_bytes = self.text_to_speech(text, voice_id)
        return base64.b64encode(audio_bytes).decode('utf-8')
    
    def text_to_speech_file(
        self,
        text: str,
        output_path: Optional[str] = None,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.8,
        style: float = 0.0,
        use_speaker_boost: bool = True,
        speed: float = 1.0,
        output_format: str = "mp3_22050_32"
    ) -> str:
        """
        Convert text to speech and save to file
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file (if None, generates unique filename)
            voice_id: Voice ID to use (optional)
            model_id: Model ID (default: eleven_multilingual_v2)
            stability: Stability setting (0.0-1.0)
            similarity_boost: Similarity boost (0.0-1.0)
            style: Style setting (0.0-1.0)
            use_speaker_boost: Whether to use speaker boost
            speed: Speech speed (0.25-4.0)
            output_format: Audio output format (default: mp3_22050_32)
        
        Returns:
            Path to the saved audio file
        """
        if not output_path:
            output_path = f"transcript_audio_{uuid.uuid4()}.mp3"
        
        if not voice_id:
            voice_id = "pNInz6obpgDQGcFmaJgB"
        
        # Convert text to speech using official SDK
        response = self.client.text_to_speech.convert(
            voice_id=voice_id,
            output_format=output_format,
            text=text,
            model_id=model_id,
            voice_settings=VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost,
                speed=speed,
            ),
        )
        
        # Save to file
        with open(output_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        
        return output_path


# Singleton instance
_elevenlabs_instance: Optional[ElevenLabsSDK] = None

def get_elevenlabs_client() -> ElevenLabsSDK:
    """
    Get or create ElevenLabs SDK singleton instance
    
    Returns:
        ElevenLabsSDK instance
    """
    global _elevenlabs_instance
    if _elevenlabs_instance is None:
        _elevenlabs_instance = ElevenLabsSDK()
    return _elevenlabs_instance

