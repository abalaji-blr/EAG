import os
import json
import yaml
import requests
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta
import asyncio
from typing import Optional

load_dotenv()

ROOT = Path(__file__).parent.parent
MODELS_JSON = ROOT / "config" / "models.json"
PROFILE_YAML = ROOT / "config" / "profiles.yaml"

class RateLimiter:
    def __init__(self, requests_per_minute: int = 15):  # Gemini free tier limit
        self.requests_per_minute = requests_per_minute
        self.requests = []

    async def acquire(self):
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [
            req for req in self.requests if now - req < timedelta(minutes=1)
        ]

        if len(self.requests) >= self.requests_per_minute:
            # Wait until we can make another request
            wait_time = 60 - (now - self.requests[0]).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                # Refresh the requests list after waiting
                self.requests = [req for req in self.requests if now - req < timedelta(minutes=1)]

        self.requests.append(now)

class ModelManager:
    def __init__(self):
        self.config = json.loads(MODELS_JSON.read_text())
        self.profile = yaml.safe_load(PROFILE_YAML.read_text())

        self.text_model_key = self.profile["llm"]["text_generation"]
        self.model_info = self.config["models"][self.text_model_key]
        self.model_type = self.model_info["type"]

        # Initialize Gemini API
        if self.model_type == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.rate_limiter = RateLimiter()

    async def generate_text(self, prompt: str) -> str:
        if self.model_type == "gemini":
            return await self._gemini_generate(prompt)
        elif self.model_type == "ollama":
            return self._ollama_generate(prompt)
        else:
            raise NotImplementedError(f"Unsupported model type: {self.model_type}")

    async def _gemini_generate(self, prompt: str) -> str:
        """Generate text using Gemini API with rate limiting"""
        try:
            await self.rate_limiter.acquire()
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                # If we hit rate limit, wait and retry once
                await asyncio.sleep(60)  # Wait for 1 minute
                await self.rate_limiter.acquire()
                response = self.model.generate_content(prompt)
                return response.text
            raise e

    def _ollama_generate(self, prompt: str) -> str:
        response = requests.post(
            self.model_info["url"]["generate"],
            json={"model": self.model_info["model"], "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json()["response"].strip()
