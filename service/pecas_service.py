from model.pecas_model import PecaModel
from repository.pecas_repository import PecaRepository
import os
from werkzeug.utils import secure_filename

class PecaService:

    @staticmethod
    def cadastrar_peca(dados, fotos=None):
        try:
            peca = PecaModel(**dados)
            
            # Processar upload de fotos
            fotos_salvas = []
            if fotos:
                upload_folder = 'static/uploads/pecas'
                os.makedirs(upload_folder, exist_ok=True)
                
                for foto in fotos:
                    if foto and foto.filename:
                        filename = secure_filename(f"{peca.id}_{foto.filename}")
                        filepath = os.path.join(upload_folder, filename)
                        foto.save(filepath)
                        fotos_salvas.append(filepath)
            
            peca_dict = peca.to_dict()
            peca_dict['fotos'] = ','.join(fotos_salvas)
            
            status = PecaRepository.adicionar_peca(peca_dict)
            
            if status:
                return True, "Peça cadastrada com sucesso!"
            else:
                return False, "Erro ao cadastrar peça no banco de dados"
                
        except Exception as e:
            return False, f"Erro: {str(e)}"
    
    @staticmethod
    def listar_por_usuario(user_id):
        try:
            return PecaRepository.listar_por_usuario(user_id)
        except Exception as e:
            print(f"Erro ao listar peças: {e}")
            return []
    
    @staticmethod
    def listar_todos(categoria=None, estado=None):
        try:
            return PecaRepository.listar_todos(categoria, estado)
        except Exception as e:
            print(f"Erro ao listar todas as peças: {e}")
            return []
    
    @staticmethod
    def buscar_por_id(peca_id):
        try:
            return PecaRepository.buscar_por_id(peca_id)
        except Exception as e:
            print(f"Erro ao buscar peça: {e}")
            return None
    
    @staticmethod
    def deletar_peca(peca_id):
        try:
            return PecaRepository.deletar(peca_id)
        except Exception as e:
            print(f"Erro ao deletar peça: {e}")
            return False
    
    @staticmethod
    def atualizar_peca(peca_id, dados):
        try:
            return PecaRepository.atualizar_peca(peca_id, dados)
        except Exception as e:
            print(f"Erro ao atualizar peça: {e}")
            return False

    @staticmethod
    def buscar_vitrine(estado=None, limit=5):
        """
        Busca peças para a vitrine da Home de forma aleatória.
        """
        try:
            # Chama o repositório passando o filtro de estado (novo/usado) e o limite
            return PecaRepository.listar_aleatorio(estado=estado, limit=limit)
        except Exception as e:
            print(f"Erro ao buscar vitrine de peças: {e}")
            return []