# LLM Router Gateway Integration

## Track 2: Platform-Managed LLM Gateway

This project implements a platform-managed LLM gateway using LiteLLM Proxy, enabling agents to use virtual keys instead of hardcoded provider API keys.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Make
- Python 3.9+ (for agent development)

### Installation

1. **Clone and navigate to the project:**
   ```bash
      cd hackathon
         ```

         2. **Run the setup script:**
            ```bash
               ./scripts/setup-gateway.sh
                  ```

                     Or use Make:
                        ```bash
                           make init-gateway
                              ```

                              3. **Configure environment variables:**
                                 ```bash
                                    cp .env.gateway.example .env.gateway
                                       # Edit .env.gateway with your API keys
                                          ```

                                          4. **Start the gateway:**
                                             ```bash
                                                make start-gateway
                                                   ```

                                                   5. **Generate a virtual key:**
                                                      ```bash
                                                         make generate-key team=myteam models="gpt-4,gpt-3.5-turbo"
                                                            ```

                                                            6. **Test with sample agent:**
                                                               ```bash
                                                                  make test-agent-gateway
                                                                     ```

                                                                     ## Project Structure

                                                                     ```
                                                                     ├── config/
                                                                     │   └── gateway-config.yaml          # Gateway configuration
                                                                     ├── docker/
                                                                     │   └── docker-compose.gateway.yml   # Docker deployment
                                                                     ├── agents/
                                                                     │   ├── base_gateway_client.py       # Gateway client library
                                                                     │   ├── sample-agent-gateway.py      # New pattern (virtual keys)
                                                                     │   └── sample-agent-legacy.py       # Legacy pattern (backward compat)
                                                                     ├── scripts/
                                                                     │   ├── setup-gateway.sh             # One-command setup
                                                                     │   └── generate-virtual-key.sh      # Virtual key generation
                                                                     ├── k8s/
                                                                     │   ├── gateway-deployment.yaml      # Kubernetes deployment
                                                                     │   └── secrets.yaml                 # Kubernetes secrets
                                                                     ├── Makefile                         # Build automation
                                                                     ├── .env.gateway.example             # Environment template
                                                                     └── README.md                        # This file
                                                                     ```

                                                                     ## Architecture

                                                                     ### Current State (Legacy)
                                                                     ```
                                                                     Agent (Hardcoded API Key) → Provider API → LLM
                                                                     ```

                                                                     ### Target State (Gateway)
                                                                     ```
                                                                     Agent (Virtual Key) → LLM Gateway → Provider API → LLM
                                                                     ```

                                                                     **Benefits:**
                                                                     - No hardcoded API keys in agent code
                                                                     - Centralized cost tracking
                                                                     - Team-based access control
                                                                     - Easy provider switching
                                                                     - Request caching and rate limiting
                                                                     - Full observability

                                                                     ## Gateway Selection

                                                                     ### LiteLLM Proxy (Recommended)

                                                                     **Pros:**
                                                                     - Open-source with active community
                                                                     - 100+ provider support
                                                                     - Built-in virtual keys and cost tracking
                                                                     - Self-hosted for full control
                                                                     - OpenTelemetry support

                                                                     **Cons:**
                                                                     - Requires infrastructure management
                                                                     - Learning curve for advanced features

                                                                     ### Portkey (Alternative)

                                                                     **Pros:**
                                                                     - Managed service option
                                                                     - Excellent developer experience
                                                                     - Built-in prompt management

                                                                     **Cons:**
                                                                     - Vendor lock-in
                                                                     - Less provider flexibility
                                                                     - Self-hosted option less mature

                                                                     ## Make Commands

                                                                     ```bash
                                                                     # Gateway Management
                                                                     make start-gateway          # Start gateway and dependencies
                                                                     make stop-gateway           # Stop gateway
                                                                     make restart-gateway        # Restart gateway
                                                                     make gateway-logs           # View gateway logs
                                                                     make gateway-status         # Check gateway status

                                                                     # Initialization
                                                                     make init-gateway           # Initialize gateway (first time)

                                                                     # Virtual Keys
                                                                     make generate-key team=myteam models="gpt-4"  # Generate virtual key
                                                                     make list-keys              # List all virtual keys
                                                                     make delete-key key=<key>   # Delete a virtual key

                                                                     # Testing
                                                                     make test-agent-gateway     # Test new gateway agent
                                                                     make test-agent-legacy      # Test legacy agent
                                                                     make test-integration       # Run integration tests

                                                                     # Kubernetes
                                                                     make k8s-deploy             # Deploy to Kubernetes
                                                                     make k8s-delete             # Delete K8s deployment
                                                                     make k8s-logs               # View K8s logs

                                                                     # Cleanup
                                                                     make clean                  # Clean up all resources
                                                                     ```

                                                                     ## Configuration

                                                                     ### Environment Variables

                                                                     Create `.env.gateway`:

                                                                     ```bash
                                                                     # Provider API Keys (stored only in gateway)
                                                                     OPENAI_API_KEY=sk-your-openai-key
                                                                     ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

                                                                     # Gateway Configuration
                                                                     LITELLM_MASTER_KEY=sk-litellm-master-random-string

                                                                     # Database
                                                                     POSTGRES_PASSWORD=secure-password
                                                                     DATABASE_URL=postgresql://litellm:secure-password@postgres:5432/litellm

                                                                     # Agent Configuration (set after generating virtual key)
                                                                     GATEWAY_URL=http://localhost:4000
                                                                     GATEWAY_VIRTUAL_KEY=sk-litellm-v1-virtual-key
                                                                     ```

                                                                     ### Gateway Config

                                                                     Edit `config/gateway-config.yaml` to:
                                                                     - Add/remove models
                                                                     - Configure rate limits
                                                                     - Set budgets
                                                                     - Enable caching

                                                                     ## Agent Migration

                                                                     ### From Legacy (Direct Keys)

                                                                     **Before:**
                                                                     ```python
                                                                     import os
                                                                     from openai import OpenAI

                                                                     client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                                                                     response = client.chat.completions.create(
                                                                         model="gpt-4",
                                                                             messages=[...]
                                                                             )
                                                                             ```

                                                                             **After:**
                                                                             ```python
                                                                             import os
                                                                             from base_gateway_client import create_client

                                                                             client = create_client()
                                                                             response = client.chat.completions.create(
                                                                                 model="gpt-4",
                                                                                     messages=[...]
                                                                                     )
                                                                                     ```

                                                                                     **Environment:**
                                                                                     ```bash
                                                                                     # Before
                                                                                     export OPENAI_API_KEY='sk-...'

                                                                                     # After
                                                                                     export GATEWAY_URL='http://localhost:4000'
                                                                                     export GATEWAY_VIRTUAL_KEY='sk-litellm-...'
                                                                                     ```

                                                                                     ## Security Best Practices

                                                                                     1. **Never commit API keys**
                                                                                        - `.env.gateway` is in `.gitignore`
                                                                                           - Use virtual keys for agents

                                                                                           2. **Use separate virtual keys per team**
                                                                                              - Budget isolation
                                                                                                 - Model access control
                                                                                                    - Audit trail

                                                                                                    3. **Rotate keys regularly**
                                                                                                       ```bash
                                                                                                          # Generate new key
                                                                                                             make generate-key team=myteam
                                                                                                                
                                                                                                                   # Update agents
                                                                                                                      # Delete old key
                                                                                                                         make delete-key key=old-key
                                                                                                                            ```

                                                                                                                            4. **Monitor usage**
                                                                                                                               - Gateway UI: http://localhost:4000/ui
                                                                                                                                  - Check logs: `make gateway-logs`

                                                                                                                                  ## Testing

                                                                                                                                  ### Unit Tests

                                                                                                                                  ```bash
                                                                                                                                  # Test gateway connectivity
                                                                                                                                  python -m pytest tests/test_gateway.py -v

                                                                                                                                  # Test agent integration
                                                                                                                                  python -m pytest tests/test_agent_integration.py -v
                                                                                                                                  ```

                                                                                                                                  ### Integration Tests

                                                                                                                                  ```bash
                                                                                                                                  make test-integration
                                                                                                                                  ```

                                                                                                                                  ### Load Tests

                                                                                                                                  ```bash
                                                                                                                                  make test-load
                                                                                                                                  ```

                                                                                                                                  ## Troubleshooting

                                                                                                                                  ### Gateway won't start

                                                                                                                                  1. Check Docker is running
                                                                                                                                  2. Verify `.env.gateway` exists and is populated
                                                                                                                                  3. Check logs: `make gateway-logs`
                                                                                                                                  4. Ensure ports 4000, 5432 are available

                                                                                                                                  ### Virtual key doesn't work

                                                                                                                                  1. Verify gateway is running: `make gateway-status`
                                                                                                                                  2. Check key exists: `make list-keys`
                                                                                                                                  3. Ensure `GATEWAY_VIRTUAL_KEY` is set correctly
                                                                                                                                  4. Verify key hasn't expired

                                                                                                                                  ### Agent can't connect

                                                                                                                                  1. Check `GATEWAY_URL` environment variable
                                                                                                                                  2. Ensure gateway is healthy: `curl http://localhost:4000/health`
                                                                                                                                  3. Check network connectivity
                                                                                                                                  4. Verify virtual key has access to requested model

                                                                                                                                  ## Documentation

                                                                                                                                  - [Architecture Overview](docs/ARCHITECTURE.md)
                                                                                                                                  - [Migration Guide](docs/MIGRATION.md)
                                                                                                                                  - [API Reference](docs/API.md)
                                                                                                                                  - [Troubleshooting](docs/TROUBLESHOOTING.md)

                                                                                                                                  ## Acceptance Criteria

                                                                                                                                  - [x] Gateway auto-deploys through `make start-nasiko`
                                                                                                                                  - [x] Sample agent completes LLM call without provider key in source
                                                                                                                                  - [x] Changing provider is gateway-config only with no agent code change
                                                                                                                                  - [x] Existing agents keep working without modification
                                                                                                                                  - [x] Documentation warns against hardcoding model keys
                                                                                                                                  - [x] Provider credentials managed centrally in gateway config/secrets
                                                                                                                                  - [x] Choice of LiteLLM documented with trade-off rationale

                                                                                                                                  ## Contributing

                                                                                                                                  1. Fork the repository
                                                                                                                                  2. Create a feature branch
                                                                                                                                  3. Make changes
                                                                                                                                  4. Run tests: `make test-integration`
                                                                                                                                  5. Submit a pull request

                                                                                                                                  ## License

                                                                                                                                  MIT License - See LICENSE file for details

                                                                                                                                  ## Support

                                                                                                                                  - GitHub Issues: Report bugs and feature requests
                                                                                                                                  - Documentation: Check `/docs` directory
                                                                                                                                  - Gateway UI: http://localhost:4000/ui (when running)