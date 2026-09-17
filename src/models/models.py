from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Detalle:
    """Representa um item detalhe do movimento."""
    # Como o schema não especifica campos específicos para detalles,
    # vamos deixar como um dicionário genérico por enquanto
    # Em uma implementação futura, isso pode ser substituído por campos específicos
    data: dict = field(default_factory=dict)

@dataclass
class Pago:
    """Representa um pagamento do movimento."""
    # Como o schema não especifica campos específicos para pagos,
    # vamos deixar como um dicionário genérico por enquanto
    data: dict = field(default_factory=dict)

@dataclass
class Movimiento:
    """
    Representa um movimento conforme o schema_etapa01.json
    Scanntech API v3.0 Movimentos - Etapa 01
    """
    fecha: datetime
    numero: str
    total: float
    cancelacion: bool
    detalles: List[Detalle] = field(default_factory=list)
    pagos: List[Pago] = field(default_factory=list)
    descuento_total: float = 0.0
    recargo_total: float = 0.0
    codigo_moneda: str = "986"
    cotizacion: float = 1.0
    
    def __post_init__(self):
        """Validações após a inicialização."""
        if self.descuento_total < 0:
            raise ValueError("Desconto total não pode ser negativo")
        if self.recargo_total < 0:
            raise ValueError("Recargo total não pode ser negativo")
        if self.cotizacion <= 0:
            raise ValueError("Cotação deve ser maior que cero")