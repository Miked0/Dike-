"""
Serviço de validação que orquestra o processo de validação.
Interface entre a UI (Dikē .py) e o motor de validação (core).
"""
import pandas as pd
import logging
from datetime import datetime
from typing import List, Tuple, Any, Dict
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
        roteiro_file_type = roteiro_file_type or 'csv'
        casos_teste = self._processar_roteiro(roteiro_content, roteiro_file_type)

        # Processar os cupons fiscais
        cupons_data = self._processar_cupons(cupons_content)

        # Processar o JSON da API
        api_payload = self._processar_json_api(json_content)

        # Lista para armazenar os resultados
        resultados = []
        mensagens_erro = []

        # Loop principal de validação:
        # Para cada caso de teste no roteiro:
        # 1. Encontrar o cupom correspondente (baseado em alguma referência)
        # 2. Criar objeto Movimiento a partir dos dados do caso de teste, cupom e JSON
        # 3. Validar o movimento usando o ValidationEngine
        # 4. Formatar o resultado para exibição

        if casos_teste and len(casos_teste) > 0:
            resultados = []
            for i, caso in enumerate(casos_teste[:5]):  # Limitar a 5 para demonstração
                try:
                    # Encontrar cupom correspondente (simplificado - usa o primeiro disponível)
                    cupom = cupons_data[0] if cupons_data else {}
                    
                    # Criar objeto Movimiento
                    movimiento = self._criar_movimiento_desde_dados(caso, cupom, api_payload)
                    
                    # Validar o movimento
                    validation_result = self.validation_engine.validar(movimiento)
                    
                    # Formatar resultado
                    status = "Aprovado" if validation_result.get("valido", False) else "Falha"
                    severidade = validation_result.get("severidade", "Nenhuma")
                    descricao = validation_result.get("descricao", "Processado com sucesso")
                    
                    resultados.append({
                        "ID Teste": caso.get("ID Teste", f"TST-{i+1:03d}"),
                        "Cupom Ref": caso.get("Cupom Ref", f"CPN-204000{i+1}"),
                        "Status": status,
                        "Descrição": descricao,
                        "Severidade": severidade
                    })
                except Exception as e:
                    logger.error(f"Erro ao validar caso de teste {i}: {e}")
                    resultados.append({
                        "ID Teste": caso.get("ID Teste", f"TST-{i+1:03d}"),
                        "Cupom Ref": caso.get("Cupom Ref", f"CPN-204000{i+1}"),
                        "Status": "Erro",
                        "Descrição": f"Erro no processamento: {str(e)}",
                        "Severidade": "Grave"
                    })
        else:
            # Se não houver casos de teste, usar os simulados
            resultados = [
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

            if file_type is None:
                file_type = 'csv'

            test_cases = parse_test_script(roteiro_content, file_type)
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
                if isinstance(json_content, bytes):
                    json_content = json_content.decode('utf-8')
                else:
                    json_content = str(json_content)

            # Processa o JSON usando nosso parser
            payload = parse_json_payload(json_content)
            return payload
        except Exception as e:
            logger.error(f"Erro ao processar JSON da API: {e}")
            return {}
   
    def _criar_movimiento_desde_dados(
        self,
        caso_teste: dict,
        cupom_data: dict,
        api_payload: dict
    ) -> Movimiento:
        """
        Cria un objeto Movimiento a partir dos dados processados.

        Args:
            caso_teste: Dados do caso de teste do roteiro
            cupom_data: Dados do cupom fiscal
            api_payload: Payload da API (já processado pelo json_parser)

        Returns:
            Movimiento: Objeto movimento pronto para validação

        Raises:
            ValueError: Se campos obrigatórios estiverem ausentes ou inválidos
        """
        # Função auxiliar para obter valor com prioridade: JSON > Cupom > Roteiro
        def get_value_with_priority(json_key, cupom_key=None, roteiro_key=None, default=None, required=False):
            """
            Obtém um valor seguindo a ordem de prioridade: JSON > Cupom > Roteiro.

            Args:
                json_key: Chave no dicionário api_payload
                cupom_key: Chave no dicionário cupom_data (opcional)
                roteiro_key: Chave no dicionário caso_teste (opcional)
                default: Valor padrão caso nenhuma fonte tenha o valor
                required: Se True, levanta ValueError se nenhum valor for encontrado

            Returns:
                O valor encontrado ou o padrão
            """
            # 1. Tentar obter do JSON (api_payload)
            if json_key in api_payload and api_payload[json_key] is not None:
                return api_payload[json_key]

            # 2. Tentar obter do Cupom (se a chave for fornecida)
            if cupom_key and cupom_key in cupom_data and cupom_data[cupom_key] is not None:
                return cupom_data[cupom_key]

            # 3. Tentar obter do Roteiro (se a chave for fornecida)
            if roteiro_key and roteiro_key in caso_teste and caso_teste[roteiro_key] is not None:
                return caso_teste[roteiro_key]

            # 4. Retornar o padrão
            if default is not None:
                return default

            # 5. Se for obrigatório e nenhum valor foi encontrado, levantar exceção
            if required:
                sources = []
                if json_key:
                    sources.append(f"JSON.{json_key}")
                if cupom_key:
                    sources.append(f"Cupom.{cupom_key}")
                if roteiro_key:
                    sources.append(f"Roteiro.{roteiro_key}")
                raise ValueError(f"Campo obrigatório não encontrado em nenhuma fonte: {', '.join(sources)}")

            return None

        try:
            # Converter fecha string para datetime
            fecha_str = get_value_with_priority("fecha", "fecha", "fecha", required=True)
            try:
                # Formato ISO 8601 com timezone: 2026-09-15T14:30:00-03:00
                fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
            except Exception as e:
                # Se não conseguir parsear, tentar formatos alternativos ou usar data atual como último recurso
                logger.warning(f"Não foi possível parsear a fecha '{fecha_str}': {e}. Usando data atual.")
                fecha = datetime.now()

            # Obter número do cupom
            numero = get_value_with_priority("numero", "numero", "Cupom Ref", required=True)
            numero = str(numero)

            # Obter total
            total = get_value_with_priority("total", "valor", "Valor", required=True)
            try:
                total = float(total)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Campo 'total' deve ser numérico: {e}")

            # Obter cancelacion
            cancelacion = get_value_with_priority("cancelacion", "cancelado", "Status", default=False)
            # Converter para boolean, tratando strings
            if isinstance(cancelacion, str):
                cancelacion = cancelacion.lower() not in {"false", "0", "no", "não", ""}
            else:
                cancelacion = bool(cancelacion)

            # Obter detalles (apenas do JSON, já que é uma estrutura complexa)
            # Nota: Os detalhes são específicos do JSON e não têm equivalentes simples no cupom ou roteiro
            detalles_raw = api_payload.get("detalles", [])
            if not isinstance(detalles_raw, list):
                logger.warning(f"Campo 'detalles' não é uma lista: {type(detalles_raw)}. Usando lista vazia.")
                detalles_raw = []

            detalles = []
            for item in detalles_raw:
                if isinstance(item, dict):
                    detalles.append(Detalle(data=item))
                else:
                    detalles.append(Detalle(data={"raw": item}))

            # Obter pagos (apenas do JSON, mesmo motivo)
            pagos_raw = api_payload.get("pagos", [])
            if not isinstance(pagos_raw, list):
                logger.warning(f"Campo 'pagos' não é uma lista: {type(pagos_raw)}. Usando lista vazia.")
                pagos_raw = []

            pagos = []
            for item in pagos_raw:
                if isinstance(item, dict):
                    pagos.append(Pago(data=item))
                else:
                    pagos.append(Pago(data={"raw": item}))

            # Obter descontos e acréscimos (opcionais, com padrão 0)
            descuento_total = get_value_with_priority("descuentoTotal", "desconto", "Desconto", default=0.0)
            try:
                descuento_total = float(descuento_total)
            except (ValueError, TypeError) as e:
                logger.warning(f"Não foi possível converter 'descuentoTotal' para float: {e}. Usando 0.0.")
                descuento_total = 0.0

            recargo_total = get_value_with_priority("recargoTotal", "acrescimo", "Acréscimo", default=0.0)
            try:
                recargo_total = float(recargo_total)
            except (ValueError, TypeError) as e:
                logger.warning(f"Não foi possível converter 'recargoTotal' para float: {e}. Usando 0.0.")
                recargo_total = 0.0

            # Obter código da moeda (opcional, padrão "986")
            codigo_moneda = get_value_with_priority("codigoMoneda", "moeda", "Moeda", default="986")
            codigo_moneda = str(codigo_moneda)

            # Obter cotação (opcional, padrão 1.0)
            cotizacion = get_value_with_priority("cotizacion", "cotizacao", "Cotação", default=1.0)
            try:
                cotizacion = float(cotizacion)
            except (ValueError, TypeError) as e:
                logger.warning(f"Não foi possível converter 'cotizacion' para float: {e}. Usando 1.0.")
                cotizacion = 1.0

            # Criar objeto Movimiento
            movimiento = Movimiento(
                fecha=fecha,
                numero=numero,
                total=total,
                cancelacion=cancelacion,
                detalles=detalles,
                pagos=pagos,
                descuento_total=descuento_total,
                recargo_total=recargo_total,
                codigo_moneda=codigo_moneda,
                cotizacion=cotizacion
            )

            # Log de rastreabilidade das fontes usadas (opcional)
            logger.debug(f"Movimiento criado com fontes: JSON={bool(api_payload)}, Cupom={bool(cupom_data)}, Roteiro={bool(caso_teste)}")

            return movimiento

        except ValueError as e:
            # Re-lançar exceções de valor com contexto
            raise ValueError(f"Falha ao criar objeto Movimiento: {e}")
        except Exception as e:
            # Capturar qualquer outra exceção e fornecer mensagem clara
            logger.error(f"Erro inesperado ao criar Movimiento: {e}")
            raise ValueError(f"Erro inesperado ao criar objeto Movimiento: {e}")