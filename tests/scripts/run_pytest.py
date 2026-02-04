#!/usr/bin/env python3
"""
Script Python para executar testes de forma programática
Uso: python run_pytest.py [opção]
"""

import sys
import subprocess
import os
from pathlib import Path


class Colors:
    """Cores ANSI para output colorido"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color


class TestRunner:
    """Classe para executar testes pytest"""
    
    def __init__(self):
        self.base_cmd = ['pytest']
        self.test_dir = Path(__file__).parent
        
    def print_banner(self):
        """Exibe banner do sistema"""
        print(f"{Colors.BLUE}")
        print("╔════════════════════════════════════════════════════════╗")
        print("║   Sistema de Veículos e Peças - Testes Python         ║")
        print("╚════════════════════════════════════════════════════════╝")
        print(f"{Colors.NC}\n")
    
    def run_command(self, cmd, description=None):
        """Executa um comando e retorna o resultado"""
        if description:
            print(f"{Colors.CYAN}📋 {description}{Colors.NC}")
        
        print(f"{Colors.YELLOW}Executando: {' '.join(cmd)}{Colors.NC}\n")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=False,
                text=True,
                cwd=self.test_dir
            )
            
            if result.returncode == 0:
                print(f"\n{Colors.GREEN}✅ Sucesso!{Colors.NC}\n")
                return True
            else:
                print(f"\n{Colors.RED}❌ Falhou com código {result.returncode}{Colors.NC}\n")
                return False
                
        except Exception as e:
            print(f"{Colors.RED}❌ Erro ao executar: {e}{Colors.NC}")
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        cmd = self.base_cmd + ['-v', '--tb=short']
        return self.run_command(cmd, "Executando todos os testes")
    
    def run_with_coverage(self):
        """Executa testes com cobertura"""
        cmd = self.base_cmd + [
            '--cov=.',
            '--cov-report=html',
            '--cov-report=term-missing',
            '-v'
        ]
        result = self.run_command(cmd, "Executando testes com cobertura")
        
        if result:
            print(f"{Colors.GREEN}📊 Relatório gerado em: htmlcov/index.html{Colors.NC}\n")
        
        return result
    
    def run_unit_tests(self):
        """Executa apenas testes unitários"""
        cmd = self.base_cmd + ['test_*_model.py', '-v']
        return self.run_command(cmd, "Executando testes unitários")
    
    def run_integration_tests(self):
        """Executa apenas testes de integração"""
        cmd = self.base_cmd + ['test_*_service.py', '-v']
        return self.run_command(cmd, "Executando testes de integração")
    
    def run_e2e_tests(self):
        """Executa apenas testes E2E"""
        cmd = self.base_cmd + ['test_*_flow.py', 'test_integracao.py', '-v']
        return self.run_command(cmd, "Executando testes E2E")
    
    def run_quick_tests(self):
        """Executa testes rápidos"""
        cmd = self.base_cmd + ['test_*_model.py', '--tb=line', '-q']
        return self.run_command(cmd, "Executando testes rápidos")
    
    def run_parallel_tests(self):
        """Executa testes em paralelo"""
        cmd = self.base_cmd + ['-n', 'auto', '-v']
        return self.run_command(cmd, "Executando testes em paralelo")
    
    def run_specific_test(self, test_path):
        """Executa um teste específico"""
        cmd = self.base_cmd + [test_path, '-v']
        return self.run_command(cmd, f"Executando teste: {test_path}")
    
    def list_tests(self):
        """Lista todos os testes disponíveis"""
        cmd = self.base_cmd + ['--collect-only', '-q']
        return self.run_command(cmd, "Listando testes disponíveis")
    
    def show_stats(self):
        """Mostra estatísticas dos testes"""
        print(f"{Colors.CYAN}📊 Estatísticas dos Testes{Colors.NC}\n")
        
        # Contar arquivos de teste
        test_files = list(self.test_dir.glob('test_*.py'))
        print(f"Arquivos de teste: {Colors.GREEN}{len(test_files)}{Colors.NC}")
        
        # Coletar informações sobre testes
        try:
            result = subprocess.run(
                ['pytest', '--collect-only', '-q'],
                capture_output=True,
                text=True,
                cwd=self.test_dir
            )
            
            lines = result.stdout.strip().split('\n')
            if lines:
                last_line = lines[-1]
                if 'test' in last_line.lower():
                    print(f"Total de testes: {Colors.GREEN}{last_line}{Colors.NC}")
        except:
            print(f"{Colors.YELLOW}Não foi possível contar testes{Colors.NC}")
        
        print()
    
    def clean_cache(self):
        """Remove cache do pytest"""
        print(f"{Colors.YELLOW}🧹 Limpando cache...{Colors.NC}\n")
        
        paths_to_remove = [
            '.pytest_cache',
            '__pycache__',
            'htmlcov',
            '.coverage'
        ]
        
        for path_name in paths_to_remove:
            path = self.test_dir / path_name
            if path.exists():
                if path.is_file():
                    path.unlink()
                else:
                    import shutil
                    shutil.rmtree(path)
                print(f"  Removido: {path_name}")
        
        # Remover __pycache__ em subdiretórios
        for pycache in self.test_dir.rglob('__pycache__'):
            import shutil
            shutil.rmtree(pycache, ignore_errors=True)
        
        print(f"\n{Colors.GREEN}✅ Cache limpo!{Colors.NC}\n")
    
    def show_menu(self):
        """Mostra menu interativo"""
        print(f"{Colors.YELLOW}Escolha uma opção:{Colors.NC}\n")
        print(f"  {Colors.GREEN}1{Colors.NC})  Executar todos os testes")
        print(f"  {Colors.GREEN}2{Colors.NC})  Executar testes com cobertura")
        print(f"  {Colors.GREEN}3{Colors.NC})  Executar apenas testes unitários")
        print(f"  {Colors.GREEN}4{Colors.NC})  Executar apenas testes de integração")
        print(f"  {Colors.GREEN}5{Colors.NC})  Executar apenas testes E2E")
        print(f"  {Colors.GREEN}6{Colors.NC})  Executar testes rápidos")
        print(f"  {Colors.GREEN}7{Colors.NC})  Executar testes em paralelo")
        print(f"  {Colors.GREEN}8{Colors.NC})  Listar todos os testes")
        print(f"  {Colors.GREEN}9{Colors.NC})  Mostrar estatísticas")
        print(f"  {Colors.GREEN}10{Colors.NC}) Limpar cache")
        print(f"  {Colors.GREEN}0{Colors.NC})  Sair\n")
    
    def interactive_mode(self):
        """Modo interativo"""
        self.print_banner()
        
        while True:
            self.show_menu()
            choice = input(f"{Colors.CYAN}Opção: {Colors.NC}").strip()
            print()
            
            if choice == '1':
                self.run_all_tests()
            elif choice == '2':
                self.run_with_coverage()
            elif choice == '3':
                self.run_unit_tests()
            elif choice == '4':
                self.run_integration_tests()
            elif choice == '5':
                self.run_e2e_tests()
            elif choice == '6':
                self.run_quick_tests()
            elif choice == '7':
                self.run_parallel_tests()
            elif choice == '8':
                self.list_tests()
            elif choice == '9':
                self.show_stats()
            elif choice == '10':
                self.clean_cache()
            elif choice == '0':
                print(f"{Colors.GREEN}👋 Até logo!{Colors.NC}")
                break
            else:
                print(f"{Colors.RED}❌ Opção inválida{Colors.NC}\n")
            
            if choice != '0':
                input(f"\n{Colors.YELLOW}Pressione Enter para continuar...{Colors.NC}")
                print("\n" * 2)


def main():
    """Função principal"""
    runner = TestRunner()
    
    if len(sys.argv) == 1:
        # Modo interativo se não houver argumentos
        runner.interactive_mode()
    else:
        # Modo CLI com argumentos
        command = sys.argv[1].lower()
        
        runner.print_banner()
        
        if command == 'all':
            runner.run_all_tests()
        elif command == 'coverage':
            runner.run_with_coverage()
        elif command == 'unit':
            runner.run_unit_tests()
        elif command == 'integration':
            runner.run_integration_tests()
        elif command == 'e2e':
            runner.run_e2e_tests()
        elif command == 'quick':
            runner.run_quick_tests()
        elif command == 'parallel':
            runner.run_parallel_tests()
        elif command == 'list':
            runner.list_tests()
        elif command == 'stats':
            runner.show_stats()
        elif command == 'clean':
            runner.clean_cache()
        elif command == 'help':
            print(f"{Colors.CYAN}Uso: python run_pytest.py [opção]{Colors.NC}\n")
            print("Opções disponíveis:")
            print("  all         - Executar todos os testes")
            print("  coverage    - Executar com cobertura")
            print("  unit        - Apenas testes unitários")
            print("  integration - Apenas testes de integração")
            print("  e2e         - Apenas testes E2E")
            print("  quick       - Testes rápidos")
            print("  parallel    - Executar em paralelo")
            print("  list        - Listar todos os testes")
            print("  stats       - Mostrar estatísticas")
            print("  clean       - Limpar cache")
            print("  help        - Mostrar esta ajuda")
            print("\nSem argumentos: modo interativo")
        else:
            # Assumir que é um arquivo de teste específico
            runner.run_specific_test(command)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Interrompido pelo usuário{Colors.NC}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}❌ Erro: {e}{Colors.NC}")
        sys.exit(1)