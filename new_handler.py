from typing import Iterator, AsyncIterator
import litellm, os
from dotenv import load_dotenv
from litellm.types.utils import GenericStreamingChunk, ModelResponse
from litellm import CustomLLM
from openai import OpenAI, AsyncOpenAI

class NewHandler(CustomLLM):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
            )
        self.async_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
            )
    def completion(self, *args, **kwargs) -> ModelResponse:
        messages = kwargs.get("messages", [])
        model = kwargs.get("model", "gpt-3.5-turbo")
        tools = kwargs.get("tools")

        tools = kwargs.get("tools", None)
        if tools is None:
            optional_params = kwargs.get("optional_params", {})
            tools = optional_params.get("tools", None)
        
        
        response = self.client.chat.completions.create(
            model="openai/gpt-4.1-nano",
            messages=messages,
            tools=tools
        )
        
        # Preparar mensagem de resposta com suporte a tool calls
        message_data = {
            "role": response.choices[0].message.role,
            "content": response.choices[0].message.content
        }
        
        # Adicionar tool_calls se existirem
        if response.choices[0].message.tool_calls:
            message_data["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in response.choices[0].message.tool_calls
            ]
        
        return ModelResponse(
            id=response.id,
            object=response.object,
            created=response.created,
            model=response.model,
            choices=[{
                "message": message_data,
                "finish_reason": response.choices[0].finish_reason,
                "index": response.choices[0].index
            }],
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
        )

    async def acompletion(self, *args, **kwargs) -> ModelResponse:
        messages = kwargs.get("messages", [])
        model = kwargs.get("model", "gpt-3.5-turbo")
        tools = kwargs.get("tools")

        tools = kwargs.get("tools", None)
        if tools is None:
            optional_params = kwargs.get("optional_params", {})
            tools = optional_params.get("tools", None)
        
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-4.1-nano",
            messages=messages,
            tools=tools
        )
        
        # Preparar mensagem de resposta com suporte a tool calls
        message_data = {
            "role": response.choices[0].message.role,
            "content": response.choices[0].message.content
        }
        
        # Adicionar tool_calls se existirem
        if response.choices[0].message.tool_calls:
            message_data["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in response.choices[0].message.tool_calls
            ]
        
        return ModelResponse(
            id=response.id,
            object=response.object,
            created=response.created,
            model=response.model,
            choices=[{
                "message": message_data,
                "finish_reason": response.choices[0].finish_reason,
                "index": response.choices[0].index
            }],
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
        )

    def streaming(self, *args, **kwargs) -> Iterator[GenericStreamingChunk]:
        messages = kwargs.get("messages", [])
        model = kwargs.get("model", "gpt-3.5-turbo")
        tools = kwargs.get("tools")

        tools = kwargs.get("tools", None)
        if tools is None:
            optional_params = kwargs.get("optional_params", {})
            tools = optional_params.get("tools", None)
        
        # Fazer chamada não-stream para obter resposta completa
        response = self.client.chat.completions.create(
            model="openai/gpt-4.1-nano",
            messages=messages,
            tools=tools           
        )
        
        # Converter resposta completa em chunks para simular streaming
        if response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            content = choice.message.content or ""
            tool_calls = choice.message.tool_calls
            
            # Se há tool calls, enviar primeiro
            if tool_calls:
                for tool_call in tool_calls:
                    yield GenericStreamingChunk(
                        finish_reason=None,
                        index=0,
                        is_finished=False,
                        text="",
                        tool_use={
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        },
                        usage={"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
                    )
            
            # Dividir o conteúdo em chunks menores (simulando streaming)
            if content:
                chunk_size = 10  # Tamanho do chunk em caracteres
                for i in range(0, len(content), chunk_size):
                    chunk_text = content[i:i + chunk_size]
                    is_last_chunk = i + chunk_size >= len(content)
                    
                    yield GenericStreamingChunk(
                        finish_reason=choice.finish_reason if is_last_chunk else None,
                        index=0,
                        is_finished=is_last_chunk and not tool_calls,
                        text=chunk_text,
                        tool_use=None,
                        usage={
                            "completion_tokens": response.usage.completion_tokens if response.usage and is_last_chunk else 0,
                            "prompt_tokens": response.usage.prompt_tokens if response.usage and is_last_chunk else 0,
                            "total_tokens": response.usage.total_tokens if response.usage and is_last_chunk else 0
                        }
                    )
            
            # Se só há tool calls sem content, enviar chunk final
            if tool_calls and not content:
                yield GenericStreamingChunk(
                    finish_reason=choice.finish_reason,
                    index=0,
                    is_finished=True,
                    text="",
                    tool_use=None,
                    usage={
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                )

    async def astreaming(self, *args, **kwargs) -> AsyncIterator[GenericStreamingChunk]:
        messages = kwargs.get("messages", [])
        model = kwargs.get("model", "gpt-3.5-turbo")
        tools = kwargs.get("tools")

        tools = kwargs.get("tools", None)
        if tools is None:
            optional_params = kwargs.get("optional_params", {})
            tools = optional_params.get("tools", None)
        
        # Fazer chamada não-stream para obter resposta completa
        response = await self.async_client.chat.completions.create(
            model="openai/gpt-4.1-nano",
            messages=messages,
            tools=tools            
        )
        
        # Converter resposta completa em chunks para simular streaming
        if response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            content = choice.message.content or ""
            tool_calls = choice.message.tool_calls
            
            # Se há tool calls, enviar primeiro
            if tool_calls:
                for tool_call in tool_calls:
                    yield GenericStreamingChunk(
                        finish_reason=None,
                        index=0,
                        is_finished=False,
                        text="",
                        tool_use={
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        },
                        usage={"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
                    )
            
            # Dividir o conteúdo em chunks menores (simulando streaming)
            if content:
                chunk_size = 10  # Tamanho do chunk em caracteres
                for i in range(0, len(content), chunk_size):
                    chunk_text = content[i:i + chunk_size]
                    is_last_chunk = i + chunk_size >= len(content)
                    
                    yield GenericStreamingChunk(
                        finish_reason=choice.finish_reason if is_last_chunk else None,
                        index=0,
                        is_finished=is_last_chunk and not tool_calls,
                        text=chunk_text,
                        tool_use=None,
                        usage={
                            "completion_tokens": response.usage.completion_tokens if response.usage and is_last_chunk else 0,
                            "prompt_tokens": response.usage.prompt_tokens if response.usage and is_last_chunk else 0,
                            "total_tokens": response.usage.total_tokens if response.usage and is_last_chunk else 0
                        }
                    )
            
            # Se só há tool calls sem content, enviar chunk final
            if tool_calls and not content:
                yield GenericStreamingChunk(
                    finish_reason=choice.finish_reason,
                    index=0,
                    is_finished=True,
                    text="",
                    tool_use=None,
                    usage={
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                )

new_handler = NewHandler()

litellm.custom_provider_map = [ # 👈 KEY STEP - REGISTER HANDLER
        {"provider": "my-custom-llm", "custom_handler": new_handler}
    ]

resp = litellm.completion(
        model="my-custom-llm/my-fake-model",
        messages=[{"role": "user", "content": "Hello world!"}],
        stream=True,
)

for chunk in resp:
    print(chunk, end="", flush=True)   

