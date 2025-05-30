import requests


def ollama_generate(prompt, model="mistral"):
    """
    Sends a prompt to Ollama and returns the generated text.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["response"]
    except Exception as e:
        return f"[LLM ERROR] {str(e)}"
