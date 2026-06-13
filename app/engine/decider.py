import httpx
import json
from app.core.config import settings

SYSTEM_PROMPT = """You are a decision engine. Given a prompt and context, you must:
1. Make a clear decision (a short label like APPROVE/REJECT/ESCALATE or a direct answer)
2. Provide a confidence score between 0.0 and 1.0
3. Write a brief reasoning trace explaining your decision

Respond ONLY in this JSON format:
{"decision": "...", "confidence": 0.95, "reasoning": "..."}"""

async def call_llm(prompt: str, context: dict | None) -> dict:
    context_str = json.dumps(context, indent=2) if context else "No additional context."
    user_message = f"Prompt: {prompt}\n\nContext:\n{context_str}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openrouter_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2,
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
