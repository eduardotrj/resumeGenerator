# local_llm_client.py
import lmstudio as lms

SERVER_API_HOST = "localhost:1234"

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
        with lms.Client(SERVER_API_HOST) as client:
            model = client.llm.model("llama-3.2-8b-instruct")

            # Combine system message and user prompt
            full_prompt = f"System: {system_message}\n\nUser: {prompt}"

            result = model.respond(full_prompt)
            return result

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

