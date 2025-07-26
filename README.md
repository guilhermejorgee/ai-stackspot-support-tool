# Integração PydanticAI + LiteLLM + Stackspot

Este guia mostra como conectar um agente PydanticAI ao seu proxy LiteLLM local que utiliza o Stackspot como provider.

## 📋 Pré-requisitos

1. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

2. **Verificar configuração do proxy**:
   - Arquivo `config.yaml` configurado
   - Custom handler `custom_handler.py` implementado
   - Suporte a tools funcionando

## 🚀 Como Usar

### 1. Iniciar o Proxy LiteLLM

```bash

# Opção 2: Comando direto
litellm --config config.yaml --port 4000
```

O proxy ficará disponível em `http://localhost:4000`

### 2. Configurar PydanticAI

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Configurar modelo para usar proxy local
model = OpenAIModel(
    model_name='stackspot-chat',  # Nome definido no config.yaml
    base_url='http://localhost:4000/v1',  # URL do proxy
    api_key='fake-key'  # Não é necessária chave real
)

# Criar agente com tools
agent = Agent(
    model=model,
    tools=[sua_funcao_tool1, sua_funcao_tool2],
    system_prompt="Você é um assistente útil..."
)
```

### 3. Executar Agente

```python
# Executar consulta
result = await agent.run("Sua pergunta aqui")
print(result.data)
```

## 🔧 Configurações Avançadas

### Timeouts e Retries

```python
model = OpenAIModel(
    model_name='stackspot-chat',
    base_url='http://localhost:4000/v1',
    api_key='fake-key'
)
```

### Variáveis de Ambiente

Crie um arquivo `.env`:

```bash
LITELLM_BASE_URL=http://localhost:4000/v1
LITELLM_MODEL_NAME=stackspot-chat
LITELLM_API_KEY=fake-key
```

## 🛠️ Troubleshooting

### Proxy não responde
- Verifique se o proxy está rodando: `curl http://localhost:4000/health`
- Confirme a porta: pode estar sendo usada por outro processo
- Verifique logs do LiteLLM para erros de autenticação

### PydanticAI não encontra tools
- Certifique-se de que o custom handler está detectando tool calls corretamente
- Teste diretamente o proxy: `curl -X POST http://localhost:4000/v1/chat/completions`
- Verifique se as tools estão sendo passadas no formato correto

### Erros de autenticação do Stackspot
- Confirme as credenciais no `custom_handler.py`
- Teste autenticação: `python debug_test.py`
- Verifique se o JWT não expirou

### Performance lenta
- O Stackspot pode ter limitações de rate limiting
- Considere implementar cache para respostas
- Use connection pooling no httpx/requests

## 📊 Monitoramento

### Logs do Proxy
```bash
# Iniciar com logs detalhados
litellm --config config.yaml --port 4000 --verbose
```

### Métricas do PydanticAI
```python
# Acessar histórico de mensagens
result = await agent.run("pergunta")
print(f"Mensagens trocadas: {len(result.all_messages())}")
print(f"Custo estimado: {result.cost()}")
```

## 🔗 Endpoints Disponíveis

Quando o proxy estiver rodando:

- **Chat**: `POST http://localhost:4000/v1/chat/completions`
- **Models**: `GET http://localhost:4000/v1/models`  
- **Health**: `GET http://localhost:4000/health`
- **Metrics**: `GET http://localhost:4000/metrics` (se habilitado)

## 📝 Exemplo Completo

Veja `pydantic_agent_example.py` para um exemplo completo com:
- Configuração do modelo
- Definição de tools personalizadas  
- Testes de diferentes cenários
- Conversas multi-turn
- Tratamento de erros

## 🎯 Próximos Passos

1. **Produção**: Configure HTTPS, autenticação e rate limiting
2. **Monitoramento**: Adicione métricas e alertas
3. **Scaling**: Use load balancer para múltiplas instâncias
4. **Cache**: Implemente cache para respostas frequentes