"""
Motor de validação para movimentos conforme o schema_etapa01.json
Implementa as regras de negócio da Etapa 01 (Sell-out básico)
"""

from typing import List, Tuple
from ..models.models import Movimiento, Detalle, Pago

class ValidationResult:
    """Resultado da validação de um movimento."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.is_valid: bool = True
    
    def add_error(self, message: str):
        """Adiciona um erro de validação."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Adiciona um aviso de validação."""
        self.warnings.append(message)

class ValidationEngine:
    def _tem_exatamente_duas_casas_decimais(self, valor: float) -> bool:
        """Verifica se um valor tem exatamente 2 casas decimais."""
        # Multiplicar por 100 e verificar se é inteiro
        return abs(valor * 100 - round(valor * 100)) < 1e-9

    """Motor responsável por validar movimentos conforme as regras da Etapa 01."""
    
    def validar_movimiento(self, movimiento: Movimiento) -> ValidationResult:
        """
        Valida um movimento conforme as regras da Etapa 01.
        
        Args:
            movimiento: O movimento a ser validado
            
        Returns:
            ValidationResult: Resultado da validação
        """
        result = ValidationResult()
        
        # Validações de campos obrigatórios (já feitas pelo dataclass, mas reforçando)
        if not movimiento.numero or not movimiento.numero.strip():
            result.add_error("Numero do cupom é obrigatório")
        
        if movimiento.total < 0:
            result.add_error("Total do movimento não pode ser negativo")
        
        # Validação de detalhes
        self._validar_detalles(movimiento.detalles, result)
        
        # Validação de pagos
        self._validar_pagos(movimiento.pagos, result)
        
        # Validação de consistência entre total e soma dos detalhes
        self._validar_consistencia_total_detalles(movimiento, result)
        
        # Validação de consistência entre total e soma dos pagos
        self._validar_consistencia_total_pagos(movimiento, result)
        
        # Validação de desconto e recargo
        self._validar_desconto_recargo(movimiento, result)
        
        return result
    
    def _validar_detalles(self, detalles: List[Detalle], result: ValidationResult):
        """Valida a lista de detalhes conforme estrutura necessária."""
        if not detalles:
            result.add_warning("Nenhum detalhe informado")
            return
        
        for i, detalle in enumerate(detalles):
            if not detalle.data:
                result.add_warning(f"Detalhe {i+1} está vazio")
                continue
            
            # Verificar campos obrigatórios conforme documentação da API
            campos_obrigatorios = ["codigoArticulo", "codigoBarras", "descripcionArticulo", "cantidad", "importeUnitario", "importe"]
            campos_faltantes = [campo for campo in campos_obrigatorios if campo not in detalle.data]
            
            if campos_faltantes:
                faltantes_str = ", ".join(campos_faltantes)
                result.add_error(f"Detalhe {i+1} está faltando os campos obrigatórios: {faltantes_str}")
                continue
            
            # Validar formato numérico dos valores monetários (2 casas decimais)
            campos_valor = ["importeUnitario", "importe"]
            for campo in campos_valor:
                if campo in detalle.data and detalle.data[campo] is not None:
                    try:
                        valor = float(detalle.data[campo])
                        if not self._tem_exatamente_duas_casas_decimais(valor):
                            result.add_error(f"Detalhe {i+1}, campo '{campo}' deve ter exatamente 2 casas decimais")
                    except (ValueError, TypeError):
                        result.add_error(f"Detalhe {i+1}, campo '{campo}' deve ser numérico")
    
    def _validar_pagos(self, pagos: List[Pago], result: ValidationResult):
        """Valida a lista de pagos com verificação de estrutura e tipos."""
        if not pagos:
            result.add_error("Pelo menos um pagamento deve ser informado")
            return
        
        for i, pago in enumerate(pagos):
            if not pago.data:
                result.add_warning(f"Pagamento {i+1} está vazio")
                continue
                
            # Verificar que o pagamento seja um dicionário
            if not isinstance(pago.data, dict):
                result.add_warning(f"Pagamento {i+1} não é um objeto válido")
                continue
                
            # Verificar se tem pelo menos algum identificador de pagamento
            campos_identificacao = ['tipo', 'Tipo', 'tipoPagamento', 'formaPagamento', 'bandeira', 'numero', 'autorizacao']
            tem_identificador = any(campo in pago.data for campo in campos_identificacao)
            
            if not tem_identificador:
                result.add_warning(f"Pagamento {i+1} não possui identificador claro de pagamento")
            
            # Verificar se tem valor do pagamento (campo essencial para validação)
            campos_valor = ['valor', 'Valor', 'valorPagamento', 'vl_pagamento', 'amount', 'amountPaid']
            tem_valor = any(campo in pago.data and pago.data[campo] is not None for campo in campos_valor)
            
            if not tem_valor:
                result.add_warning(f"Pagamento {i+1} não possui informações de valor para validação")
            else:
                # Validar que o valor seja numérico e tenha 2 casas decimais (padrão monetário)
                for campo in campos_valor:
                    if campo in pago.data and pago.data[campo] is not None:
                        try:
                            valor = float(pago.data[campo])
                            if not self._tem_exatamente_duas_casas_decimais(valor):
                                result.add_error(f"Pagamento {i+1}, campo '{campo}' deve ter exatamente 2 casas decimais")
                        except (ValueError, TypeError):
                            result.add_error(f"Pagamento {i+1}, campo '{campo}' deve ser numérico")
    
    def _validar_consistencia_total_detalles(self, movimiento: Movimiento, result: ValidationResult):
        """Valida se o total do movimento é consistente com a soma dos detalhes."""
        if not movimiento.detalles:
            return
        
        try:
            total_detalles = 0.0
            detalhes_com_valor = 0
            
            for i, detalle in enumerate(movimiento.detalles):
                # Tentar extrair o valor do item detalhado
                valor_item = None
                data = detalle.data
                
                if isinstance(data, dict):
                    # Tentar vários nomes de campo comuns para valor do item
                    for field in ['subtotal', 'importe', 'valorTotalItem', 'ValorTotalItem', 'valor_item', 'valor', 'value', 'amount', 'Valor']:
                        if field in data and data[field] is not None:
                            try:
                                valor_item = float(data[field])
                                break
                            except (ValueError, TypeError):
                                continue
                    
                    # Se não encontrou valor direto, tentar calcular quantidade * valor unitário
                    if valor_item is None:
                        quantidade = None
                        valor_unitario = None
                        
                        # Tentar extrair quantidade
                        for q_field in ['quantidade', 'Quantidade', 'cantidad', 'qtd']:
                            if q_field in data and data[q_field] is not None:
                                try:
                                    quantidade = float(data[q_field])
                                    break
                                except (ValueError, TypeError):
                                    continue
                        
                        # Tentar extrair valor unitário
                        for vu_field in ['valor_unitario', 'ValorUnitario', 'importeUnitario', 'valor_unitario', 'preco_unitario', 'price']:
                            if vu_field in data and data[vu_field] is not None:
                                try:
                                    valor_unitario = float(data[vu_field])
                                    break
                                except (ValueError, TypeError):
                                    continue
                        
                        if quantidade is not None and valor_unitario is not None:
                            valor_item = quantidade * valor_unitario
                
                if valor_item is not None:
                    total_detalles += valor_item
                    detalhes_com_valor += 1
                else:
                    # Se não conseguiu extrair o valor, adiciona aviso
                    result.add_warning(f"Não foi possível extrair valor do detalhe {i+1}. Verifique a estrutura dos dados.")
            
            # Só fazer a validação se conseguimos extrair valor de pelo menos um detalhe
            if detalhes_com_valor > 0:
                # Calcular o total esperado baseado nos detalhes, descontos e acréscimos
                total_esperado = total_detalles - movimiento.descuento_total + movimiento.recargo_total
                
                # Usar uma tolerância pequena para comparações de ponto flutuante
                tolerancia = 0.01
                diferenca = abs(movimiento.total - total_esperado)
                
                if diferenca > tolerancia:
                    result.add_error(
                        f"Total do movimento ({movimiento.total}) não é consistente com os detalhes. "
                        f"Esperado: {total_detalles:.2f} (detalhes) - {movimiento.descuento_total:.2f} (desconto) + {movimiento.recargo_total:.2f} (acréscimo) = {total_esperado:.2f}. "
                        f"Diferença: {diferenca:.2f}"
                    )
                # Se estiver consistente, não precisa adicionar nada (validação implícita passando)
                
        except Exception as e:
            result.add_warning(f"Erro ao validar consistência total-detalhes: {e}")
    
    def _validar_consistencia_total_pagos(self, movimiento: Movimiento, result: ValidationResult):
        """Valida se o total do movimento é consistente com a soma dos pagos."""
        if not movimiento.pagos:
            return
        
        try:
            total_pagos = 0.0
            pagos_com_valor = 0
            
            for i, pago in enumerate(movimiento.pagos):
                # Tentar extrair o valor do pagamento
                valor_pagamento = None
                data = pago.data
                
                if isinstance(data, dict):
                    # Tentar vários nomes de campo comuns para valor do pagamento
                    for field in ['valor', 'Valor', 'valorPagamento', 'vl_pagamento', 'amount', 'amountPaid', 'pago', 'Pago', 'valor_pago']:
                        if field in data and data[field] is not None:
                            try:
                                valor_pagamento = float(data[field])
                                break
                            except (ValueError, TypeError):
                                continue
                
                if valor_pagamento is not None:
                    total_pagos += valor_pagamento
                    pagos_com_valor += 1
                else:
                    # Se não conseguiu extrair o valor, adiciona aviso
                    result.add_warning(f"Não foi possível extrair valor do pagamento {i+1}. Verifique a estrutura dos dados.")
            
            # Só fazer a validação se conseguimos extrair valor de pelo menos um pagamento
            if pagos_com_valor > 0:
                # Usar uma tolerância pequena para comparações de ponto flutuante
                tolerancia = 0.01
                diferenca = abs(movimiento.total - total_pagos)
                
                if diferenca > tolerancia:
                    result.add_error(
                        f"Total do movimento ({movimiento.total}) não é consistente com os pagos. "
                        f"Soma dos pagos: {total_pagos:.2f}. Diferença: {diferenca:.2f}"
                    )
                # Se estiver consistente, não precisa adicionar nada (validação implícita passando)
                
        except Exception as e:
            result.add_warning(f"Erro ao validar consistência total-pagos: {e}")
    
    def _validar_desconto_recargo(self, movimiento: Movimiento, result: ValidationResult):
        """Valida os campos de desconto e recargo."""
        if movimiento.descuento_total > movimiento.total:
            result.add_error("Desconto total não pode ser maior que o total do movimento")
        
        # Validar que o total líquido (total - desconto + recargo) não seja negativo
        total_liquido = movimiento.total - movimiento.descuento_total + movimiento.recargo_total
        if total_liquido < 0:
            result.add_error("Total líquido (total - desconto + recargo) não pode ser negativo")