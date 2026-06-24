import os, sys
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("PPIO_API_KEY")
base_url = os.getenv("PPIO_BASE_URL")
model = os.getenv("LLM_MODEL_NAME", "deepseek/deepseek-v4-flash")

print("base_url:", base_url)
print("model:", model)

from anthropic import Anthropic
client = Anthropic(api_key=api_key, base_url=base_url)

resp = client.messages.create(
    model=model,
    max_tokens=50,
    messages=[{"role": "user", "content": "请回复LLM调用成功这五个字"}]
)

print("Response type:", type(resp.content[0]).__name__)
for block in resp.content:
    if hasattr(block, 'text'):
        print("Text:", block.text)
    elif hasattr(block, 'thinking'):
        print("Thinking:", block.thinking[:100], "...")
    else:
        print("Block type:", type(block).__name__, "|", str(block)[:100])
print("Stop reason:", resp.stop_reason)
print("Usage - input:", resp.usage.input_tokens, "output:", resp.usage.output_tokens)
print("SUCCESS: LLM API is reachable and working")