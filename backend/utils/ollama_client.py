import requests
import json

class OllamaClient:
    def __init__(self, host="http://localhost:11434", model="qwen2.5:7b"):
        self.host = host.rstrip('/')
        self.model = model

    def is_available(self):
        """
        Check if Ollama is running and accessible.
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name') for m in models]
                
                # Auto-detect if user has a smaller version of qwen2.5 installed (e.g., 1.5b or 3b)
                for name in model_names:
                    if "qwen2.5" in name:
                        self.model = name
                        return True
                
                for name in model_names:
                    if self.model in name or name in self.model:
                        return True
                return len(models) > 0
            return False
        except Exception:
            return False

    def generate_explanation(self, system_prompt, user_content):
        """
        Send a chat completion request to the local Qwen model.
        """
        url = f"{self.host}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "").strip()
            else:
                return f"[Error: Ollama returned status code {response.status_code}]"
        except requests.exceptions.Timeout:
            return "[Error: Request to Ollama timed out. Make sure the local Ollama service is responsive.]"
        except Exception as e:
            return f"[Error: Failed to connect to Ollama. Details: {str(e)}]"
