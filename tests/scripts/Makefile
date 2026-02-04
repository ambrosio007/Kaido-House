.PHONY: help install test test-unit test-integration test-e2e test-coverage test-quick test-parallel clean setup

# Variáveis
PYTHON := python3
PIP := pip
PYTEST := pytest
COVERAGE := coverage

# Cores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Mostra esta mensagem de ajuda
	@echo "$(BLUE)════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Sistema de Veículos e Peças - Comandos de Teste$(NC)"
	@echo "$(BLUE)════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Instala todas as dependências
	@echo "$(YELLOW)Instalando dependências...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-test.txt
	@echo "$(GREEN)✓ Dependências instaladas$(NC)"

setup: install ## Configuração inicial completa
	@echo "$(YELLOW)Configurando ambiente de teste...$(NC)"
	@createdb sistema_veiculos_test 2>/dev/null || echo "Banco já existe"
	@$(PYTHON) migrate.py
	@echo "$(GREEN)✓ Ambiente configurado$(NC)"

test: ## Executa todos os testes
	@echo "$(BLUE)Executando todos os testes...$(NC)"
	$(PYTEST) -v --tb=short

test-unit: ## Executa apenas testes unitários
	@echo "$(BLUE)Executando testes unitários...$(NC)"
	$(PYTEST) test_*_model.py -v

test-integration: ## Executa apenas testes de integração
	@echo "$(BLUE)Executando testes de integração...$(NC)"
	$(PYTEST) test_*_service.py -v

test-e2e: ## Executa apenas testes E2E
	@echo "$(BLUE)Executando testes E2E...$(NC)"
	$(PYTEST) test_*_flow.py test_integracao.py -v

test-coverage: ## Executa testes com relatório de cobertura
	@echo "$(BLUE)Executando testes com cobertura...$(NC)"
	$(PYTEST) --cov=. --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Relatório gerado em htmlcov/index.html$(NC)"

test-coverage-xml: ## Gera relatório de cobertura em XML (para CI/CD)
	$(PYTEST) --cov=. --cov-report=xml

test-quick: ## Executa testes rápidos (apenas unitários)
	@echo "$(BLUE)Executando testes rápidos...$(NC)"
	$(PYTEST) test_*_model.py --tb=line -q

test-parallel: ## Executa testes em paralelo
	@echo "$(BLUE)Executando testes em paralelo...$(NC)"
	$(PYTEST) -n auto -v

test-watch: ## Modo watch - re-executa testes ao salvar
	@echo "$(BLUE)Modo watch ativado$(NC)"
	ptw -- -v

test-failed: ## Re-executa apenas testes que falharam
	@echo "$(BLUE)Re-executando testes que falharam...$(NC)"
	$(PYTEST) --lf -v

test-specific: ## Executa um teste específico (use: make test-specific TEST=test_file.py)
	@echo "$(BLUE)Executando teste: $(TEST)$(NC)"
	$(PYTEST) $(TEST) -v

clean: ## Remove cache e arquivos temporários
	@echo "$(YELLOW)Limpando cache...$(NC)"
	@rm -rf .pytest_cache
	@rm -rf __pycache__
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf coverage.xml
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Cache limpo$(NC)"

clean-db: ## Limpa o banco de dados de teste
	@echo "$(YELLOW)Limpando banco de dados...$(NC)"
	@dropdb sistema_veiculos_test 2>/dev/null || echo "Banco não existe"
	@createdb sistema_veiculos_test
	@$(PYTHON) migrate.py
	@echo "$(GREEN)✓ Banco de dados limpo e recriado$(NC)"

lint: ## Verifica qualidade do código
	@echo "$(BLUE)Verificando qualidade do código...$(NC)"
	@$(PIP) install flake8 pylint 2>/dev/null || true
	@flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Formata o código com black
	@echo "$(BLUE)Formatando código...$(NC)"
	@$(PIP) install black 2>/dev/null || true
	@black . --exclude venv
	@echo "$(GREEN)✓ Código formatado$(NC)"

report: test-coverage ## Abre o relatório de cobertura no navegador
	@echo "$(BLUE)Abrindo relatório de cobertura...$(NC)"
	@xdg-open htmlcov/index.html 2>/dev/null || open htmlcov/index.html 2>/dev/null || echo "Abra manualmente: htmlcov/index.html"

check: lint test ## Verifica código e executa testes
	@echo "$(GREEN)✓ Verificação completa$(NC)"

ci: clean test-coverage-xml ## Simula ambiente de CI/CD
	@echo "$(GREEN)✓ Testes de CI concluídos$(NC)"

stats: ## Mostra estatísticas dos testes
	@echo "$(BLUE)Estatísticas dos testes:$(NC)"
	@echo "$(YELLOW)Arquivos de teste:$(NC)"
	@ls -1 test_*.py | wc -l
	@echo "$(YELLOW)Total de testes:$(NC)"
	@$(PYTEST) --collect-only -q | tail -n 1
	@echo "$(YELLOW)Duração estimada:$(NC)"
	@$(PYTEST) --collect-only --quiet | wc -l | awk '{print $$1 * 0.1 " segundos (aprox.)"}'

benchmark: ## Mostra os 10 testes mais lentos
	@echo "$(BLUE)Top 10 testes mais lentos:$(NC)"
	$(PYTEST) --durations=10

debug: ## Executa testes em modo debug
	@echo "$(BLUE)Modo debug ativado$(NC)"
	$(PYTEST) -v --tb=long --pdb-trace

list: ## Lista todos os testes disponíveis
	@echo "$(BLUE)Testes disponíveis:$(NC)"
	$(PYTEST) --collect-only -q

# Atalhos rápidos
t: test ## Atalho para 'make test'
tc: test-coverage ## Atalho para 'make test-coverage'
tu: test-unit ## Atalho para 'make test-unit'
ti: test-integration ## Atalho para 'make test-integration'
te: test-e2e ## Atalho para 'make test-e2e'
c: clean ## Atalho para 'make clean'