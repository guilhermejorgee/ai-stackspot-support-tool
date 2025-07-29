# Stackspot LiteLLM Proxy

Proxy LiteLLM altamente otimizado para integração com Stackspot AI, com suporte completo a streaming, tool calling e logging estratégico.

## 🚀 Características Principais

### ✅ Implementação Completa
- **4 métodos LiteLLM**: `completion`, `acompletion`, `streaming`, `astreaming`
- **Tool Calling**: Suporte total a ferramentas OpenAI-compatíveis
- **Streaming SSE**: Resposta em tempo real com Server-Sent Events
- **Correlation ID**: Suporte obrigatório para rastreamento de conversas

### 🏗️ Arquitetura Refatorada
- **~200 linhas eliminadas** através de métodos compartilhados
- **Anti-over-engineering**: Apenas abstrações necessárias
- **Métodos públicos minimalistas**: 1-3 linhas cada
- **Código DRY**: Zero duplicação entre sync/async

### 📊 Logging Estratégico
- **Autenticação**: Sucesso/falha com detalhes
- **Tool Calls**: Detecção e argumentos
- **SSE Connections**: Monitoramento de conexões
- **Performance**: Métricas de chunks processados

## 📋 Pré-requisitos

### Dependências
```bash
pip install -r requirements.txt
```

### Variáveis de Ambiente
Crie um arquivo `.env`:
```bash
CLIENT_ID=seu_client_id_stackspot
CLIENT_SECRET=seu_client_secret_stackspot
REALM=seu_realm
GENAI_AGENT_ID=seu_agent_id
```

## 🔧 Configuração

### 1. Configurar config.yaml
```yaml
model_list:
  - model_name: stackspot-chat
    litellm_params:
      model: stackspot-chat
      custom_llm_provider: stackspot
```

### 2. Iniciar o Proxy
```bash
litellm --config config.yaml --port 4000
```

## 💻 Uso com PydanticAI

### Configuração Básica
```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Configurar modelo
model = OpenAIModel(
    model_name='stackspot-chat',
    base_url='http://localhost:4000/v1',
    api_key='fake-key'  # Não é necessária
)

# Criar agente com tools
agent = Agent(
    model=model,
    tools=[sua_funcao_tool],
    system_prompt="Você é um assistente útil..."
)
```

### Com Correlation ID (Obrigatório)
```python
import httpx

# Cliente customizado com correlation ID
client = httpx.AsyncClient(
    headers={'correlation-id': 'sua-conversa-123'}
)

model = OpenAIModel(
    model_name='stackspot-chat',
    base_url='http://localhost:4000/v1',
    api_key='fake-key',
    http_client=client
)
```

### Executar com Streaming
```python
# Streaming automático com PydanticAI
result = await agent.run("Sua pergunta aqui", stream=True)
print(result.data)
```

## 🛠️ Features Avançadas

### Tool Calling
O proxy detecta automaticamente tool calls do Stackspot:
```
FUNCTION_CALL_START
function_name
arguments: {"param": "value"}
FUNCTION_CALL_END
```

### Logging Configurável
```python
import logging

# Debug detalhado
logging.getLogger('custom_handler').setLevel(logging.DEBUG)

# Produção (apenas erros)
logging.getLogger('custom_handler').setLevel(logging.ERROR)
```

### Métricas de Performance
- Tool calls detectados por requisição
- Chunks de streaming processados  
- Tamanho das respostas coletadas
- Tempo de autenticação JWT

## 🔍 Troubleshooting

### Erro: "correlation_id ausente"
```python
# ✅ Correto - incluir header
headers = {'correlation-id': 'conversa-123'}

# ❌ Incorreto - sem header
# Resultará em KeyError
```

### Autenticação Falhando
```bash
# Verificar logs
tail -f litellm.log | grep "Authentication"

# Testar manualmente
python -c "from custom_handler import StackspotLLM; s=StackspotLLM(); s.authenticate()"
```

### Streaming Não Funciona
```python
# Verificar se está usando stream=True
result = await agent.run("pergunta", stream=True)

# Debug de conexão SSE
logging.getLogger('custom_handler').setLevel(logging.DEBUG)
```

### Performance Lenta
- **Rate Limiting**: Stackspot pode ter limites
- **JWT Caching**: Tokens são reutilizados automaticamente  
- **Connection Pooling**: Use `httpx.AsyncClient` persistente

## 📊 Monitoramento

### Logs Estratégicos
```bash
# Iniciar com logs detalhados
export PYTHONPATH=.
litellm --config config.yaml --port 4000 --debug

# Filtrar apenas erros críticos
litellm --config config.yaml --port 4000 2>&1 | grep ERROR
```

### Métricas em Tempo Real
- `INFO`: Tool calls encontrados
- `DEBUG`: Chunks de streaming processados
- `ERROR`: Falhas de autenticação/conexão
- `WARNING`: Parsing de eventos falhou

## 🏛️ Arquitetura Interna

### Métodos Públicos (Ultra-Simples)
```python
def completion(self, model, messages, **kwargs):
    url, headers, payload = self._prepare_streaming_request(messages, **kwargs)
    return self._collect_completion_response(url, headers, payload, model)

def streaming(self, model, messages, **kwargs):
    url, headers, payload = self._prepare_streaming_request(messages, **kwargs)
    yield from self._process_streaming_events(url, headers, payload)
```

### Métodos Compartilhados
- `_prepare_streaming_request()`: Setup comum
- `_collect_completion_response()`: Coleta SSE para completion
- `_process_streaming_events()`: Streaming em tempo real
- `_process_tool_calls_streaming()`: Tool calls progressivos

## 🚦 API Endpoints

Quando o proxy estiver rodando:

- **Chat Completions**: `POST http://localhost:4000/v1/chat/completions`
- **Streaming**: Mesmo endpoint com `"stream": true`
- **Models**: `GET http://localhost:4000/v1/models`
- **Health**: `GET http://localhost:4000/health`

## 📝 Exemplo Completo

```python
import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
import httpx

async def main():
    # Cliente com correlation ID
    client = httpx.AsyncClient(
        headers={'correlation-id': 'conversa-teste-123'}
    )
    
    # Modelo configurado
    model = OpenAIModel(
        model_name='stackspot-chat',
        base_url='http://localhost:4000/v1', 
        api_key='fake-key',
        http_client=client
    )
    
    # Agente com tool
    def buscar_tempo(cidade: str) -> str:
        return f"Tempo em {cidade}: 25°C, ensolarado"
    
    agent = Agent(
        model=model,
        tools=[buscar_tempo],
        system_prompt="Use as ferramentas disponíveis para responder."
    )
    
    # Executar com streaming
    result = await agent.run(
        "Qual o tempo em São Paulo?",
        stream=True
    )
    
    print(f"Resposta: {result.data}")
    print(f"Tool calls: {len([m for m in result.all_messages() if m.role == 'tool'])}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🎯 Próximos Passos

1. **Produção**: HTTPS, autenticação, rate limiting
2. **Observabilidade**: Prometheus metrics, OpenTelemetry  
3. **Scaling**: Load balancer, múltiplas instâncias
4. **Cache**: Redis para respostas frequentes
5. **Monitoring**: Health checks, alertas automáticos