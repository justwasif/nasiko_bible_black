"""
Sample Legacy Agent (Direct Provider Keys)

This agent demonstrates the OLD pattern of using hardcoded provider API keys.
This agent is kept for backward compatibility testing.

IMPORTANT: This pattern is NOT recommended for new agents.
Use the gateway pattern (sample-agent-gateway.py) instead.

Key features:
- Uses direct provider API keys
- Hardcoded credentials (security risk)
- Connects directly to provider API
- No centralized cost tracking
"""

import os
import sys
from typing import List, Optional

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed")
    print("Install with: pip install openai")
    sys.exit(1)


class LegacyAgent:
    """
    Sample agent that uses direct provider API keys.
    
    WARNING: This is the legacy pattern. New agents should use the gateway pattern.
    This agent is maintained for backward compatibility only.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the agent with provider API key.
        
        Args:
            api_key: OpenAI API key. If not provided, reads from OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. "
                "Set OPENAI_API_KEY environment variable."
            )
        
        # Initialize OpenAI client with direct API key
        self.client = OpenAI(api_key=self.api_key)
        
        print(f"Legacy Agent initialized")
        print(f"  Provider: OpenAI")
        print(f"  API Key: {self.api_key[:10]}...")
        print(f"  ⚠️  WARNING: Using direct provider keys (legacy pattern)")
    
    def process_task(self, task: str, model: str = "gpt-4") -> str:
        """
        Process a task using direct provider API.
        
        Args:
            task: The task description
            model: Model to use (e.g., "gpt-4", "gpt-3.5-turbo")
            
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
            
            content = response.choices[0].message.content
            usage = response.usage
            
            print(f"✓ Task completed")
            print(f"  Tokens used: {usage.total_tokens if usage else 'N/A'}")
            print(f"  Cost tracked: No (direct API call)")
            
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


def main():
    """
    Main execution function demonstrating the legacy agent.
    
    This demonstrates the old pattern with hardcoded keys.
    For new development, use the gateway pattern instead.
    """
    print("=" * 60)
    print("Legacy Agent (Direct Provider Keys)")
    print("=" * 60)
    print("\n⚠️  WARNING: This demonstrates the OLD pattern.")
    print("   New agents should use: sample-agent-gateway.py")
    print("=" * 60)
    
    # Check if running in compatibility mode
    if os.getenv('FORCE_LEGACY_MODE'):
        print("\nRunning in forced legacy mode (FORCE_LEGACY_MODE=1)")
    
    # Show configuration
    print("\nConfiguration:")
    print(f"  OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"  Direct provider connection: Yes")
    print(f"  Gateway used: No")
    
    try:
        # Initialize agent
        agent = LegacyAgent()
        
        # Example task
        print("\n" + "=" * 60)
        print("Example: Processing task with direct API")
        print("=" * 60)
        
        response = agent.process_task(
            "What is 2+2?",
            model="gpt-3.5-turbo"
        )
        
        print(f"\nResponse:\n{response}")
        
        print("\n" + "=" * 60)
        print("Legacy agent completed successfully")
        print("=" * 60)
        print("\n⚠️  IMPORTANT: Migrate to gateway pattern for:")
        print("  • Better security (no hardcoded keys)")
        print("  • Centralized cost tracking")
        print("  • Team-based access control")
        print("  • Provider switching without code changes")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTo test legacy agent:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  python sample-agent-legacy.py")
        raise


if __name__ == "__main__":
    main()
