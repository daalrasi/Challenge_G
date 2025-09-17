# ====== Config ======
DC ?= docker compose
API := http://localhost:8081
HEALTH := $(API)/healthz

# ====== Ayuda ======
.PHONY: help
help: ## Lista los comandos disponibles
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' Makefile | awk -F':.*## ' '{printf " - %s\n", $$1}'


# ====== Docker ======
.PHONY: up
up: ## Construye y levanta la app en segundo plano
	$(DC) up --build -d

.PHONY: down
down: ## Detiene y elimina los contenedores y volúmenes
	$(DC) down -v

.PHONY: logs
logs: ## Muestra logs del servicio api
	$(DC) logs -f api

.PHONY: wait
wait: ## Espera a que /healthz responda 200
	@bash scripts/wait_for.sh $(HEALTH)

# ====== Seeds ======
.PHONY: seed
seed: ## Carga CSVs de catálogos
	@bash scripts/seed.sh

# ====== Batches por curl ======
.PHONY: curl-batch
curl-batch: ## Envía batch.json (<=1000 items)
	@curl -s -X POST "$(API)/insert_batch" \
	 -H "Content-Type: application/json" \
	 -d @batch.json | tee /dev/tty

.PHONY: curl-batch-big
curl-batch-big: ## Envía batch_big.json (>1000 items -> esperado 422)
	@curl -i -s -X POST "$(API)/insert_batch" \
	 -H "Content-Type: application/json" \
	 -d @batch_big.json | tee /dev/tty

# ====== Complete ======
.PHONY: dev
dev: up wait seed ## Levanta, espera, carga datos
	@echo "Dev listo: $(API)/docs"

# ====== Tests ======
.PHONY: test
test: up wait seed ## Ejecuta pytest contra la API levantada
	pytest -q

# Opcional: test + tear down
.PHONY: test-clean
test-clean: up wait seed
	pytest -q || ( $(DC) logs api ; false )
	$(DC) down -v
