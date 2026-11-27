import asyncio
import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from channels.generic.websocket import AsyncWebsocketConsumer
from .speech import transcribe_audio
from .models import Transcription

executor = ThreadPoolExecutor(max_workers=2)

class SpeechConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.audio_path = tempfile.mktemp(suffix=".webm")
        self.audio_bytes = bytearray()
        self.last_text = ""
        self.last_language = "unknown"
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "status",
            "message": "Connected. Start speaking."
        }))

    async def disconnect(self, close_code):
        if os.path.exists(self.audio_path):
            os.remove(self.audio_path)

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            self.audio_bytes.extend(bytes_data)
            with open(self.audio_path, "wb") as audio_file:
                audio_file.write(self.audio_bytes)
            try:
                loop = asyncio.get_running_loop()
                text, language = await loop.run_in_executor(
                    executor, transcribe_audio, self.audio_path
                )
                if text:
                    self.last_text = text
                    self.last_language = language
                    await self.send(text_data=json.dumps({
                        "type": "transcription",
                        "text": text,
                        "language": language,
                    }))
            except Exception as exc:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": str(exc),
                }))
            return

        if text_data:
            try:
                payload = json.loads(text_data)
            except json.JSONDecodeError:
                return
            if payload.get("action") == "finish":
                text = payload.get("text", "").strip() or self.last_text
                language = payload.get("language", self.last_language)
                title = payload.get("title", "Speech transcription").strip()
                if text:
                    transcription = await self.save_transcription(title, text, language)
                    await self.send(text_data=json.dumps({
                        "type": "saved",
                        "id": transcription.id,
                        "message": "Transcription saved successfully.",
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": "No speech was detected.",
                    }))

    @staticmethod
    def save_transcription(title, text, language):
        return Transcription.objects.create(
            title=title or "Speech transcription",
            text=text,
            language=language or "unknown",
        )

    async def save_transcription(self, title, text, language):
        from channels.db import database_sync_to_async
        return await database_sync_to_async(self.save_transcription_sync)(title, text, language)

    @staticmethod
    def save_transcription_sync(title, text, language):
        return Transcription.objects.create(
            title=title or "Speech transcription",
            text=text,
            language=language or "unknown",
        )
