# LLM Gateway Integration - Makefile
# Provides commands to manage the LLM Gateway and related services

.PHONY: help start-gateway stop-gateway restart-gateway gateway-logs gateway-status
.PHONY: start-nasiko stop-nasiko init-gateway generate-key
.PHONY: test-agent-legacy test-agent-gateway test-integration
.PHONY: k8s-deploy k8s-delete k8s-logs
.PHONY: docs clean

# Configuration
GATEWAY_COMPOSE=docker/docker-compose.gateway.yml
K8S_DIR=k8s
AGENT_DIR=agents
SCRIPTS_DIR=scripts

# Default target
.DEFAULT_GOAL := help

## ============================================
## Help
## ============================================

help: ## Show this help message
	@echo "LLM Gateway - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  1. Copy .env.gateway.example to .env.gateway and fill in values"
	@echo "  2. Run: make init-gateway"
	@echo "  3. Run: make start-gateway"
	@echo "  4. Run: make generate-key team=myteam"
	@echo "  5. Run: make test-agent-gateway"

## ============================================
## Gateway Management
## ============================================

start-gateway: ## Start the LLM Gateway and dependencies
	@echo "========================================"
	@echo "Starting LLM Gateway..."
	@echo "========================================"
	docker-compose -f $(GATEWAY_COMPOSE) up -d
	@echo ""
	@echo "Waiting for services to be healthy..."
	@sleep 15
	@echo ""
	@echo "Gateway Status:"
	@docker-compose -f $(GATEWAY_COMPOSE) ps
	@echo ""
	@echo "Gateway URL: http://localhost:4000"
	@echo "Health Check: http://localhost:4000/health"
	@echo ""
	@echo "To generate virtual keys, run: make generate-key team=<name>"

stop-gateway: ## Stop the LLM Gateway and dependencies
	@echo "Stopping LLM Gateway..."
	docker-compose -f $(GATEWAY_COMPOSE) down
	@echo "Gateway stopped."

restart-gateway: stop-gateway start-gateway ## Restart the LLM Gateway

gateway-logs: ## View gateway logs
	docker-compose -f $(GATEWAY_COMPOSE) logs -f litellm-gateway

gateway-status: ## Check gateway status
	@echo "Gateway Containers:"
	@docker-compose -f $(GATEWAY_COMPOSE) ps
	@echo ""
	@echo "Health Check:"
	@curl -s http://localhost:4000/health | jq . || echo "Gateway not responding"

## ============================================
## Initialization
## ============================================

init-gateway: ## Initialize gateway (first time setup)
	@echo "========================================"
	@echo "Initializing LLM Gateway..."
	@echo "========================================"
	@echo ""
	@if [ ! -f .env.gateway ]; then \
		echo "Creating .env.gateway from template..."; \
		cp .env.gateway.example .env.gateway; \
		echo "Please edit .env.gateway with your actual API keys"; \
		echo "Then run: make init-gateway again"; \
		exit 1; \
	fi
	@echo "Environment file found."
	@echo ""
	@echo "Starting services..."
	$(MAKE) start-gateway
	@echo ""
	@echo "========================================"
	@echo "Gateway initialized successfully!"
	@echo "========================================"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Generate virtual keys: make generate-key team=<name>"
	@echo "  2. Update agent environment variables"
	@echo "  3. Test with: make test-agent-gateway"

## ============================================
## Virtual Key Management
## ============================================

generate-key: ## Generate a virtual key (usage: make generate-key team=<name> models="gpt-4,gpt-3.5-turbo")
	@if [ -z "$(team)" ]; then \
		echo "Error: team parameter required"; \
		echo "Usage: make generate-key team=<name> models='gpt-4,gpt-3.5-turbo'"; \
		exit 1; \
	fi
	@echo "Generating virtual key for team: $(team)"
	@TEAM="$(team)" \
	MODELS="$(or $(models),gpt-4,gpt-3.5-turbo)" \
	BUDGET="$(or $(budget),100.0)" \
	$(SCRIPTS_DIR)/generate-virtual-key.sh

list-keys: ## List all virtual keys
	@echo "Listing virtual keys..."
	@curl -s http://localhost:4000/key/list \
		-H "Authorization: Bearer $$LITELLM_MASTER_KEY" | jq .

delete-key: ## Delete a virtual key (usage: make delete-key key=<key>)
	@if [ -z "$(key)" ]; then \
		echo "Error: key parameter required"; \
		exit 1; \
	fi
	@echo "Deleting virtual key: $(key)"
	@curl -s -X POST http://localhost:4000/key/delete \
		-H "Authorization: Bearer $$LITELLM_MASTER_KEY" \
		-H "Content-Type: application/json" \
		-d '{"key": "$(key)"}' | jq .

## ============================================
## Orchestrator Integration (Nasiko)
## ============================================

start-nasiko: start-gateway ## Start Nasiko orchestrator with LLM Gateway
	@echo "Starting Nasiko orchestrator with LLM Gateway..."
	@echo "Gateway is running at: http://localhost:4000"
	# Add your existing Nasiko startup commands here
	# Example: docker-compose -f docker-compose.nasiko.yml up -d
	@echo "Nasiko started successfully!"

stop-nasiko: ## Stop Nasiko orchestrator
	@echo "Stopping Nasiko orchestrator..."
	# Add your existing Nasiko stop commands here
	$(MAKE) stop-gateway
	@echo "Nasiko stopped."

## ============================================
## Testing
## ============================================

test-agent-legacy: ## Test legacy agent with direct provider keys
	@echo "Testing legacy agent..."
	cd $(AGENT_DIR) && python sample-agent-legacy.py

test-agent-gateway: ## Test agent with gateway virtual key
	@echo "Testing gateway agent..."
	cd $(AGENT_DIR) && python sample-agent-gateway.py

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	python -m pytest tests/ -v

test-load: ## Run load tests
	@echo "Running load tests..."
	python tests/test_load.py

## ============================================
## Kubernetes Deployment
## ============================================

k8s-deploy: ## Deploy to Kubernetes
	@echo "Deploying to Kubernetes..."
	kubectl apply -f $(K8S_DIR)/secrets.yaml
	kubectl apply -f $(K8S_DIR)/gateway-deployment.yaml
	@echo "Deployment complete."
	kubectl get pods -l app=litellm-gateway

k8s-delete: ## Delete Kubernetes deployment
	@echo "Deleting Kubernetes deployment..."
	kubectl delete -f $(K8S_DIR)/gateway-deployment.yaml
	kubectl delete -f $(K8S_DIR)/secrets.yaml

k8s-logs: ## View Kubernetes logs
	kubectl logs -l app=litellm-gateway --tail=100 -f

## ============================================
## Documentation
## ============================================

docs: ## Generate/update documentation
	@echo "Documentation is available in:"
	@echo "  - docs/ARCHITECTURE.md"
	@echo "  - docs/MIGRATION.md"
	@echo "  - docs/API.md"
	@echo "  - docs/TROUBLESHOOTING.md"

## ============================================
## Cleanup
## ============================================

clean: ## Clean up all resources
	@echo "Cleaning up..."
	docker-compose -f $(GATEWAY_COMPOSE) down -v
	docker system prune -f
	@echo "Cleanup complete."

## ============================================
## Development Helpers
## ============================================

shell-gateway: ## Open shell in gateway container
	docker-compose -f $(GATEWAY_COMPOSE) exec litellm-gateway /bin/sh

db-shell: ## Open PostgreSQL shell
	docker-compose -f $(GATEWAY_COMPOSE) exec postgres psql -U litellm -d litellm
