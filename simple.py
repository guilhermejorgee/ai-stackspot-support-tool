import requests
import ulid

BASE_URL = "http://localhost:4000/v1/chat/completions"
MODEL = "stackspot-chat"  # ajuste conforme necessário

def chat():
    correlation_id = str(ulid.new())
    headers = {"correlation-id": correlation_id}
    print("Digite 'sair' para encerrar a conversa.")
    while True:
        user_input = input("Você: ")
        if user_input.lower() == "sair":
            break
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": user_input}],
            "stream": False
        }
        try:
            response = requests.post(BASE_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            print("LLM:", reply)
        except Exception as e:
            print("Erro ao se comunicar com o LLM:", e)

if __name__ == "__main__":
    chat()