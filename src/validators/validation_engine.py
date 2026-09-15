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
        """Valida a lista de detalhes."""
        if not detalles:
            result.add_warning("Nenhum detalhe informado")
            return
            
        for i, detalle in enumerate(detalles):
            if not detalle.data:
                result.add_warning(f"Detalhe {i+1} está vazio")
    
    def _validar_pagos(self, pagos: List[Pago], result: ValidationResult):
        """Valida a lista de pagos."""
        if not pagos:
            result.add_error("Pelo menos um pagamento deve ser informado")
            return
            
        for i, pago in enumerate(pagos):
            if not pago.data:
                result.add_warning(f"Pagamento {i+1} está vazio")
    
    def _validar_consistencia_total_detalles(self, movimiento: Movimiento, result: ValidationResult):
        """
        Valida se o total do movimento é consistente com a soma dos detalhes.
        Nota: Como não temos a estrutura específica dos detalhes, esta validação
        é simplificada e deve ser aprimorada quando a estrutura dos detalhes for conhecida.
        """
        # Esta validação precisará ser implementada conforme a estrutura real dos detalhes
        # Por enquanto, apenas adicionamos um aviso de que esta validação precisa ser implementada
        if movimento.detalles:
            result.add_warning("Validação de consistência total-detalhes precisa ser implementada conforme estrutura dos detalhes")
    
    def _validar_consistencia_total_pagos(self, movimiento: Movimiento, result: ValidationResult):
        """
        Valida se o total do movimento é consistente com a soma dos pagos.
        Nota: Como não temos a estrutura específica dos pagos, esta validação
        é simplificada e deve ser aprimorada quando a estrutura dos pagos for conhecida.
        """
        # Esta validação precisará ser implementada conforme a estrutura real dos pagos
        # Por enquanto, apenas adicionamos um aviso de que esta validação precisa ser implementada
        if movimento.pagos:
            result.add_warning("Validação de consistência total-pagos precisa ser implementada conforme estrutura dos pagos")
    
    def _validar_desconto_recargo(self, movimiento: Movimiento, result: ValidationResult):
        """Valida os campos de desconto e recargo."""
        if movimiento.descuento_total > movimiento.total:
            result.add_error("Desconto total não pode ser maior que o total do movimento")
            
        # Validar que o total líquido (total - desconto + recargo) não seja negativo
        total_liquido = movimiento.total - movimiento.descuento_total + movimiento.recargo_total
        if total_liquido < 0:
            result.add_error("Total líquido (total - desconto + recargo) não pode ser negativo")
