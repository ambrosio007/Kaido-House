from model.veiculos_model import VeiculoModel
from repository.veiculo_repository import VeiculoRepository
import os
from werkzeug.utils import secure_filename

class VeiculoService:

    @staticmethod
    def cadastrar_veiculo(dados, fotos=None):
        try:
            veiculo = VeiculoModel(**dados)
            
            # Processar upload de fotos
            fotos_salvas = []
            if fotos:
                upload_folder = 'static/uploads/veiculos'
                os.makedirs(upload_folder, exist_ok=True)
                
                for foto in fotos:
                    if foto and foto.filename:
                        filename = secure_filename(f"{veiculo.id}_{foto.filename}")
                        filepath = os.path.join(upload_folder, filename)
                        foto.save(filepath)
                        fotos_salvas.append(filepath)
            
            veiculo_dict = veiculo.to_dict()
            veiculo_dict['fotos'] = ','.join(fotos_salvas)
            
            status = VeiculoRepository.adicionar_veiculo(veiculo_dict)
            
            if status:
                return True, "Veículo cadastrado com sucesso!"
            else:
                return False, "Erro ao cadastrar veículo no banco de dados"
                
        except Exception as e:
            return False, f"Erro: {str(e)}"
    
    @staticmethod
    def listar_por_usuario(user_id):
        try:
            return VeiculoRepository.listar_por_usuario(user_id)
        except Exception as e:
            print(f"Erro ao listar veículos: {e}")
            return []
    
    @staticmethod
    def listar_todos():
        try:
            return VeiculoRepository.listar_todos()
        except Exception as e:
            print(f"Erro ao listar todos os veículos: {e}")
            return []
    
    @staticmethod
    def buscar_por_id(veiculo_id):
        try:
            return VeiculoRepository.buscar_por_id(veiculo_id)
        except Exception as e:
            print(f"Erro ao buscar veículo: {e}")
            return None
    
    @staticmethod
    def deletar_veiculo(veiculo_id):
        try:
            return VeiculoRepository.deletar(veiculo_id)
        except Exception as e:
            print(f"Erro ao deletar veículo: {e}")
            return False
    
    @staticmethod
    def atualizar_veiculo(veiculo_id, dados):
        try:
            return VeiculoRepository.atualizar_veiculo(veiculo_id, dados)
        except Exception as e:
            print(f"Erro ao atualizar veículo: {e}")
            return False
        
    @staticmethod
    def buscar_vitrine(apenas_novos=True, limit=5):
        """
        Busca veículos para a vitrine filtrando por novos ou usados.
        Consideramos 'novos' veículos com KM próximo a zero (ex: < 100km).
        """
        try:
            # Chama o repositório com o filtro de KM e o limite de 5 itens aleatórios
            return VeiculoRepository.listar_aleatorio_home(apenas_novos=apenas_novos, limit=limit)
        except Exception as e:
            print(f"Erro ao buscar vitrine de veículos: {e}")
            return []