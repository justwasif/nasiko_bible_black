"""
Base Gateway Client for LLM Gateway Integration

This module provides a client that agents can use to connect to the LLM Gateway
instead of directly connecting to LLM providers.

Features:
- OpenAI-compatible interface
- Virtual key authentication
- Automatic endpoint switching
- Retry logic with exponential backoff
- Timeout handling
- Tracing context propagation
"""

import os
import time
from typing import Optional, Dict, Any, List, Union
import httpx
from dataclasses import dataclass


@dataclass
class GatewayConfig:
    """Configuration for the LLM Gateway client."""
    base_url: str = "http://localhost:4000"
    virtual_key: Optional[str] = None
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    @classmethod
    def from_env(cls) -> 'GatewayConfig':
        """Create configuration from environment variables."""
        return cls(
            base_url=os.getenv('GATEWAY_URL', 'http://localhost:4000'),
            virtual_key=os.getenv('GATEWAY_VIRTUAL_KEY'),
            timeout=float(os.getenv('GATEWAY_TIMEOUT', '60.0')),
            max_retries=int(os.getenv('GATEWAY_MAX_RETRIES', '3')),
            retry_delay=float(os.getenv('GATEWAY_RETRY_DELAY', '1.0'))
        )


class GatewayClientError(Exception):
    """Base exception for gateway client errors."""
    pass


class GatewayAuthenticationError(GatewayClientError):
    """Raised when authentication fails."""
    pass


class GatewayRateLimitError(GatewayClientError):
    """Raised when rate limit is exceeded."""
    pass


class GatewayClient:
    """
    Client for interacting with the LLM Gateway.
    
    This client provides an OpenAI-compatible interface that routes all requests
    through the gateway instead of directly to LLM providers.
    
    Usage:
        client = GatewayClient()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(self, config: Optional[GatewayConfig] = None):
        """
        Initialize the gateway client.
        
        Args:
            config: Gateway configuration. If None, loads from environment.
        """
        self.config = config or GatewayConfig.from_env()
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=self._get_headers()
        )
        
        # Initialize sub-clients
        self.chat = ChatCompletionsClient(self)
        self.embeddings = EmbeddingsClient(self)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests."""
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.config.virtual_key:
            headers["Authorization"] = f"Bearer {self.config.virtual_key}"
        
        return headers
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a request to the gateway with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx
            
        Returns:
            Response data as dictionary
            
        Raises:
            GatewayAuthenticationError: If authentication fails
            GatewayRateLimitError: If rate limit is exceeded
            GatewayClientError: For other errors
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=endpoint,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise GatewayAuthenticationError(
                        "Invalid virtual key. Please check your GATEWAY_VIRTUAL_KEY."
                    )
                elif e.response.status_code == 429:
                    raise GatewayRateLimitError(
                        "Rate limit exceeded. Please wait before retrying."
                    )
                elif e.response.status_code >= 500:
                    # Server error, retry
                    if attempt < self.config.max_retries:
                        time.sleep(self.config.retry_delay * (2 ** attempt))
                        continue
                raise GatewayClientError(f"HTTP {e.response.status_code}: {e.response.text}")
                
            except httpx.TimeoutException:
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise GatewayClientError("Request timed out")
                
            except Exception as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise GatewayClientError(f"Request failed: {str(e)}")
        
        raise GatewayClientError(f"Max retries exceeded: {str(last_exception)}")
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ChatCompletionsClient:
    """Client for chat completions API."""
    
    def __init__(self, gateway_client: GatewayClient):
        self.gateway = gateway_client
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion.
        
        Args:
            model: Model name (e.g., "gpt-4", "claude-3-opus")
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            Completion response
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        return self.gateway._request("POST", "/chat/completions", json=payload)


class EmbeddingsClient:
    """Client for embeddings API."""
    
    def __init__(self, gateway_client: GatewayClient):
        self.gateway = gateway_client
    
    def create(
        self,
        model: str,
        input: Union[str, List[str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create embeddings.
        
        Args:
            model: Model name (e.g., "text-embedding-ada-002")
            input: Text or list of texts to embed
            **kwargs: Additional parameters
            
        Returns:
            Embeddings response
        """
        payload = {
            "model": model,
            "input": input,
            **kwargs
        }
        
        return self.gateway._request("POST", "/embeddings", json=payload)


# Convenience function for quick usage
def create_client(
    base_url: Optional[str] = None,
    virtual_key: Optional[str] = None
) -> GatewayClient:
    """
    Create a gateway client with optional overrides.
    
    Args:
        base_url: Gateway base URL (overrides env var)
        virtual_key: Virtual key (overrides env var)
        
    Returns:
        Configured GatewayClient
    """
    config = GatewayConfig.from_env()
    
    if base_url:
        config.base_url = base_url
    if virtual_key:
        config.virtual_key = virtual_key
    
    return GatewayClient(config)


# Example usage
if __name__ == "__main__":
    # Example: Create a client and make a request
    try:
        client = create_client()
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! How are you?"}
            ],
            max_tokens=100
        )
        
        print("Response:", response)
        
    except GatewayAuthenticationError as e:
        print(f"Authentication error: {e}")
    except GatewayRateLimitError as e:
        print(f"Rate limit error: {e}")
    except GatewayClientError as e:
        print(f"Client error: {e}")
