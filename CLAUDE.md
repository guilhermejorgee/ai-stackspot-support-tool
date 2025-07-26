# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LiteLLM proxy configuration for integrating Stackspot AI services. The project creates a custom LLM handler that authenticates with Stackspot's identity management system and provides chat completion capabilities through their inference API.

## Architecture

The project consists of three main components:

1. **config.yaml** - LiteLLM configuration that defines the model mapping and custom handler setup
2. **custom_handler.py** - Custom LLM implementation (`StackspotLLM`) that extends LiteLLM's `CustomLLM` class
3. **get_jwt.sh** - Shell script for manual JWT token generation and API testing

### Core Components

- **StackspotLLM Class** (`custom_handler.py:7-170`): Implements synchronous and asynchronous completion methods
  - `authenticate()`: Handles OAuth2 client credentials flow with Stackspot IDM
  - `completion()`: Synchronous chat completion
  - `acompletion()`: Asynchronous chat completion  
  - `streaming()`: Synchronous streaming responses
  - `astreaming()`: Asynchronous streaming responses

- **Configuration** (`config.yaml`): Maps `stackspot-chat` model to the custom handler instance

## API Integration

- **Authentication Endpoint**: `https://idm.stackspot.com/{realm}/oidc/oauth/token`
- **Chat Endpoint**: `https://genai-inference-app.stackspot.com/v1/agent/01JY28DS74594K2ZR3SSM7F08Q/chat`
- **Agent ID**: `01JY28DS74594K2ZR3SSM7F08Q` (hardcoded in the implementation)

## Dependencies

The project requires:
- `litellm` - Core LLM proxy framework
- `requests` - HTTP client for synchronous requests  
- `httpx` - HTTP client for asynchronous requests

## Authentication

The system uses OAuth2 client credentials flow with hardcoded client credentials in the code. The JWT token is cached in the class instance and refreshed as needed.

## Development Notes

- No formal package management files (requirements.txt, setup.py) are present
- The project appears to be a minimal configuration setup rather than a full application
- All API endpoints and credentials are currently hardcoded in the source