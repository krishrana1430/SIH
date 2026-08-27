"""
WeatherGPT LLM Service
Three-tier provider fallback chain for resilient LLM calls
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import asyncio
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LLMService:
    """
    Unified LLM service with three-tier fallback:
    - Tier A (Primary): Groq or Gemini (free, fast)
    - Tier B (Secondary): Alternative free tier
    - Tier C (Fallback): Local Ollama (offline capable)

    All tiers speak OpenAI-compatible chat/completions API.
    """

    def __init__(self):
        self.last_tier_used = None
        self.timeout = 8.0  # seconds per tier attempt

        # Tier A: Primary (Groq by default)
        self.primary_client = None
        self.primary_model = os.getenv("LLM_PRIMARY_MODEL", "openai/gpt-oss-20b")
        if os.getenv("LLM_PRIMARY_BASE_URL") and os.getenv("LLM_PRIMARY_API_KEY"):
            self.primary_client = AsyncOpenAI(
                base_url=os.getenv("LLM_PRIMARY_BASE_URL"),
                api_key=os.getenv("LLM_PRIMARY_API_KEY")
            )

        # Tier B: Secondary (Gemini by default)
        self.secondary_client = None
        self.secondary_model = os.getenv("LLM_SECONDARY_MODEL", "gemini-2.0-flash")
        if os.getenv("LLM_SECONDARY_BASE_URL") and os.getenv("LLM_SECONDARY_API_KEY"):
            self.secondary_client = AsyncOpenAI(
                base_url=os.getenv("LLM_SECONDARY_BASE_URL"),
                api_key=os.getenv("LLM_SECONDARY_API_KEY")
            )

        # Tier C: Fallback (Ollama - local, no key needed)
        self.fallback_client = None
        self.fallback_model = os.getenv("LLM_FALLBACK_MODEL", "llama3.2:1b")
        if os.getenv("LLM_FALLBACK_BASE_URL"):
            self.fallback_client = AsyncOpenAI(
                base_url=os.getenv("LLM_FALLBACK_BASE_URL"),
                api_key="ollama"  # Ollama doesn't validate API key
            )

        logger.info(f"LLM Service initialized:")
        logger.info(f"  Primary: {self.primary_model if self.primary_client else 'Not configured'}")
        logger.info(f"  Secondary: {self.secondary_model if self.secondary_client else 'Not configured'}")
        logger.info(f"  Fallback: {self.fallback_model if self.fallback_client else 'Not configured'}")

    async def call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        json_mode: bool = False
    ) -> str:
        """
        Call LLM with three-tier fallback.

        Args:
            messages: OpenAI-format messages [{"role": "user", "content": "..."}]
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response tokens
            json_mode: Force JSON response format

        Returns:
            LLM response text

        Raises:
            Exception: If all three tiers fail
        """
        # Try Tier A (Primary)
        if self.primary_client:
            try:
                response = await self._call_with_timeout(
                    self.primary_client,
                    self.primary_model,
                    messages,
                    temperature,
                    max_tokens,
                    json_mode
                )
                self.last_tier_used = "primary"
                logger.info(f"✓ LLM call successful (tier: primary)")
                return response
            except Exception as e:
                logger.warning(f"Primary LLM tier failed: {e}")

        # Try Tier B (Secondary)
        if self.secondary_client:
            try:
                response = await self._call_with_timeout(
                    self.secondary_client,
                    self.secondary_model,
                    messages,
                    temperature,
                    max_tokens,
                    json_mode
                )
                self.last_tier_used = "secondary"
                logger.info(f"✓ LLM call successful (tier: secondary)")
                return response
            except Exception as e:
                logger.warning(f"Secondary LLM tier failed: {e}")

        # Try Tier C (Fallback)
        if self.fallback_client:
            try:
                response = await self._call_with_timeout(
                    self.fallback_client,
                    self.fallback_model,
                    messages,
                    temperature,
                    max_tokens,
                    json_mode
                )
                self.last_tier_used = "fallback"
                logger.info(f"✓ LLM call successful (tier: fallback)")
                return response
            except Exception as e:
                logger.error(f"Fallback LLM tier failed: {e}")

        # All tiers failed
        self.last_tier_used = "none"
        raise Exception("All LLM provider tiers failed. Check configuration and network.")

    async def _call_with_timeout(
        self,
        client: AsyncOpenAI,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        json_mode: bool
    ) -> str:
        """Make LLM call with timeout."""
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Add JSON mode if requested (not all models support this)
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        # Call with timeout
        response = await asyncio.wait_for(
            client.chat.completions.create(**kwargs),
            timeout=self.timeout
        )

        return response.choices[0].message.content

    def get_tier_info(self) -> Dict[str, Any]:
        """Get information about configured tiers."""
        return {
            "primary": {
                "configured": self.primary_client is not None,
                "model": self.primary_model
            },
            "secondary": {
                "configured": self.secondary_client is not None,
                "model": self.secondary_model
            },
            "fallback": {
                "configured": self.fallback_client is not None,
                "model": self.fallback_model
            },
            "last_tier_used": self.last_tier_used
        }


# Global instance
llm_service = LLMService()


if __name__ == "__main__":
    # Test the service
    async def test():
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one sentence."}
        ]
        response = await llm_service.call_llm(messages)
        print(f"Response: {response}")
        print(f"Tier used: {llm_service.last_tier_used}")

    asyncio.run(test())
