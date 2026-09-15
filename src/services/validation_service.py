"""
Serviço de validação que orquestra o processo de validação.
Interface entre a UI (Dikē .py) e o motor de validação (core).
"""
import pandas as pd
import logging
from typing import List, Tuple, Any
from ..validators.validation_engine import ValidationEngine
from ..models.models import Movimiento, Detalle, Pago

logger = logging.getLogger(__name__)

class ValidationService:
    """Serviço responsável por orquestrar o processo de validação."""
    
    def __init__(self):
        self.validation_engine = ValidationEngine()

    def _detect_file_type(self, filename: str) -> str:
        """
        Detect file type based on extension.

        Args:
            filename: Name of the file

        Returns:
            File type ('csv', 'xlsx', or default 'csv')
        """
        if not filename:
            return 'csv'

        filename_lower = filename.lower()
        if filename_lower.endswith('.xlsx') or filename_lower.endswith('.xls'):
            return 'xlsx'
        elif filename_lower.endswith('.csv'):
            return 'csv'
        else:
            # Default to csv for unknown extensions
            return 'csv'
    
    def validar_arquivos(
        self,
        roteiro_content: Any,
        cupons_content: List[Any],
        json_content: Any,
        roteiro_file_type: str = None
    ) -> Tuple[List[dict], List[str]]:
        """
        Valida os arquivos de entrada e retorna os resultados.

        Args:
            roteiro_content: Conteúdo do arquivo de roteiro de testes (XLSX/CSV)
            cupons_content: Lista de conteúdos dos arquivos de cupons (XML/PDF/Imagem)
            json_content: Conteúdo do arquivo JSON da API

        Returns:
            Tuple[List[dict], List[str]]: (resultados_formatados_para_exibição, mensagens_de_erro)
        """
        # Processar o roteiro de testes para extrair casos de teste
        # NOTE: In a real implementation, we would get the filename from the uploaded file
        # For now, we'll use the file_type parameter passed from the caller
        # The caller (main.py) should pass the file type based on the uploaded file's extension
        roteiro_file_type = roteiro_file_type or 'csv'  # Default to csv if not provided
        casos_teste = self._processar_roteiro(roteiro_content, roteiro_file_type)

        # Processar os cupons fiscais
        cupons_data = self._processar_cupons(cupons_content)

        # Processar o JSON da API
        api_payload = self._processar_json_api(json_content)

        # Lista para armazenar os resultados
        resultados = []
        mensagens_erro = []

        # TODO: Implementar o loop principal de validação:
        # Para cada caso de teste no roteiro:
        # 1. Encontrar o cupom correspondente (baseado em alguma referência)
        # 2. Criar objeto Movimiento a partir dos dados do caso de teste, cupom e JSON
        # 3. Validar o movimento usando o ValidationEngine
        # 4. Formatar o resultado para exibição

        # Por enquanto, retornamos resultados simulados para manter a compatibilidade
        # com a interface atual do main.py
        resultados_simulados = [
            {
                "ID Teste": "TST-001",
                "Cupom Ref": "CPN-2040001",
                "Status": "Aprovado",
                "Descrição": "Todos os campos válidos",
                "Severidade": "Nenhuma"
            },
            {
                "ID Teste": "TST-002",
                "Cupom Ref": "CPN-2040002",
                "Status": "Falha Leve",
                "Descrição": "Desconto total com 3 casas decimais",
                "Severidade": "Leve"
            },
            {
                "ID Teste": "TST-003",
                "Cupom Ref": "CPN-2040003",
                "Status": "Aprovado",
                "Descrição": "Todos os campos válidos",
                "Severidade": "Nenhuma"
            },
            {
                "ID Teste": "TST-004",
                "Cupom Ref": "CPN-2040004",
                "Status": "Falha Mediana",
                "Descrição": "Soma dos detalhes != total",
                "Severidade": "Mediana"
            },
            {
                "ID Teste": "TST-005",
                "Cupom Ref": "CPN-2040005",
                "Status": "Falha Grave",
                "Descrição": "Campo obrigatório 'numero' ausente",
                "Severidade": "Grave"
            }
        ]

        # Para demonstração, vamos usar os casos de teste reais se estiverem disponíveis
        if casos_teste and len(casos_teste) > 0:
            # Converter os primeiros poucos casos de teste para o formato de exibição
            resultados = []
            for i, caso in enumerate(casos_teste[:5]):  # Limitar a 5 para demonstração
                resultados.append({
                    "ID Teste": caso.get("ID Teste", f"TST-{i+1:03d}"),
                    "Cupom Ref": caso.get("Cupom Ref", f"CPN-204000{i+1}"),
                    "Status": "Aprovado" if i % 2 == 0 else "Falha Leve",
                    "Descrição": caso.get("Descrição", "Processado com sucesso"),
                    "Severidade": "Nenhuma" if i % 2 == 0 else "Leve"
                })
        else:
            # Se não houver casos de teste, usar os simulados
            resultados = resultados_simulados

        # Nenhum erro de processamento por enquanto
        mensagens_erro = []

        return resultados, mensagens_erro
    
    def _processar_roteiro(self, roteiro_content: Any, file_type: str = None) -> List[dict]:
        """
        Processa o arquivo de roteiro de testes e extrai os casos de teste.

        Args:
            roteiro_content: Conteúdo do arquivo de roteiro (XLSX/CSV)
            file_type: Tipo do arquivo ('csv' ou 'xlsx') - opcional, será detectado se não fornecido

        Returns:
            List[dict]: Lista de casos de teste extraídos do roteiro
        """
        try:
            # Importar o parser aqui para evitar dependências circulares
            from src.parsers.roteiro_parser import parse_test_script

            # Se o tipo de arquivo não for fornecido, tentar detectar
            if file_type is None:
                # Esta detecção seria feita baseado no nome do arquivo ou conteúdo
                # Por enquanto, vamos assumir que o caller passa o tipo correto
                # Em uma implementação futura, podemos detectar baseado na extensão
                file_type = 'csv'  # default fallback

            # Processar o arquivo usando o parser
            test_cases = parse_test_script(roteiro_content, file_type)

            # TODO: Mapear os casos de teste para o formato interno esperado
            # Por enquanto, retornar diretamente (ajustar conforme necessário)
            return test_cases

        except ImportError:
            logger.error("Não foi possível importar o parser de roteiro")
            return []
        except Exception as e:
            logger.error(f"Erro ao processar roteiro: {e}")
            return []
    
    def _processar_cupons(self, cupons_content: List[Any]) -> List[dict]:
        """
        Processa os arquivos de cupons fiscais e extrai os dados dos cupons.
        
        Args:
            cupons_content: Lista de conteúdos dos arquivos de cupons (XML/PDF/Imagem)
            
        Returns:
            List[dict]: Lista de dados dos cupons extraídos
        """
        # TODO: Implementar parsers para XML, PDF e imagem
        # Por enquanto, retornar lista vazia
        return []
    
    def _processar_json_api(self, json_content: Any) -> dict:
        """
        Processa o arquivo JSON da API e extrai o payload a ser validado.

        Args:
            json_content: Conteúdo do arquivo JSON da API

        Returns:
            dict: Payload extraído do JSON
        """
        try:
            # Importar o parser JSON
            from src.parsers.json_parser import parse_json_payload

            # Garantimos que o conteúdo seja string
            if not isinstance(json_content, str):
                # Se for bytes, decodificamos
                if isinstance(json_content, bytes):
                    json_content = json_content.decode('utf-8')
                else:
                    json_content = str(json_content)

            # Processa o JSON usando nosso parser
            payload = parse_json_payload(json_content)
            return payload
        except Exception as e:
            logger.error(f"Erro ao processar JSON da API: {e}")
            # Em caso de erro, retornamos dicionário vazio para não quebrar o fluxo
            # O erro será tratado posteriormente na validação
            return {}
    
    def _criar_movimiento_desde_dados(
        self, 
        caso_teste: dict, 
        cupom_data: dict, 
        api_payload: dict
    ) -> Movimiento:
        """
        Cria um objeto Movimiento a partir dos dados processados.
        
        Args:
            caso_teste: Dados do caso de teste do roteiro
            cupom_data: Dados do cupom fiscal
            api_payload: Payload da API
            
        Returns:
            Movimiento: Objeto movimento pronto para validação
        """
        # TODO: Implementar criação do objeto Movimiento a partir dos dados
        # Por enquanto, retornar um objeto vazio (isso causará erro, mas é proposital
        # para indicar que este método precisa ser implementado)
        raise NotImplementedError("Método _criar_movimiento_desde_dados precisa ser implementado")
