import os

import httpx


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:14b",
)

OLLAMA_TIMEOUT = float(
    os.getenv(
        "OLLAMA_TIMEOUT",
        "300",
    )
)


class LLMService:
    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout: float = OLLAMA_TIMEOUT,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "stream": False,
                },
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=self.timeout,
                    write=30.0,
                    pool=10.0,
                ),
            )

            response.raise_for_status()

        except httpx.ReadTimeout as exc:
            raise RuntimeError(
                f"Ollama did not finish generating within "
                f"{self.timeout:.0f} seconds."
            ) from exc

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Failed to communicate with Ollama: {exc}"
            ) from exc

        data = response.json()

        try:
            return data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise RuntimeError(
                "Ollama returned an unexpected response."
            ) from exc