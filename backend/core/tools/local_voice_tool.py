"""
Local Voice Tool - FREE voice capabilities

Provides text-to-speech (TTS) and speech-to-text (STT) using free services:
- TTS: edge-tts (Microsoft Edge TTS - completely FREE)
- STT: Whisper (via OpenAI API or local Whisper.cpp)
"""

from core.agentpress.tool import Tool, ToolResult, openapi_schema, tool_metadata, method_metadata
from core.agentpress.thread_manager import ThreadManager
from core.sandbox.tool_base import SandboxToolsBase
from core.utils.logger import logger
from core.utils.config import config
from typing import List, Dict, Any, Optional
import json
import base64
import asyncio


@tool_metadata(
    display_name="Voice (Local)",
    description="Free text-to-speech and speech-to-text using Edge TTS and Whisper",
    icon="Mic",
    color="bg-purple-100 dark:bg-purple-800/50",
    weight=65,
    visible=True,
    is_core=False
)
class LocalVoiceTool(SandboxToolsBase):
    """
    Local Voice Tool - completely free voice capabilities.
    
    Features:
    - Text-to-Speech using Microsoft Edge TTS (free, no API key)
    - Speech-to-Text using Whisper (OpenAI API or local)
    - Multiple voices and languages
    - High quality audio output
    """

    def __init__(self, project_id: str, thread_manager: ThreadManager):
        super().__init__(project_id, thread_manager)
        self.supported_voices = [
            "en-US-AriaNeural",      # Female, friendly
            "en-US-GuyNeural",       # Male, professional
            "en-US-JennyNeural",     # Female, young
            "en-GB-RyanNeural",      # Male, British
            "en-AU-NatashaNeural",   # Female, Australian
            "es-ES-ElviraNeural",    # Female, Spanish
            "fr-FR-DeniseNeural",    # Female, French
            "de-DE-KatjaNeural",     # Female, German
        ]

    @method_metadata(
        display_name="Text to Speech (Free)",
        description="Convert text to natural speech using Microsoft Edge TTS - completely free",
        is_core=False,
        visible=True
    )
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "text_to_speech_free",
            "description": "Convert text to speech using Microsoft Edge TTS. Returns audio file URL. Completely free with no API key required. Supports multiple voices and languages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to convert to speech. Maximum ~5000 characters."
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice to use. Options: en-US-AriaNeural (default, female), en-US-GuyNeural (male), en-GB-RyanNeural (British male), en-US-JennyNeural (young female). Default: en-US-AriaNeural",
                        "default": "en-US-AriaNeural"
                    },
                    "rate": {
                        "type": "string",
                        "description": "Speech rate. Options: x-slow, slow, medium, fast, x-fast. Default: medium",
                        "default": "medium"
                    }
                },
                "required": ["text"]
            }
        }
    })
    async def text_to_speech_free(self, text: str, voice: str = "en-US-AriaNeural", rate: str = "medium") -> ToolResult:
        """
        Convert text to speech using Edge TTS - completely free.
        
        Args:
            text: Text to speak
            voice: Voice to use
            rate: Speech rate
            
        Returns:
            ToolResult with audio file URL
        """
        try:
            await self._ensure_sandbox()
            
            # Limit text length
            if len(text) > 5000:
                text = text[:5000]
                logger.warning("Text truncated to 5000 characters")
            
            # Install edge-tts if not present
            install_cmd = "pip install -q edge-tts 2>&1 | grep -v 'already satisfied' || true"
            await self.sandbox.process.exec(install_cmd, timeout=60)
            
            # Escape text for shell
            escaped_text = text.replace("'", "'\\''")
            
            # Map rate to edge-tts format
            rate_map = {
                "x-slow": "-50%",
                "slow": "-25%",
                "medium": "+0%",
                "fast": "+25%",
                "x-fast": "+50%"
            }
            tts_rate = rate_map.get(rate, "+0%")
            
            # Generate unique filename
            import uuid
            audio_filename = f"speech_{uuid.uuid4().hex[:8]}.mp3"
            audio_path = f"/tmp/{audio_filename}"
            
            # Generate speech using edge-tts
            tts_cmd = f"edge-tts --voice '{voice}' --rate='{tts_rate}' --text '{escaped_text}' --write-media '{audio_path}'"
            
            logger.info(f"Generating speech with voice '{voice}' at rate '{rate}'")
            response = await self.sandbox.process.exec(tts_cmd, timeout=30)
            
            if response.exit_code != 0:
                error_msg = f"TTS generation failed: {response.result}"
                logger.error(error_msg)
                return self.fail_response(error_msg)
            
            # Check if file was created
            check_cmd = f"test -f '{audio_path}' && echo 'exists' || echo 'missing'"
            check_response = await self.sandbox.process.exec(check_cmd, timeout=5)
            
            if "missing" in check_response.result:
                return self.fail_response("Audio file was not generated")
            
            # Get file size
            size_cmd = f"stat -f%z '{audio_path}' 2>/dev/null || stat -c%s '{audio_path}' 2>/dev/null"
            size_response = await self.sandbox.process.exec(size_cmd, timeout=5)
            file_size = int(size_response.result.strip()) if size_response.exit_code == 0 else 0
            
            # Upload to S3 or return base64
            # For now, read as base64 and return
            read_cmd = f"base64 '{audio_path}'"
            read_response = await self.sandbox.process.exec(read_cmd, timeout=10)
            
            if read_response.exit_code != 0:
                return self.fail_response("Failed to read generated audio file")
            
            audio_base64 = read_response.result.strip()
            
            # Create data URL
            audio_data_url = f"data:audio/mpeg;base64,{audio_base64}"
            
            result_text = f"🔊 Generated speech audio:\n"
            result_text += f"- Voice: {voice}\n"
            result_text += f"- Rate: {rate}\n"
            result_text += f"- Text length: {len(text)} characters\n"
            result_text += f"- Audio size: {file_size} bytes\n\n"
            result_text += f"Audio is ready for playback."
            
            logger.info(f"Speech generated successfully: {file_size} bytes, voice={voice}")
            
            return ToolResult(
                output=result_text,
                data={
                    "audio_url": audio_data_url,
                    "audio_base64": audio_base64,
                    "voice": voice,
                    "rate": rate,
                    "text_length": len(text),
                    "file_size": file_size,
                    "format": "mp3",
                    "source": "edge-tts"
                },
                success=True
            )
            
        except Exception as e:
            error_msg = f"Text-to-speech error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.fail_response(error_msg)

    @method_metadata(
        display_name="Speech to Text",
        description="Convert speech audio to text using Whisper",
        is_core=False,
        visible=True
    )
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "speech_to_text",
            "description": "Convert speech audio to text using Whisper (OpenAI API or local). Supports multiple audio formats.",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_base64": {
                        "type": "string",
                        "description": "Base64-encoded audio file (mp3, wav, m4a, webm, etc.)"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (en, es, fr, de, etc.). Default: auto-detect",
                        "default": "auto"
                    },
                    "use_local": {
                        "type": "boolean",
                        "description": "Use local Whisper.cpp instead of OpenAI API (requires Ollama with whisper model). Default: false",
                        "default": False
                    }
                },
                "required": ["audio_base64"]
            }
        }
    })
    async def speech_to_text(self, audio_base64: str, language: str = "auto", use_local: bool = False) -> ToolResult:
        """
        Convert speech to text using Whisper.
        
        Args:
            audio_base64: Base64-encoded audio
            language: Language code or "auto"
            use_local: Use local Whisper instead of OpenAI API
            
        Returns:
            ToolResult with transcribed text
        """
        try:
            await self._ensure_sandbox()
            
            # Save audio file
            import uuid
            audio_filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
            audio_path = f"/tmp/{audio_filename}"
            
            # Write base64 to file
            write_cmd = f"echo '{audio_base64}' | base64 -d > '{audio_path}'"
            write_response = await self.sandbox.process.exec(write_cmd, timeout=10)
            
            if write_response.exit_code != 0:
                return self.fail_response("Failed to save audio file")
            
            transcribed_text = ""
            
            if use_local:
                # Use local Whisper via Ollama
                if not config.OLLAMA_API_BASE:
                    return self.fail_response("Local Whisper requested but OLLAMA_API_BASE not configured")
                
                # Install whisper.cpp or use Ollama's whisper
                logger.info("Using local Whisper for transcription")
                
                # Use Ollama's whisper model (if available)
                whisper_cmd = f"curl -s -X POST '{config.OLLAMA_API_BASE}/api/generate' -H 'Content-Type: application/json' -d '{{\"model\": \"whisper\", \"prompt\": \"transcribe\", \"stream\": false, \"audio\": \"$(base64 -w 0 {audio_path})\"}}'  "
                response = await self.sandbox.process.exec(whisper_cmd, timeout=60)
                
                if response.exit_code == 0:
                    result = json.loads(response.result)
                    transcribed_text = result.get("response", "")
                else:
                    return self.fail_response("Local Whisper transcription failed. Make sure 'ollama pull whisper' has been run.")
            else:
                # Use OpenAI Whisper API
                if not config.OPENAI_API_KEY:
                    return self.fail_response("OpenAI Whisper requested but OPENAI_API_KEY not configured. Set use_local=true to use local Whisper via Ollama.")
                
                logger.info("Using OpenAI Whisper API for transcription")
                
                # Install openai library
                install_cmd = "pip install -q openai 2>&1 | grep -v 'already satisfied' || true"
                await self.sandbox.process.exec(install_cmd, timeout=60)
                
                # Create Python script for Whisper API call
                lang_param = f", language='{language}'" if language != "auto" else ""
                whisper_script = f"""
import json
import os
from openai import OpenAI

try:
    client = OpenAI(api_key='{config.OPENAI_API_KEY}')
    
    with open('{audio_path}', 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file{lang_param}
        )
    
    print(json.dumps({{'text': transcript.text, 'success': True}}))
except Exception as e:
    print(json.dumps({{'error': str(e), 'success': False}}))
"""
                
                script_path = "/tmp/whisper_script.py"
                write_script_cmd = f"cat > {script_path} << 'EOFSCRIPT'\n{whisper_script}\nEOFSCRIPT"
                await self.sandbox.process.exec(write_script_cmd, timeout=10)
                
                response = await self.sandbox.process.exec(f"python {script_path}", timeout=60)
                
                if response.exit_code != 0:
                    return self.fail_response(f"Whisper API call failed: {response.result}")
                
                result = json.loads(response.result)
                if not result.get("success"):
                    return self.fail_response(f"Transcription error: {result.get('error', 'Unknown error')}")
                
                transcribed_text = result.get("text", "")
            
            if not transcribed_text:
                return self.fail_response("No text was transcribed from the audio")
            
            result_output = f"🎤 Transcribed audio:\n\n{transcribed_text}"
            
            logger.info(f"Successfully transcribed audio: {len(transcribed_text)} characters")
            
            return ToolResult(
                output=result_output,
                data={
                    "text": transcribed_text,
                    "language": language,
                    "method": "local_whisper" if use_local else "openai_whisper",
                    "text_length": len(transcribed_text)
                },
                success=True
            )
            
        except Exception as e:
            error_msg = f"Speech-to-text error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.fail_response(error_msg)

    @method_metadata(
        display_name="List Available Voices",
        description="List all available TTS voices",
        is_core=False,
        visible=True
    )
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "list_voices",
            "description": "List all available text-to-speech voices with their languages and characteristics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "Filter by language code (en, es, fr, de). Default: all languages",
                        "default": "all"
                    }
                },
                "required": []
            }
        }
    })
    async def list_voices(self, language: str = "all") -> ToolResult:
        """
        List available TTS voices.
        
        Args:
            language: Language filter
            
        Returns:
            ToolResult with list of voices
        """
        try:
            await self._ensure_sandbox()
            
            # Install edge-tts
            install_cmd = "pip install -q edge-tts 2>&1 | grep -v 'already satisfied' || true"
            await self.sandbox.process.exec(install_cmd, timeout=60)
            
            # Get list of all voices
            list_cmd = "edge-tts --list-voices"
            response = await self.sandbox.process.exec(list_cmd, timeout=15)
            
            if response.exit_code != 0:
                return self.fail_response("Failed to fetch voice list")
            
            # Parse voice list
            voices_output = response.result
            voices = []
            
            # Parse the output (format: Name: voice-name)
            for line in voices_output.split('\n'):
                if line.strip() and 'Name:' in line:
                    voice_name = line.split('Name:')[1].strip()
                    
                    # Filter by language if specified
                    if language != "all":
                        if not voice_name.startswith(f"{language}-"):
                            continue
                    
                    # Extract language and gender info
                    parts = voice_name.split('-')
                    lang_code = parts[0] if len(parts) > 0 else "unknown"
                    region = parts[1] if len(parts) > 1 else "unknown"
                    
                    is_neural = "Neural" in voice_name
                    
                    voices.append({
                        "id": voice_name,
                        "language": lang_code,
                        "region": region,
                        "is_neural": is_neural
                    })
            
            # Format output
            result_text = f"🎙️ Available Text-to-Speech Voices ({len(voices)} found):\n\n"
            
            # Group by language
            voices_by_lang = {}
            for voice in voices:
                lang = voice['language']
                if lang not in voices_by_lang:
                    voices_by_lang[lang] = []
                voices_by_lang[lang].append(voice)
            
            for lang, lang_voices in sorted(voices_by_lang.items()):
                result_text += f"**{lang}** ({len(lang_voices)} voices):\n"
                for voice in lang_voices[:5]:  # Show first 5 per language
                    result_text += f"  - {voice['id']}\n"
                if len(lang_voices) > 5:
                    result_text += f"  ... and {len(lang_voices) - 5} more\n"
                result_text += "\n"
            
            logger.info(f"Listed {len(voices)} voices")
            
            return ToolResult(
                output=result_text,
                data={
                    "voices": voices,
                    "total_count": len(voices),
                    "languages": list(voices_by_lang.keys())
                },
                success=True
            )
            
        except Exception as e:
            error_msg = f"List voices error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.fail_response(error_msg)
