import pandas as pd
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from ..models.models import Movimiento, Detalle, Pago

logger = logging.getLogger(__name__)

class ValidationService:
    def __init__(self):
        """Inicializa o serviço de validação."""
        pass

    # ===== MÉTODOS EXISTENTES (mantidos para compatibilidade) =====

    def _processar_roteiro(self, content: bytes, file_type: str) -> Dict[str, dict]:
        """
        Processa o roteiro de testes (mantido como estava).
        Implementação simplificada para foco no export_audit.
        """
        try:
            linhas = self._ler_planilha(content, file_type)
            resultado = {}
            for linha in linhas:
                # Assumindo que o roteiro tem coluna para número do cupom
                numero_cupom = linha.get('numero_cupom') or linha.get('Numero Cupom') or linha.get(0)
                if numero_cupom and not (isinstance(numero_cupom, float) and pd.isna(numero_cupom)):
                    try:
                        num_str = str(int(float(numero_cumom))) if float(numero_cupom).is_integer() else str(numero_cupom)
                        resultado[num_str] = linha
                    except:
                        resultado[str(numero_cupom)] = linha
            return resultado
        except Exception as e:
            logger.error(f"Erro ao processar roteiro: {e}")
            return {}

    def _processar_cupons(self, content: List[bytes]) -> Dict[str, dict]:
        """
        Processa os cupons fiscais (mantido como estava).
        Implementação simplificada para foco no export_audit.
        """
        resultado = {}
        for i, cupom_content in enumerate(content):
            try:
                # Para simplificação, estamos usando o índice como chave
                # Em implementação real, extrairíamos o número do cupom do conteúdo XML
                resultado[f"CUPOM_{i:04d}"] = {"conteudo": cupom_content, "indice": i}
            except Exception as e:
                logger.error(f"Erro ao processar cupom {i}: {e}")
                resultado[f"CUPOM_ERRO_{i:04d}"] = {"erro": str(e)}
        return resultado

    

    def _criar_movimiento_desde_dados(self, caso_teste: dict, cupom_data: dict, api_payload: dict) -> Movimiento:
        """
        Cria objeto Movimiento a partir dos dados processados com prioridade: JSON > Cupom > Roteiro.
        
        Args:
            caso_teste: Dados do roteiro de testes
            cupom_data: Dados do cupom fiscal
            api_payload: Dados do JSON do export_audit
        
        Returns:
            Movimiento: Objeto movimentado criado a partir dos dados
        
        Raises:
            ValueError: Se campos obrigatórios estiverem faltando ou tiverem tipos inválidos
        """
        from datetime import datetime
        
        # Função auxiliar para obter valor com prioridade
        def get_valor(chave, default=None):
            # Prioridade: api_payload > cupom_data > caso_teste
            if chave in api_payload and api_payload[chave] is not None:
                return api_payload[chave]
            if chave in cupom_data and cupom_data[chave] is not None:
                return cupom_data[chave]
            if chave in caso_teste and caso_teste[chave] is not None:
                return caso_teste[chave]
            return default
        
        # Extrair campos obrigatórios
        fecha_str = get_valor('fecha')
        numero = get_valor('numero')
        total = get_valor('total')
        cancelacion = get_valor('cancelacion')
        
        # Campos opcionais com padrão
        descuento_total = get_valor('descuentoTotal', 0.0)
        recargo_total = get_valor('recargoTotal', 0.0)
        codigo_moneda = get_valor('codigoMoneda', '986')
        cotizacion = get_valor('cotizacion', 1.0)
        
        # Detalles e pagos (assumimos que vêm principalmente do JSON, mas verificamos todos)
        detalles = get_valor('detalles', [])
        pagos = get_valor('pagos', [])
        
        # Garantir que detalhes e pagos sejam listas
        if not isinstance(detalles, list):
            raise ValueError("Campo 'detalles' deve ser uma lista")
        if not isinstance(pagos, list):
            raise ValueError("Campo 'pagos' deve ser uma lista")
        
        # Validar presença dos campos obrigatórios
        if fecha_str is None:
            raise ValueError("Campo obrigatório não encontrado: fecha")
        if numero is None:
            raise ValueError("Campo obrigatório não encontrado: numero")
        if total is None:
            raise ValueError("Campo obrigatório não encontrado: total")
        if cancelacion is None:
            raise ValueError("Campo obrigatório não encontrado: cancelacion")
        
        # Converter tipos
        try:
            # fecha: esperar string ISO format, tentar parsear
            if isinstance(fecha_str, str):
                # Remover timezone info se presente para simplicidade (ou manter)
                # Vamos usar datetime.fromisoformat que handling timezone
                fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
            else:
                # Se não for string, tenta converter para string e depois parsear
                fecha = datetime.fromisoformat(str(fecha_str).replace('Z', '+00:00'))
        except Exception as e:
            # Se falhar ao parsear a data, usa a data/hora atual como fallback
            # e apenas registra o warning (na implementação real, logaríamos aqui)
            logger.warning(f"Não foi possível parsear a data '{fecha_str}': {e}. Usando data/hora atual como fallback.")
            fecha = datetime.now()
        
        try:
            numero = str(numero)
        except Exception:
            raise ValueError("Campo 'numero' deve ser convertível para string")
        
        try:
            total = float(total)
        except Exception:
            raise ValueError("Campo 'total' deve ser numérico")
        
        # cancelacion pode ser bool ou string
        if isinstance(cancelacion, bool):
            pass
        elif isinstance(cancelacion, str):
            cancelacion_lower = cancelacion.lower()
            cancelacion = cancelacion_lower not in ('false', '0', 'no', 'não')
        else:
            try:
                cancelacion = bool(cancelacion)
            except Exception:
                raise ValueError("Campo 'cancelacion' deve ser booleano")
        
        # Converter valores numéricos opcionais
        try:
            descuento_total = float(descuento_total)
        except Exception:
            raise ValueError("Campo 'descuentoTotal' deve ser numérico")
        try:
            recargo_total = float(recargo_total)
        except Exception:
            raise ValueError("Campo 'recargoTotal' deve ser numérico")
        try:
            codigo_moneda = str(codigo_moneda)
        except Exception:
            raise ValueError("Campo 'codigoMoneda' deve ser string")
        try:
            cotizacion = float(cotizacion)
        except Exception:
            raise ValueError("Campo 'cotizacion' deve ser numérico")
        
        # Criar objetos Detalle e Pago a partir dos dados brutos
        from ..models.models import Detalle, Pago
        detalle_objs = [Detalle(data=d) for d in detalles]
        pago_objs = [Pago(data=p) for p in pagos]
        
        # Criar e retornar o Movimiento
        movimiento = Movimiento(
            fecha=fecha,
            numero=numero,
            total=total,
            cancelacion=cancelacion,
            detalles=detalle_objs,
            pagos=pago_objs,
            descuento_total=descuento_total,
            recargo_total=recargo_total,
            codigo_moneda=codigo_moneda,
            cotizacion=cotizacion
        )
        return movimiento
    def validar_movimiento(self, movimiento: Movimiento) -> 'ValidationResult':
        """
        Valida um movimento conforme as regras da Etapa 01.

        Args:
            movimiento: O movimento a ser validado

        Returns:
            ValidationResult: Resultado da validação
        """
        from src.validators.validation_engine import ValidationEngine, ValidationResult
        validator = ValidationEngine()
        return validator.validar_movimiento(movimiento)

    # ===== NOVOS MÉTODOS PARA EXPORT_AUDIT =====

    def _ler_planilha(self, content: Any, file_type: str = None) -> List[Dict]:
        """
        Lê conteúdo de planilha (XLSX/CSV) e retorna lista de dicionários.

        Args:
            content: Bytes do arquivo
            file_type: Extensão do arquivo ('xlsx', 'csv') - se None, tenta detectar

        Returns:
            Lista de dicionários onde cada dict representa uma linha
        """
        try:
            # Detectar tipo se não fornecido (básico)
            if file_type is None:
                # Em produção, seria melhor detectar pelo conteúdo
                # Por agora, assumimos que o caller passa o tipo correto
                pass

            # Usar pandas para ler o conteúdo - converter bytes para BytesIO
            from io import BytesIO
            if file_type in ['xlsx', 'xls']:
                df = pd.read_excel(BytesIO(content))
            else:  # csv
                df = pd.read_csv(BytesIO(content))

            # Converter para lista de dicionários (tratando NaN como None)
            import numpy as np
            df = df.replace({np.nan: None})
            return df.to_dict('records')

        except Exception as e:
            logger.error(f"Erro ao ler planilha: {e}")
            return []

    def _processar_export_audit(self, content: Any, file_type: str = None) -> Dict[str, dict]:
        """
        Processa o export_audit para extrair JSONs válidos indexados por número do cupom.

        Returns:
            Dict[str, dict]: {numero_cupom: json_payload_validado_e_normalizado}
        """
        try:
            # 1. Ler planilha
            linhas = self._ler_planilha(content, file_type)

            # 2. Extrair dados das colunas H (índice 7 ou nome) e S (índice 18 ou nome)
            resultado = {}
            linhas_processadas = 0
            linhas_com_erro = 0

            for linha in linhas:
                # Suporte flexível por nome de coluna ou índice (tentando nomes primeiro)
                numero_cupom_raw = linha.get('H') or linha.get('Número cupom') or linha.get(7)
                json_request = linha.get('S') or linha.get('Request') or linha.get(18)

                # Pular linhas inválidas (cabeçalhos ou dados corrompidos)
                if numero_cupom_raw is None or (isinstance(numero_cupom_raw, float) and pd.isna(numero_cupom_raw)):
                    linhas_com_erro += 1
                    continue

                if json_request is None or (isinstance(json_request, str) and pd.isna(json_request)):
                    linhas_com_erro += 1
                    continue

                # Converter numero do cupom para string padronizada
                try:
                    num_float = float(numero_cupom_raw)
                    # Se for inteiro (ex: -2036799.0), remove o .0
                    numero_cupom = str(int(num_float)) if num_float.is_integer() else str(num_float)
                except (ValueError, TypeError):
                    linhas_com_erro += 1
                    continue  # Pula se não for convertível para número

                # 3. Validar e parsear o JSON
                try:
                    json_validado = self._validar_json_request(json_request, numero_cupom)
                    if json_validado:
                        resultado[numero_cupom] = json_validado
                        linhas_processadas += 1
                    else:
                        linhas_com_erro += 1
                except Exception as e:
                    logger.debug(f"JSON inválido no export_audit para cupom {numero_cupom}: {e}")
                    linhas_com_erro += 1

            logger.info(f"Export_audit processado: {linhas_processadas} válidas, {linhas_com_erro} com erro")
            return resultado

        except Exception as e:
            logger.error(f"Erro crítico ao processar export_audit: {e}")
            return {}

    def _validar_json_request(self, json_str: str, numero_cupom_esperado: str) -> Optional[dict]:
        """
        Valida JSON do request contra schema e verifica consistência.

        Args:
            json_str: String contendo JSON
            numero_cupom_esperado: Valor esperado da coluna H

        Returns:
            dict: JSON parseado e validado, ou None se inválido
        """
        from src.parsers.json_parser import parse_json_payload, JSONSchemaValidationError, JSONTypeConversionError

        try:
            # Parse e validação básica contra schema_etapa01.json
            payload = parse_json_payload(json_str)

            # Verificar consistência do numero do cupom (se ambos existirem)
            numero_json = payload.get("numero")
            if numero_json is not None and str(numero_json) != numero_cupom_esperado:
                logger.warning(
                    f"Inconsistência de numero: coluna H={numero_cupom_esperado}, JSON={numero_json}"
                )
                # Nota: Não corrigimos automaticamente - apenas logamos para rastreabilidade
                # A decisão de qual valor usar fica na fase de matching (export_audit tem prioridade)

            return payload

        except (JSONSchemaValidationError, JSONTypeConversionError) as e:
            logger.debug(f"Validação do JSON falhou contra schema: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao validar JSON: {e}")
            return None

    # ===== ATUALIZAR O MÉTODO PRINCIPAL =====

    def validar_arquivos(
        self,
        roteiro_content: bytes,
        cupons_content: List[bytes],
        export_audit_content: bytes,  # ALTERADO: agora é export_audit
        roteiro_file_type: str,
        export_audit_file_type: str   # NOVO: parâmetro adicional
    ) -> Tuple[List[Dict], List[str]]:
        """
        Orquestra o processo completo de validação com export_audit como terceiro input.
        Para o v0.03, focamos na validação individual do export_audit.
        O matching tríplice completo será implementado em versões futuras.
        """
        logger.info("Iniciando validação de arquivos com export_audit como terceiro input")

        resultados = []
        erros = []

        try:
            # 1. Processar roteiro de testes (mantido para compatibilidade)
            logger.debug("Processando roteiro de testes...")
            roteiro_data = self._processar_roteiro(roteiro_content, roteiro_file_type)

            # 2. Processar cupons fiscais (mantido para compatibilidade)
            logger.debug("Processando cupons fiscais...")
            cupons_data = self._processar_cupons(cupons_content)

            # 3. NOVO: Processar export_audit (FOCO DO V0.03)
            logger.debug("Processando export_audit...")
            export_audit_data = self._processar_export_audit(export_audit_content, export_audit_file_type)

            logger.info(f"Dados processados - Roteiro: {len(roteiro_data)} entradas, "
                       f"Cupons: {len(cupons_data)} entradas, "
                       f"Export_audit: {len(export_audit_data)} entradas")

            # 4. VALIDAR CADA ENTRADA DO EXPORT_AUDIT INDIVIDUALMENTE
            # (Matching tríplice será implementado em v0.04+)
            for numero_cupom, json_payload in export_audit_data.items():
                try:
                    # Validar que temos os dados mínimos necessários
                    if not json_payload or not isinstance(json_payload, dict):
                        erros.append(f"Cupom {numero_cupom}: Dados do export_audit inválidos")
                        continue

                    # Criar objeto Movimiento diretamente do JSON do export_audit
                    movimiento = Movimiento(
                        fecha=json_payload['fecha'],
                        numero=str(json_payload['numero']),
                        total=float(json_payload['total']),
                        cancelacion=bool(json_payload['cancelacion']),
                        detalles=[Detalle(data=d) for d in json_payload.get('detalles', [])],
                        pagos=[Pago(data=p) for p in json_payload.get('pagos', [])],
                        descuento_total=float(json_payload.get('descuentoTotal', 0.0)),
                        recargo_total=float(json_payload.get('recargoTotal', 0.0)),
                        codigo_moneda=str(json_payload.get('codigoMoneda', '986')),
                        cotizacion=float(json_payload.get('cotizacion', 1.0))
                    )

                    # Validar o movimento usando o engine existente
                    validation_result = self.validar_movimiento(movimiento)

                    # Preparar resultado para exibição na interface
                    status = "Aprovado" if validation_result.is_valid else "Falha Grave"
                    severidade = "Nenhuma"
                    if validation_result.errors:
                        severidade = "Grave"
                    elif validation_result.warnings:
                        severidade = "Mediana"

                    descricao = f"Validação do export_audit - "
                    descricao += f"{len(validation_result.errors)} erro(s), "
                    descricao += f"{len(validation_result.warnings)} aviso(s)"

                    resultado_item = {
                        "ID Teste": f"EA-{numero_cupom}",
                        "Cupom Ref": numero_cupom,
                        "Status": status,
                        "Descrição": descricao,
                        "Severidade": severidade
                    }

                    resultados.append(resultado_item)

                    # Coletar mensagens detalhadas para a seção de erros
                    for error in validation_result.errors:
                        erros.append(f"Cupom {numero_cupom}: {error}")
                    for warning in validation_result.warnings:
                        erros.append(f"Cupom {numero_cupom} (aviso): {warning}")

                except KeyError as e:
                    logger.error(f"Campo obrigatório faltando no JSON do cupom {numero_cupom}: {e}")
                    erros.append(f"Cupom {numero_cupom}: Campo obrigatório faltando no JSON - {str(e)}")
                except Exception as e:
                    logger.error(f"Erro ao processar cupom {numero_cupom} do export_audit: {e}")
                    erros.append(f"Cupom {numero_cupom}: Erro ao processar dados - {str(e)}")

            # Se não houver resultados válidos, adicionar um aviso geral
            if not resultados and export_audit_data:
                resultados.append({
                    "ID Teste": "EA-GERAL",
                    "Cupom Ref": "N/A",
                    "Status": "Impossível Validar",
                    "Descrição": "Nenhum movimento pôde ser criado dos dados do export_audit",
                    "Severidade": "Grave"
                })
                erros.append("Nenhum movimento válido pôde ser criado do export_audit")

        except Exception as e:
            logger.error(f"Erro crítico na validação de arquivos: {e}")
            erros.append(f"Erro crítico no processamento: {str(e)}")

        logger.info(f"Validação concluída: {len(resultados)} resultados, {len(erros)} erros")
        return resultados, erros