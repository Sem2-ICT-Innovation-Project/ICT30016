import ollama

r = ollama.chat(model="qwen2.5:3b", messages=[
    {"role": "system", "content": "You are a test agent. Follow instructions exactly."},
    {"role": "user", "content": "Say READY if you can hear me."},
])
print(r["message"]["content"])
