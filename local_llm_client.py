# local_llm_client.py
from openai import OpenAI
import os

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",  # required dummy key for compatibility
)

def run_llm(prompt, system_message="You are a helpful assistant."):
    response = client.chat.completions.create(
        model="local-model",  # replace if necessary
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

