#!/usr/bin/env python3
"""
chatbot_multi_mcp.py  ·  Gradio + PydanticAI + MCP
Exemplo de chatbot que integra três servidores MCP distintos:
  1) Servidor de horário (AWS Lambda)
  2) Servidor de alertas meteorológicos (AWS Lambda)
  3) Servidor local de busca genérica
"""
import os
import httpx
import ulid
import logging
import asyncio
import time
import concurrent.futures
import gradio as gr
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStreamableHTTP

# ————————————————
# Configuração de logging
# ————————————————
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ————————————————
# Variáveis de ambiente para endpoints MCP
# ————————————————

# ————————————————
# Configuração dos stubs MCP HTTP para cada serviço
# ————————————————

# ————————————————
# Inicializa o agente PydanticAI com múltiplos servidores MCP
# ————————————————
# O modelo pode ser OpenAI ou outro compatível

# Create a custom httpx.AsyncClient with desired headers
custom_client = httpx.AsyncClient(headers={"correlation-id": str(ulid.new())})

model = OpenAIModel(
    'stackspot-chat',
    provider=OpenAIProvider(
        base_url='http://localhost:4000/v1',
        api_key='your-perplexity-api-key',
        http_client=custom_client
    ),
)

server = MCPServerStreamableHTTP('http://localhost:8000/mcp')

agent = Agent(model, toolsets=[server])

# Estado global de status
status_message = "🔄 Conectando aos servidores MCP..."

# ————————————————
# Função para processar cada pergunta do usuário
# ————————————————
def process_query(message, history, model_name=None):
    """
    Envia a mensagem para o agente, que decide qual servidor MCP chamar.
    Retorna resposta e atualiza status.
    """
    global status_message
    logger.info(f"Consulta recebida: {message}")
    status_message = "⏳ Processando via MCP..."

    try:
        # Executa agente com timeout rigoroso em thread pool
        with concurrent.futures.ThreadPoolExecutor() as pool:
            start_time = time.time()

            def run_agent():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                async def _run():
                    return await agent.run(message)
                return loop.run_until_complete(_run())

            future = pool.submit(run_agent)
            result = future.result(timeout=20)
            elapsed = time.time() - start_time

            status_message = f"✅ Resposta em {elapsed:.2f}s"
            logger.info(f"Resposta obtida em {elapsed:.2f}s")
            return result.output, history

    except concurrent.futures.TimeoutError:
        status_message = "❌ Timeout (>20s)"
        return "⚠️ Tempo esgotado. Tente novamente.", history
    except Exception as e:
        status_message = f"❌ Erro: {e}"
        logger.exception("Erro ao processar consulta")
        return f"⚠️ Erro interno: {e}", history

# ————————————————
# Constrói interface Gradio para chat
# ————————————————
with gr.Blocks(theme="soft") as demo:
    gr.Markdown("# 🤖 Chatbot Multi-MCP")
    # Exibe status de conexão
    status_box = gr.Textbox(label="Status", value=status_message, interactive=False)
    gr.Button("🔄 Atualizar Status").click(lambda: status_message, None, status_box)

    # Chatbot
    chatbot = gr.Chatbot(type="messages", label="Conversa")
    user_input = gr.Textbox(placeholder="Digite sua pergunta aqui...")
    send_btn = gr.Button("Enviar")

    def respond(message, history):
        if not message:
            return history
        history.append({"role": "user", "content": message})
        response, _ = process_query(message, history)
        history.append({"role": "assistant", "content": response})
        return history

    send_btn.click(respond, [user_input, chatbot], chatbot)
    user_input.submit(respond, [user_input, chatbot], chatbot)

# ————————————————
# Ponto de entrada
# ————————————————
if __name__ == "__main__":
    demo.launch(server_port=7860)