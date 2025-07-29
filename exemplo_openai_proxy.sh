#!/bin/bash
# Exemplo de requisição para API OpenAI (proxy local)

curl -X POST \
  http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-fake-key" \
  -H "X-My-Random-Header: valor-teste" \
  -d '{
    "model": "stackspot-chat",
    "messages": [
      {"role": "user", "content": "Diga olá!"}
    ]
  }'