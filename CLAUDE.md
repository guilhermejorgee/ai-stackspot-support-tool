# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LiteLLM proxy configuration for integrating Stackspot AI services. The project creates a custom LLM handler that authenticates with Stackspot's identity management system and provides both completion and streaming chat capabilities with full tool support through their inference API.

## Architecture

The project consists of a streamlined architecture:

1. **config.yaml** - LiteLLM configuration that defines the model mapping and custom handler setup
2. **custom_handler.py** - Refactored custom LLM implementation (`StackspotLLM`) with optimized code structure

### Core Components

- **StackspotLLM Class** (`custom_handler.py:12-507`): Highly optimized implementation with all four required methods
  - `authenticate()`: OAuth2 client credentials flow with comprehensive logging
  - `completion()`: Synchronous chat completion (2 lines - uses shared methods)
  - `acompletion()`: Asynchronous chat completion (2 lines - uses shared methods)  
  - `streaming()`: Synchronous streaming responses (2 lines - uses shared methods)
  - `astreaming()`: Asynchronous streaming responses (3 lines - uses shared methods)

### Refactored Architecture Features

- **Shared Request Setup** (`_prepare_streaming_request()`): Handles authentication, headers, and payload for all methods
- **Completion Response Collection** (`_collect_completion_response()`): Centralized SSE processing for completion methods
- **Streaming Event Processing** (`_process_streaming_events()`): Handles real-time SSE streaming with tool call support
- **Tool Call Processing** (`_process_tool_calls_streaming()`): Progressive tool call streaming implementation
- **Message Conversion** (`_convert_messages_to_prompt()`): Converts OpenAI format to Stackspot format with tool instructions

## API Integration

- **Authentication Endpoint**: `https://idm.stackspot.com/{realm}/oidc/oauth/token`
- **Chat Endpoint**: `https://genai-code-buddy-api.stackspot.com/v3/chat`
- **Agent ID**: `id-do-seu-agent` (configurable via environment)

## Key Features

### Tool Support
- Full OpenAI-compatible tool calling
- Automatic detection of `FUNCTION_CALL_START/END` patterns from Stackspot
- Progressive streaming of tool calls with argument building
- Support for multiple simultaneous tool calls

### Streaming Capabilities
- Real-time SSE (Server-Sent Events) streaming
- Tool calls streamed progressively as they're detected
- Proper OpenAI `GenericStreamingChunk` format
- Async and sync streaming variants

### Correlation ID Support
- Required `correlation_id` header validation
- Passed as `conversation_id` to Stackspot API
- Error handling for missing correlation IDs

### Comprehensive Logging
- Authentication success/failure tracking
- Tool call detection with argument previews
- SSE connection monitoring
- Performance metrics (chunks processed, response sizes)
- Appropriate log levels (DEBUG/INFO/ERROR)

## Dependencies

The project requires:
- `litellm` - Core LLM proxy framework
- `requests` - HTTP client for requests
- `requests-sse` - Server-Sent Events client
- `python-dotenv` - Environment variable management
- `logging` - Built-in logging framework

## Environment Configuration

Required environment variables:
- `CLIENT_ID` - Stackspot OAuth2 client ID
- `CLIENT_SECRET` - Stackspot OAuth2 client secret  
- `REALM` - Stackspot realm identifier
- `GENAI_AGENT_ID` - Stackspot AI agent identifier

## Code Quality

### Refactoring Principles Applied
- **DRY (Don't Repeat Yourself)**: Eliminated ~200 lines of duplication
- **Single Responsibility**: Each method has one clear purpose  
- **Composition over Inheritance**: Shared functionality through private methods
- **Minimal Public Interface**: 4 simple public methods (1-3 lines each)

### Anti-Over-Engineering
- Removed unnecessary abstraction layers
- Inline GenericStreamingChunk creation where appropriate
- Focused helper methods only where genuine code reuse exists
- Maintained readability over excessive modularity

## Development Notes

- The architecture is production-ready with proper error handling
- All methods share common setup logic to ensure consistency
- Logging is strategically placed for debugging without noise
- Tool call parsing handles multiple Stackspot response formats
- SSE connections include proper timeout and error recovery