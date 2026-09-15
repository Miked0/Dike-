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
        
        # Nota: O schema permite total >= 0, mas na prática, movimentos cancelados podem ter total negativo
        # Vamos permitir total negativo apenas se indicar cancelamento explícito
        if movimiento.total < 0 and not movimiento.cancelacion:
            result.add_error("Total do movimento não pode ser negativo para movimentos não cancelados")
        
        # Validação de detalhes
        self._validar_detalles(movimiento.detalles, result)
        
        # Validação de pagos
        self._validar_pagos(movimiento.pagos, result)
        
        # Validação de consistência entre total bruto dos detalhes e total líquido (considerando descontos/acréscimos)
        self._validar_consistencia_total_detalles(movimiento, result)
        
        # Validação de consistência entre total e soma dos pagos
        self._validar_consistencia_total_pagos(movimiento, result)
        
        # Validação de desconto e recargo
        self._validar_desconto_recargo(movimiento, result)
        
        return result
    
    def _validar_detalles(self, detalles: List[Detalle], result: ValidationResult):
            """Valida a lista de detalhes."""
            if not detalles:
                result.add_warning("Nenhum detalhe informado")
                return
        
            for i, detalle in enumerate(detalles):
                if not detalle.data:
                    result.add_warning(f"Detalhe {i+1} está vazio")
                    continue
                
                # Validar que o detalhe tenha pelo menos alguns campos essenciais
                data = detalle.data
                if not isinstance(data, dict):
                    result.add_warning(f"Detalhe {i+1} não é um objeto válido")
                    continue
                
                # Verificar se tem algum identificador de item ou descrição
                has_identifier = any(key in data for key in [
                    'NumeroItem', 'numeroItem', 'numero_item',
                    'Codigo', 'codigo', 'code',
                    'Descricao', 'descricao', 'description', 'desc'
                ])
            
                if not has_identifier:
                    result.add_warning(f"Detalhe {i+1} não possui identificador ou descrição clara")
            
                # Verificar se tem informações de valor (direto ou por quantidade * unitário)
                has_direct_value = any(key in data for key in [
                    'ValorTotalItem', 'valorTotalItem', 'valor_item',
                    'Valor', 'valor', 'value', 'amount'
                ])
            
                has_quantity_and_unit = (
                    any(key in data for key in ['Quantidade', 'quantidade', 'qtd']) and
                    any(key in data for key in ['ValorUnitario', 'valorUnitario', 'preco_unitario', 'unit_price'])
                )
            
                if not has_direct_value and not has_quantity_and_unit:
                    result.add_warning(f"Detalhe {i+1} não possui informações de valor suficientes para validação")
    
    def _validar_pagos(self, pagos: List[Pago], result: ValidationResult):
            """Valida a lista de pagos."""
            if not pagos:
                result.add_error("Pelo menos um pagamento deve ser informado")
                return
        
            for i, pago in enumerate(pagos):
                if not pago.data:
                    result.add_warning(f"Pagamento {i+1} está vazio")
                    continue
                
                # Validar que o pagamento tenha pelo menos alguns campos essenciais
                data = pago.data
                if not isinstance(data, dict):
                    result.add_warning(f"Pagamento {i+1} não é um objeto válido")
                    continue
                
                # Verificar se tem algum identificador de pagamento ou forma
                has_identifier = any(key in data for key in [
                    'FormaPagamento', 'formaPagamento', 'forma_pagamento',
                    'Tipo', 'tipo', 'type',
                    'Bandeira', 'bandeira', 'flag',
                    'Numero', 'numero', 'number', 'num',
                    'Valor', 'valor', 'value', 'amount'
                ])
            
                if not has_identifier:
                    result.add_warning(f"Pagamento {i+1} não possui identificador claro")
            
                # Verificar se tem informações de valor
                has_value = any(key in data for key in [
                    'Valor', 'valor', 'value', 'amount',
                    'ValorPagamento', 'vl_pagamento', 'valor_pago'
                ])
            
                if not has_value:
                    result.add_warning(f"Pagamento {i+1} não possui informações de valor")
    
    def _validar_consistencia_total_detalles(self, movimiento: Movimiento, result: ValidationResult):
        """
        Valida se o total do movimento é consistente com a soma dos detalhes.
        A relação correta é:
        total_liquido = soma_dos_detalhes - descontos + acréscimos
        Onde total_liquido é o campo 'total' do movimento.
        """
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
                    for field in ['valorTotalItem', 'ValorTotalItem', 'valor_item', 'valor', 'value', 'amount', 'Valor']:
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
                        for q_field in ['quantidade', 'Quantidade', 'QuantidadeItem', 'qtd']:
                            if q_field in data and data[q_field] is not None:
                                try:
                                    quantidade = float(data[q_field])
                                    break
                                except (ValueError, TypeError):
                                    continue
                        
                        # Tentar extrair valor unitário
                        for vu_field in ['valorUnitario', 'ValorUnitario', 'valor_unitario', 'preco_unitario', 'price']:
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
        """
        Valida se o total do movimento é consistente com a soma dos pagos.
        O total do movimento (campo 'total') deveria ser igual à soma dos pagos,
        já que representa o valor que efetivamente precisa ser pago/recebido.
        """
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
                    for field in ['valor', 'Valor', 'value', 'amount', 'ValorPagamento', 'vl_pagamento']:
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
                        f"Total do movimento ({movimiento.total}) não é igual à soma dos pagos ({total_pagos:.2f}). "
                        f"Diferença: {diferenca:.2f}"
                    )
                # Se estiver consistente, não precisa adicionar nada (validação implícita passando)
                    
        except Exception as e:
            result.add_warning(f"Erro ao validar consistência total-pagos: {e}")
    
    def _validar_desconto_recargo(self, movimiento: Movimiento, result: ValidationResult):
        """Valida os campos de desconto e recargo com regras aprimoradas."""
        # Validar que descontos e acréscimos não sejam negativos
        if movimiento.descuento_total < 0:
            result.add_error("Desconto total não pode ser negativo")
        
        if movimiento.recargo_total < 0:
            result.add_error("Recargo total não pode ser negativo")
        
        # Validação adicional para descontos: em movimentos normais (não cancelados),
        # o desconto não debería ser maior que o total bruto dos detalhes
        if movimiento.descuento_total > 0 and movimiento.detalles and not movimiento.cancelacion:
            # Estimar o total bruto dos detalhes (sem descontos)
            total_detalles_estimado = 0.0
            detalhes_com_valor = 0
            
            for detalle in movimiento.detalles:
                if isinstance(detalle.data, dict):
                    # Tentar obter valor total do item
                    for field in ['valorTotalItem', 'ValorTotalItem', 'valor', 'value']:
                        if field in detalle.data and detalle.data[field] is not None:
                            try:
                                total_detalles_estimado += float(detalle.data[field])
                                detalhes_com_valor += 1
                                break
                            except (ValueError, TypeError):
                                continue
            
            # Se conseguimos estimar o total dos detalhes e temos detalhes com valor,
            # verificar se o desconto faz sentido
            if total_detalles_estimado > 0 and detalhes_com_valor > 0:
                # O desconto não deveria ser maior que o total estimado dos detalhes
                # (exceto em casos de cupons cancelados onde o total pode ser negativo)
                if movimiento.descuento_total > total_detalles_estimado:
                    result.add_warning(
                        f"Desconto total ({movimiento.descuento_total}) parece ser maior que o "
                        f"total estimado dos detalhes ({total_detalles_estimado:.2f}). "
                        f"Isso pode indicar um erro nos dados, exceto se o movimento estiver cancelado."
                    )