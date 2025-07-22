from openai import OpenAI

SERVER_API_HOST = "localhost:1234"
MODEL = "llama-3.2-8b-instruct"

client = OpenAI(base_url=f"http://{SERVER_API_HOST}/v1", api_key="lm-studio")

def run_llm(prompt, system_message="You are a helpful assistant."):
    """
    Run LLM with the given prompt and system message

    Args:
        prompt (str): The user prompt
        system_message (str): The system message to set context

    Returns:
        str: The LLM response
    """
    try:
        return client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        ).choices[0].message.content.strip()
        # Connect to the LM Studio client
        # Using the OpenAI client to connect to LM Studio

    except Exception as e:
        print(f"Error connecting to LM Studio: {e}")
        # Fallback error message
        return f"Error: Could not generate response. Make sure LM Studio is running on {SERVER_API_HOST}"

# Test function - can be removed in production
def test_connection():
    """Test the connection to LM Studio"""
    try:
        test_response = run_llm("Hello, are you working?", "You are a helpful assistant.")
        print("✅ LM Studio connection successful")
        print(f"Test response: {test_response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ LM Studio connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()

