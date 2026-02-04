#!/bin/bash

# Script para executar testes automatizados
# Uso: ./run_tests.sh [opção]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para exibir banner
show_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║      Sistema de Veículos e Peças - Testes             ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Função para verificar dependências
check_dependencies() {
    echo -e "${YELLOW}Verificando dependências...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python3 não encontrado. Por favor, instale Python 3.8+${NC}"
        exit 1
    fi
    
    if ! command -v psql &> /dev/null; then
        echo -e "${RED}PostgreSQL não encontrado. Por favor, instale PostgreSQL${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Dependências verificadas${NC}"
}

# Função para instalar requirements
install_requirements() {
    echo -e "${YELLOW}Instalando dependências de teste...${NC}"
    pip install -r requirements-test.txt
    echo -e "${GREEN}✓ Dependências instaladas${NC}"
}

# Função para verificar banco de dados
check_database() {
    echo -e "${YELLOW}Verificando banco de dados...${NC}"
    
    if psql -lqt | cut -d \| -f 1 | grep -qw sistema_veiculos_test; then
        echo -e "${GREEN}✓ Banco de dados de teste encontrado${NC}"
    else
        echo -e "${YELLOW}Banco de dados de teste não encontrado. Criando...${NC}"
        createdb sistema_veiculos_test
        echo -e "${GREEN}✓ Banco de dados criado${NC}"
    fi
}

# Função para limpar cache do pytest
clean_cache() {
    echo -e "${YELLOW}Limpando cache...${NC}"
    rm -rf .pytest_cache
    rm -rf __pycache__
    rm -rf htmlcov
    rm -rf .coverage
    find . -type d -name "__pycache__" -exec rm -rf {} +
    echo -e "${GREEN}✓ Cache limpo${NC}"
}

# Função para executar todos os testes
run_all_tests() {
    echo -e "${BLUE}Executando todos os testes...${NC}"
    pytest -v --tb=short
}

# Função para executar testes com cobertura
run_with_coverage() {
    echo -e "${BLUE}Executando testes com cobertura...${NC}"
    pytest --cov=. --cov-report=html --cov-report=term-missing
    echo -e "${GREEN}✓ Relatório de cobertura gerado em htmlcov/index.html${NC}"
}

# Função para executar testes unitários
run_unit_tests() {
    echo -e "${BLUE}Executando testes unitários...${NC}"
    pytest test_*_model.py -v
}

# Função para executar testes de integração
run_integration_tests() {
    echo -e "${BLUE}Executando testes de integração...${NC}"
    pytest test_*_service.py -v
}

# Função para executar testes E2E
run_e2e_tests() {
    echo -e "${BLUE}Executando testes E2E...${NC}"
    pytest test_*_flow.py test_integracao.py -v
}

# Função para executar testes rápidos
run_quick_tests() {
    echo -e "${BLUE}Executando testes rápidos (unitários)...${NC}"
    pytest test_*_model.py --tb=line -q
}

# Função para executar testes em paralelo
run_parallel_tests() {
    echo -e "${BLUE}Executando testes em paralelo...${NC}"
    pytest -n auto -v
}

# Função para executar testes específicos
run_specific_test() {
    echo -e "${BLUE}Executando teste específico: $1${NC}"
    pytest "$1" -v
}

# Função para executar testes em modo watch
run_watch_mode() {
    echo -e "${BLUE}Modo watch ativado. Testes serão re-executados ao salvar arquivos.${NC}"
    echo -e "${YELLOW}Pressione Ctrl+C para sair${NC}"
    ptw -- -v
}

# Menu principal
show_menu() {
    echo -e "${YELLOW}"
    echo "Escolha uma opção:"
    echo "1) Executar todos os testes"
    echo "2) Executar testes com cobertura"
    echo "3) Executar apenas testes unitários"
    echo "4) Executar apenas testes de integração"
    echo "5) Executar apenas testes E2E"
    echo "6) Executar testes rápidos"
    echo "7) Executar testes em paralelo"
    echo "8) Modo watch (auto re-executar)"
    echo "9) Limpar cache"
    echo "10) Instalar dependências"
    echo "0) Sair"
    echo -e "${NC}"
}

# Processar argumentos da linha de comando
process_args() {
    case "$1" in
        all)
            run_all_tests
            ;;
        coverage)
            run_with_coverage
            ;;
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        e2e)
            run_e2e_tests
            ;;
        quick)
            run_quick_tests
            ;;
        parallel)
            run_parallel_tests
            ;;
        watch)
            run_watch_mode
            ;;
        clean)
            clean_cache
            ;;
        install)
            install_requirements
            ;;
        help)
            echo "Uso: ./run_tests.sh [opção]"
            echo ""
            echo "Opções disponíveis:"
            echo "  all         - Executar todos os testes"
            echo "  coverage    - Executar com cobertura"
            echo "  unit        - Apenas testes unitários"
            echo "  integration - Apenas testes de integração"
            echo "  e2e         - Apenas testes E2E"
            echo "  quick       - Testes rápidos"
            echo "  parallel    - Executar em paralelo"
            echo "  watch       - Modo watch"
            echo "  clean       - Limpar cache"
            echo "  install     - Instalar dependências"
            echo "  help        - Mostrar esta ajuda"
            ;;
        *)
            # Modo interativo
            show_banner
            check_dependencies
            
            while true; do
                show_menu
                read -p "Opção: " option
                
                case $option in
                    1)
                        run_all_tests
                        ;;
                    2)
                        run_with_coverage
                        ;;
                    3)
                        run_unit_tests
                        ;;
                    4)
                        run_integration_tests
                        ;;
                    5)
                        run_e2e_tests
                        ;;
                    6)
                        run_quick_tests
                        ;;
                    7)
                        run_parallel_tests
                        ;;
                    8)
                        run_watch_mode
                        ;;
                    9)
                        clean_cache
                        ;;
                    10)
                        install_requirements
                        ;;
                    0)
                        echo -e "${GREEN}Saindo...${NC}"
                        exit 0
                        ;;
                    *)
                        echo -e "${RED}Opção inválida${NC}"
                        ;;
                esac
                
                echo ""
                read -p "Pressione Enter para continuar..."
                clear
                show_banner
            done
            ;;
    esac
}

# Executar
show_banner
process_args "$1"