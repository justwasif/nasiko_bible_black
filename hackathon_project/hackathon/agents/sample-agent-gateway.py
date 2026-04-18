"""
Sample Agent Using LLM Gateway

This agent demonstrates the new pattern of using the LLM Gateway
instead of hardcoding provider API keys.

Key features:
- Uses virtual key from environment
- No hardcoded API keys in source code
- Connects to gateway endpoint
- Full traceability through gateway
"""

import os
import sys
from typing import List, Dict, Any
from base_gateway_client import GatewayClient, create_client

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class GatewayAgent:
    """
    Sample agent that uses the LLM Gateway.
    
    This agent uses virtual keys and connects through the gateway,
    allowing centralized management of LLM providers and costs.
    """
    
    def __init__(self, client: GatewayClient = None):
        """
        Initialize the agent.
        
        Args:
            client: Optional pre-configured gateway client.
                   If not provided, creates from environment.
        """
        self.client = client or create_client()
        
        # Validate configuration
        if not os.getenv('GATEWAY_VIRTUAL_KEY'):
            raise ValueError(
                "GATEWAY_VIRTUAL_KEY not set. "
                "Please set this environment variable with your virtual key."
            )
        
        print(f"Gateway Agent initialized")
        print(f"  Gateway URL: {self.client.config.base_url}")
        print(f"  Virtual Key: {self.client.config.virtual_key[:10]}...")
    
    def process_task(self, task: str, model: str = "gpt-4") -> str:
        """
        Process a task using the LLM Gateway.
        
        Args:
            task: The task description
            model: Model to use (e.g., "gpt-4", "gpt-3.5-turbo", "claude-3-opus")
            
        Returns:
            The LLM response
        """
        print(f"\nProcessing task with model: {model}")
        print(f"Task: {task[:100]}...")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Provide concise, accurate responses."
                    },
                    {
                        "role": "user",
                        "content": task
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the response content
            content = response['choices'][0]['message']['content']
            usage = response.get('usage', {})
            
            print(f"✓ Task completed successfully")
            print(f"  Tokens used: {usage.get('total_tokens', 'N/A')}")
            print(f"  Cost tracked: Yes (via gateway)")
            
            return content
            
        except Exception as e:
            print(f"✗ Task failed: {e}")
            raise
    
    def batch_process(self, tasks: List[str], model: str = "gpt-4") -> List[str]:
        """
        Process multiple tasks in batch.
        
        Args:
            tasks: List of task descriptions
            model: Model to use
            
        Returns:
            List of responses
        """
        results = []
        
        print(f"\nBatch processing {len(tasks)} tasks...")
        
        for i, task in enumerate(tasks, 1):
            print(f"\n--- Task {i}/{len(tasks)} ---")
            try:
                result = self.process_task(task, model)
                results.append(result)
            except Exception as e:
                print(f"Failed to process task {i}: {e}")
                results.append(f"Error: {str(e)}")
        
        return results
    
    def close(self):
        """Clean up resources."""
        if self.client:
            self.client.close()


def main():
    """
    Main execution function demonstrating the gateway agent.
    
    This demonstrates:
    1. Initializing agent with virtual key
    2. Processing tasks through gateway
    3. No provider keys in source code
    """
    print("=" * 60)
    print("LLM Gateway Sample Agent")
    print("=" * 60)
    
    # Show configuration
    print("\nConfiguration:")
    print(f"  GATEWAY_URL: {os.getenv('GATEWAY_URL', 'http://localhost:4000')}")
    print(f"  GATEWAY_VIRTUAL_KEY: {'Set' if os.getenv('GATEWAY_VIRTUAL_KEY') else 'Not set'}")
    print(f"  OPENAI_API_KEY in env: {'Yes (ignored)' if os.getenv('OPENAI_API_KEY') else 'No'}")
    
    # Initialize agent
    agent = GatewayAgent()
    
    try:
        # Example 1: Simple task
        print("\n" + "=" * 60)
        print("Example 1: Simple Task")
        print("=" * 60)
        
        response = agent.process_task(
            "What are 3 benefits of using a centralized LLM gateway?",
            model="gpt-4"
        )
        print(f"\nResponse:\n{response}")
        
        # Example 2: Different model
        print("\n" + "=" * 60)
        print("Example 2: Using GPT-3.5-Turbo")
        print("=" * 60)
        
        response = agent.process_task(
            "Summarize the concept of virtual API keys in one sentence.",
            model="gpt-3.5-turbo"
        )
        print(f"\nResponse:\n{response}")
        
        # Example 3: Batch processing
        print("\n" + "=" * 60)
        print("Example 3: Batch Processing")
        print("=" * 60)
        
        tasks = [
            "Define 'security through separation of concerns'.",
            "What is the benefit of centralized cost tracking?",
            "Explain how virtual keys enable team-based access control."
        ]
        
        responses = agent.batch_process(tasks, model="gpt-3.5-turbo")
        
        for i, response in enumerate(responses, 1):
            print(f"\n--- Response {i} ---")
            print(response)
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        print("\nKey Benefits Demonstrated:")
        print("  ✓ No hardcoded API keys in agent code")
        print("  ✓ Uses virtual key from environment")
        print("  ✓ Routes through gateway for centralized management")
        print("  ✓ Costs tracked at gateway level")
        print("  ✓ Easy to switch models without code changes")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure the gateway is running: make start-gateway")
        print("  2. Check your virtual key: make list-keys")
        print("  3. Verify GATEWAY_URL and GATEWAY_VIRTUAL_KEY environment variables")
        raise
    
    finally:
        agent.close()


if __name__ == "__main__":
    main()
