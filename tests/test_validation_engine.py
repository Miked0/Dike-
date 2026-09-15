import unittest
from src.validators.validation_engine import ValidationEngine, ValidationResult
from src.models.models import Movimiento, Detalle, Pago
from datetime import datetime

class TestValidationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ValidationEngine()

    def test_validar_movimiento_valido(self):
        """Test validation of a valid movement"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=100.50,
            cancelacion=False,
            detalles=[
                Detalle(data={"NumeroItem": "1", "Descricao": "Produto A", "ValorTotalItem": 50.25}),
                Detalle(data={"NumeroItem": "2", "Descricao": "Produto B", "ValorTotalItem": 50.25})
            ],
            pagos=[
                Pago(data={"Tipo": "Dinheiro", "Valor": 100.50})
            ],
            descuento_total=0.0,
            recargo_total=0.0
        )
        
        result = self.engine.validar_movimiento(movimiento)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        # May have warnings about empty details/pagos if they don't have enough info, but should be valid

    def test_validar_movimiento_numero_obrigatorio(self):
        """Test that numero is required"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="",  # Empty numero
            total=100.50,
            cancelacion=False,
            detalles=[],
            pagos=[],
            descuento_total=0.0,
            recargo_total=0.0
        )
        
        result = self.engine.validar_movimiento(movimiento)
        
        self.assertFalse(result.is_valid)
        self.assertIn("Numero do cupom é obrigatório", result.errors)

    def test_validar_movimiento_total_negativo_nao_cancelado(self):
        """Test that negative total is invalid for non-cancelled movements"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=-50.00,  # Negative total
            cancelacion=False,  # Not cancelled
            detalles=[],
            pagos=[],
            descuento_total=0.0,
            recargo_total=0.0
        )
        
        result = self.engine.validar_movimiento(movimiento)
        
        self.assertFalse(result.is_valid)
        self.assertIn("Total do movimento não pode ser negativo para movimentos não cancelados", result.errors)

    def test_validar_movimiento_total_negativo_cancelado_valido(self):
        """Test that negative total is valid for cancelled movements"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=-50.00,  # Negative total
            cancelacion=True,  # Cancelled
            detalles=[],
            pagos=[],
            descuento_total=0.0,
            recargo_total=0.0
        )
        
        result = self.engine.validar_movimiento(movimiento)
        
        # Should be valid (no error about negative total for cancelled movements)
        # May have other warnings/errors but not the negative total one
        negative_total_errors = [err for err in result.errors if "Total do movimento não pode ser negativo" in err]
        self.assertEqual(len(negative_total_errors), 0)

    def test_validar_detalles_vazio_warning(self):
        """Test that empty detalles generates warning"""
        result = ValidationResult()
        self.engine._validar_detalles([], result)
        
        self.assertTrue(len(result.warnings) > 0)
        self.assertIn("Nenhum detalhe informado", result.warnings)

    def test_validar_detalles_objeto_invalido_warning(self):
        """Test that invalid detail object generates warning"""
        result = ValidationResult()
        detalle = Detalle(data="not a dict")  # Invalid data type
        self.engine._validar_detalles([detalle], result)
        
        self.assertTrue(len(result.warnings) > 0)
        self.assertIn("não é um objeto válido", result.warnings[0])

    def test_validar_detalles_sem_identificador_warning(self):
        """Test that detail without identifier generates warning"""
        result = ValidationResult()
        detalle = Detalle(data={"QualquerCoisa": "valor"})  # No identifier fields
        self.engine._validar_detalles([detalle], result)
        
        self.assertTrue(len(result.warnings) > 0)
        self.assertIn("não possui identificador ou descrição clara", result.warnings[0])

    def test_validar_detalles_sem_valor_suficiente_warning(self):
        """Test that detail without sufficient value info generates warning"""
        result = ValidationResult()
        # Detail with identifier but no value information
        detalle = Detalle(data={"NumeroItem": "1", "Descricao": "Produto"})  # Has ID but no value
        self.engine._validar_detalles([detalle], result)
        
        self.assertTrue(len(result.warnings) > 0)
        self.assertIn("não possui informações de valor suficientes", result.warnings[0])

    def test_validar_detalles_com_valor_direto_valido(self):
        """Test that detail with direct value is accepted"""
        result = ValidationResult()
        detalle = Detalle(data={"NumeroItem": "1", "ValorTotalItem": 50.0})  # Has direct value
        self.engine._validar_detalles([detalle], result)
        
        # Should not generate warnings about value
        value_warnings = [w for w in result.warnings if "informações de valor suficientes" in w]
        self.assertEqual(len(value_warnings), 0)

    def test_validar_detalles_com_quantidade_e_unitario_valido(self):
        """Test that detail with quantity and unit price is accepted"""
        result = ValidationResult()
        detalle = Detalle(data={"NumeroItem": "1", "Quantidade": 2, "ValorUnitario": 25.0})  # Has qty and unit price
        self.engine._validar_detalles([detalle], result)
        
        # Should not generate warnings about value
        value_warnings = [w for w in result.warnings if "informações de valor suficientes" in w]
        self.assertEqual(len(value_warnings), 0)

    def test_validar_pagos_vazio_error(self):
        """Test that empty pagos generates error"""
        result = ValidationResult()
        self.engine._validar_pagos([], result)
        
        self.assertFalse(result.is_valid)
        self.assertIn("Pelo menos um pagamento deve ser informado", result.errors)

    def test_validar_pagos_objeto_invalido_warning(self):
        """Test that invalid payment object generates warning"""
        result = ValidationResult()
        pago = Pago(data="not a dict")  # Invalid data type
        self.engine._validar_pagos([pago], result)
        
        self.assertTrue(len(result.warnings) > 0)
        self.assertIn("não é um objeto válido", result.warnings[0])

    def test_validar_pagos_sem_identificador_warning(self):
        """Test that payment without identifier generates warning"""
        result = ValidationResult()
        pago = Pago(data={"QualquerCoisa": "valor"})  # No identifier fields
        self.engine._validar_pagos([pago], result)
        
        self.assertTrue(len(result.warnings) > 0)
        self.assertIn("não possui identificador claro", result.warnings[0])

    def test_validar_pagos_sem_valor_warning(self):
        """Test that payment without value generates warning"""
        result = ValidationResult()
        pago = Pago(data={"Tipo": "Dinheiro"})  # Has type but no value
        self.engine._validar_pagos([pago], result)
        
        self.assertTrue(len(result.warnings) > 0)
        self.assertIn("não possui informações de valor", result.warnings[0])

    def test_validar_pagos_com_valor_valido(self):
        """Test that payment with value is accepted"""
        result = ValidationResult()
        pago = Pago(data={"Tipo": "Dinheiro", "Valor": 100.0})  # Has value
        self.engine._validar_pagos([pago], result)
        
        # Should not generate warnings about value
        value_warnings = [w for w in result.warnings if "informações de valor" in w]
        self.assertEqual(len(value_warnings), 0)

    def test_validar_consistencia_total_detalles_valido(self):
        """Test that consistent total-details validation passes"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=100.50,
            cancelacion=False,
            detalles=[
                Detalle(data={"NumeroItem": "1", "ValorTotalItem": 50.25}),
                Detalle(data={"NumeroItem": "2", "ValorTotalItem": 50.25})
            ],
            pagos=[],
            descuento_total=0.0,
            recargo_total=0.0
        )
        
        result = ValidationResult()
        self.engine._validar_consistencia_total_detalles(movimiento, result)
        
        # Should be consistent: 50.25 + 50.25 = 100.50 matches total
        consistency_errors = [err for err in result.errors if "Total do movimento" in err and "detalles" in err]
        self.assertEqual(len(consistency_errors), 0)

    def test_validar_consistencia_total_detalles_invalido(self):
        """Test that inconsistent total-details validation fails"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=100.0,  # Incorrect total
            cancelacion=False,
            detalles=[
                Detalle(data={"NumeroItem": "1", "ValorTotalItem": 50.25}),
                Detalle(data={"NumeroItem": "2", "ValorTotalItem": 50.25})
            ],
            pagos=[],
            descuento_total=0.0,
            recargo_total=0.0
        )
        
        result = ValidationResult()
        self.engine._validar_consistencia_total_detalles(movimiento, result)
        
        # Should be inconsistent: 50.25 + 50.25 = 100.5 != 100.0 total
        consistency_errors = [err for err in result.errors if "Total do movimento" in err and "detalhes" in err]
        self.assertEqual(len(consistency_errors), 1)
        self.assertIn("100.0", consistency_errors[0])
        self.assertIn("100.5", consistency_errors[0])

    def test_validar_consistencia_total_detalles_com_desconto(self):
        """Test consistency validation with discount"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=95.0,  # 100.5 - 5.5 discount
            cancelacion=False,
            detalles=[
                Detalle(data={"NumeroItem": "1", "ValorTotalItem": 50.25}),
                Detalle(data={"NumeroItem": "2", "ValorTotalItem": 50.25})
            ],
            pagos=[],
            descuento_total=5.5,  # Discount
            recargo_total=0.0
        )
        
        result = ValidationResult()
        self.engine._validar_consistencia_total_detalles(movimiento, result)
        
        # Should be consistent: (50.25 + 50.25) - 5.5 = 95.0 matches total
        consistency_errors = [err for err in result.errors if "Total do movimento" in err and "detalles" in err]
        self.assertEqual(len(consistency_errors), 0)

    def test_validar_consistencia_total_detalles_com_acrescimo(self):
        """Test consistency validation with surcharge"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=105.5,  # 100.5 + 5.0 surcharge
            cancelacion=False,
            detalles=[
                Detalle(data={"NumeroItem": "1", "ValorTotalItem": 50.25}),
                Detalle(data={"NumeroItem": "2", "ValorTotalItem": 50.25})
            ],
            pagos=[],
            descuento_total=0.0,
            recargo_total=5.0  # Surcharge
        )
        
        result = ValidationResult()
        self.engine._validar_consistencia_total_detalles(movimiento, result)
        
        # Should be consistent: (50.25 + 50.25) + 5.0 = 105.5 matches total
        consistency_errors = [err for err in result.errors if "Total do movimento" in err and "detalles" in err]
        self.assertEqual(len(consistency_errors), 0)

    def test_validar_consistencia_total_pagos_valido(self):
        """Test that consistent total-pagos validation passes"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=100.5,
            cancelacion=False,
            detalles=[],
            pagos=[
                Pago(data={"Tipo": "Dinheiro", "Valor": 50.25}),
                Pago(data={"Tipo": "Cartão", "Valor": 50.25})
            ],
            descuento_total=0.0,
            recargo_total=0.0
        )
        
        result = ValidationResult()
        self.engine._validar_consistencia_total_pagos(movimiento, result)
        
        # Should be consistent: 50.25 + 50.25 = 100.5 matches total
        consistency_errors = [err for err in result.errors if "Total do movimento" in err and "pagos" in err]
        self.assertEqual(len(consistency_errors), 0)

    def test_validar_consistencia_total_pagos_invalido(self):
        """Test that inconsistent total-pagos validation fails"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=100.0,  # Incorrect total
            cancelacion=False,
            detalles=[],
            pagos=[
                Pago(data={"Tipo": "Dinheiro", "Valor": 50.25}),
                Pago(data={"Tipo": "Cartão", "Valor": 50.25})
            ],
            descuento_total=0.0,
            recargo_total=0.0
        )
        
        result = ValidationResult()
        self.engine._validar_consistencia_total_pagos(movimiento, result)
        
        # Should be inconsistent: 50.25 + 50.25 = 100.5 != 100.0 total
        consistency_errors = [err for err in result.errors if "Total do movimento" in err and "pagos" in err]
        self.assertEqual(len(consistency_errors), 1)
        self.assertIn("100.0", consistency_errors[0])
        self.assertIn("100.5", consistency_errors[0])

    def test_validar_desconto_recargo_negativo_error(self):
            """Test that negative discount or surcharge generates error"""
            # Test negative discount - should raise ValueError on Movimiento construction
            with self.assertRaises(ValueError) as context:
                Movimiento(
                    fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
                    numero="2040001",
                    total=100.0,
                    cancelacion=False,
                    detalles=[],
                    pagos=[],
                    descuento_total=-5.0,  # Negative discount
                    recargo_total=0.0
                )
            self.assertIn("Desconto total não pode ser negativo", str(context.exception))

            # Test negative surcharge - should raise ValueError on Movimiento construction
            with self.assertRaises(ValueError) as context:
                Movimiento(
                    fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
                    numero="2040001",
                    total=100.0,
                    cancelacion=False,
                    detalles=[],
                    pagos=[],
                    descuento_total=0.0,
                    recargo_total=-3.0  # Negative surcharge
                )
            self.assertIn("Recargo total não pode ser negativo", str(context.exception))

    def test_validar_desconto_maior_que_detalhes_warning(self):
        """Test that discount larger than details total generates warning"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=50.0,
            cancelacion=False,
            detalles=[
                Detalle(data={"NumeroItem": "1", "ValorTotalItem": 30.0}),
                Detalle(data={"NumeroItem": "2", "ValorTotalItem": 20.0})
                # Total details = 50.0
            ],
            pagos=[],
            descuento_total=60.0,  # Discount larger than details total
            recargo_total=0.0
        )
        
        result = self.engine.validar_movimiento(movimiento)
        
        # Should generate warning about discount being too large
        discount_warnings = [w for w in result.warnings if "Desconto total" in w and "maior que o total estimado" in w]
        self.assertEqual(len(discount_warnings), 1)

    def test_validar_desconto_maior_que_detalhes_cancelado_sem_warning(self):
        """Test that cancelled movement with large discount doesn't generate warning"""
        movimiento = Movimiento(
            fecha=datetime.fromisoformat("2026-09-15T14:30:00-03:00"),
            numero="2040001",
            total=-10.0,  # Negative total allowed for cancelled
            cancelacion=True,  # Cancelled
            detalles=[
                Detalle(data={"NumeroItem": "1", "ValorTotalItem": 30.0}),
                Detalle(data={"NumeroItem": "2", "ValorTotalItem": 20.0})
                # Total details = 50.0
            ],
            pagos=[],
            descuento_total=100.0,  # Large discount
            recargo_total=0.0
        )
        
        result = self.engine.validar_movimiento(movimiento)
        
        # Should NOT generate warning about discount being too large for cancelled movements
        discount_warnings = [w for w in result.warnings if "Desconto total" in w and "maior que o total estimado" in w]
        self.assertEqual(len(discount_warnings), 0)

if __name__ == '__main__':
    unittest.main()