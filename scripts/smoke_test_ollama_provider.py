from src.llm.ollama_provider import OllamaProvider
from src.llm.schemas import LLMMessage, LLMRequest


provider = OllamaProvider(model="qwen3:4b")

request = LLMRequest(
    messages=[
        LLMMessage(
            role="user",
            content='Return only JSON with status equal to "ok".',
        )
    ],
    temperature=0.0,
    response_schema={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
            }
        },
        "required": ["status"],
    },
)

response = provider.generate(request)

print("content:", response.content)
print("thinking:", response.thinking)
print("model:", response.model)
print("latency_seconds:", response.latency_seconds)
print("usage:", response.usage)