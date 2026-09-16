import unittest
from src.models.models import Movimiento, Detalle, Pago
from src.validators.validation_engine import ValidationEngine
from datetime import datetime, timezone

class TestValidationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ValidationEngine()

    def test_validar_movimiento_valido(self):
        """Teste de validação de um movimento válido."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            100.0,
            False,
            [
                Detalle(data={"importe": 50.00, "codigoArticulo": "001", "codigoBarras": "123", "descripcionArticulo": "Produto", "cantidad": 2, "importeUnitario": 25.00}),
                Detalle(data={"importe": 50.00, "codigoArticulo": "002", "codigoBarras": "456", "descripcionArticulo": "Produto2", "cantidad": 1, "importeUnitario": 50.00})
            ],
            [
                Pago(data={"valor": 50.00, "tipo": "Dinheiro"}),
                Pago(data={"valor": 50.00, "tipo": "Cartão"})
            ],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        # Should be valid (no errors)
        self.assertTrue(result.is_valid, f"Expected valid movement, got errors: {result.errors}")
        # May have warnings but no errors

    def test_validar_movimento_total_negativo(self):
        """Teste de validação de movimento com total negativo (deve ser inválido)."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            -10.0,
            False,
            [],
            [],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        self.assertFalse(result.is_valid)
        self.assertIn("Total do movimento não pode ser negativo", result.errors)

    def test_validar_detalles_vazio(self):
        """Teste de validação de detalhes vazios."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            100.0,
            False,
            [],   # detalhes vazios
            [Pago(data={"valor": 100.00, "tipo": "Dinheiro"})],  # um pagamento válido
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        self.assertTrue(result.is_valid)  # Detalhes vazios são warning, não erro
        self.assertIn("Nenhum detalhe informado", result.warnings)

    def test_validar_detalles_campos_faltantes(self):
        """Teste de validação de detalhes com campos obrigatórios faltando."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            50.0,
            False,
            [
                Detalle(data={"codigoArticulo": "001"})  # Faltando varios campos
            ],
            [],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("faltando os campos obrigatórios" in err for err in result.errors))

    def test_validar_detalles_valor_decimais_invalido(self):
        """Teste de validação de detalhes com valor que não tem exatamente 2 casas decimais."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            33.33,
            False,
            [
                Detalle(data={"codigoArticulo": "001", "codigoBarras": "123456789", "descripcionArticulo": "Produto Teste", "cantidad": 1, "importeUnitario": 33.333, "importe": 33.333})
            ],
            [],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("deve ter exatamente 2 casas decimais" in err for err in result.errors))

    def test_validar_pagos_vazio(self):
        """Teste de validação de pagos vazios (deve ser erro)."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            50.0,
            False,
            [],
            [],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        self.assertFalse(result.is_valid)
        self.assertIn("Pelo menos um pagamento deve ser informado", result.errors)

    def test_validar_pagos_estrutura_invalida(self):
        """Teste de validação de pagos com estrutura inválida (não dict)."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        class FakePago:
            data = "não é dict"

        movimiento = Movimiento(
            fecha,
            "123456",
            50.0,
            False,
            [],
            [FakePago()],  # Pagamento com data não dict
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        # Should have warning about payment not being valid object
        self.assertTrue(any("não é um objeto válido" in warn for warn in result.warnings))

    def test_validar_pagos_sem_identificador(self):
        """Teste de validação de pagos sem identificador claro."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            50.0,
            False,
            [],
            [
                Pago(data={"outro_campo": "valor"})  # Sem identificador de pagamento
            ],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        # Should have warning about missing identifier
        self.assertTrue(any("não possui identificador claro de pagamento" in warn for warn in result.warnings))

    def test_validar_pagos_sem_valor(self):
        """Teste de validação de pagos sem informações de valor."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            50.0,
            False,
            [],
            [
                Pago(data={"tipo": "Dinheiro"})  # Tem identificador mas sem valor
            ],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        # Should have warning about missing valor information
        self.assertTrue(any("não possui informações de valor para validação" in warn for warn in result.warnings))

    def test_validar_pagos_valor_decimais_invalido(self):
        """Teste de validação de pagos com valor que não tem exatamente 2 casas decimais."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            33.33,
            False,
            [],
            [
                Pago(data={"valor": 33.333, "tipo": "Dinheiro"})
            ],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("deve ter exatamente 2 casas decimais" in err for err in result.errors))

    def test_validar_consistencia_total_detalles_consistente(self):
        """Teste de validação de consistência total-detalhes consistente."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            100.0,
            False,
            [
                Detalle(data={"importe": 50.00, "codigoArticulo": "001", "codigoBarras": "123", "descripcionArticulo": "Produto", "cantidad": 2, "importeUnitario": 25.00}),
                Detalle(data={"importe": 50.00, "codigoArticulo": "002", "codigoBarras": "456", "descripcionArticulo": "Produto2", "cantidad": 1, "importeUnitario": 50.00})
            ],
            [
                Pago(data={"valor": 100.00, "tipo": "Dinheiro"})  # Adicionado pagamento para satisfazer validação
            ],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        # Should be valid (consistent)
        self.assertTrue(result.is_valid, f"Expected valid movement, got errors: {result.errors}")

    def test_validar_consistencia_total_detalles_inconsistente(self):
        """Teste de validação de consistência total-detalhes inconsistente."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            100.0,
            False,
            [
                Detalle(data={"importe": 30.00, "codigoArticulo": "001", "codigoBarras": "123", "descripcionArticulo": "Produto", "cantidad": 2, "importeUnitario": 15.00}),
                Detalle(data={"importe": 30.00, "codigoArticulo": "002", "codigoBarras": "456", "descripcionArticulo": "Produto2", "cantidad": 1, "importeUnitario": 30.00})
            ],
            [
                Pago(data={"valor": 100.00, "tipo": "Dinheiro"})  # Adicionado pagamento para satisfazer validação
            ],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        # Should be invalid due to inconsistency
        self.assertFalse(result.is_valid)
        self.assertTrue(any("não é consistente com os detalhes" in err for err in result.errors))

    def test_validar_consistencia_total_pagos_consistente(self):
        """Teste de validação de consistência total-pagos consistente."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            100.0,
            False,
            [],
            [
                Pago(data={"valor": 50.00, "tipo": "Dinheiro"}),
                Pago(data={"valor": 50.00, "tipo": "Cartão"})
            ],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        # Should be valid (consistent)
        self.assertTrue(result.is_valid, f"Expected valid movement, got errors: {result.errors}")

    def test_validar_consistencia_total_pagos_inconsistente(self):
        """Teste de validação de consistência total-pagos inconsistente."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            100.0,
            False,
            [],
            [
                Pago(data={"valor": 30.00, "tipo": "Dinheiro"}),
                Pago(data={"valor": 30.00, "tipo": "Cartão"})
            ],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        # Should be invalid due to inconsistency
        self.assertFalse(result.is_valid)
        self.assertTrue(any("não é consistente com os pagos" in err for err in result.errors))

    def test_validar_desconto_recargo_desconto_maior_total(self):
        """Teste de validação de desconto maior que o total."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            50.0,
            False,
            [],
            [],
            60.0,  # Maior que o total
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        self.assertFalse(result.is_valid)
        self.assertIn("Desconto total não pode ser maior que o total do movimento", result.errors)

    def test_validar_desconto_recargo_total_liquido_negativo(self):
        """Teste de validação de total líquido negativo."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            10.0,
            False,
            [],
            [],
            20.0,  # Desconto de 20
            5.0,   # Acréscimo de 5
            "986",
            1.0
            # Total líquido = 10 - 20 + 5 = -5 (negativo)
        )
        result = self.engine.validar_movimiento(movimiento)
        self.assertFalse(result.is_valid)
        self.assertIn("Total líquido (total - desconto + recargo) não pode ser negativo", result.errors)

    def test_validar_movimento_cancelado_total_negativo(self):
        """Teste de validação de movimento cancelado com total negativo (deve ser permitido)."""
        fecha = datetime(2026, 9, 15, 10, 30, 0, tzinfo=timezone.utc)
        movimiento = Movimiento(
            fecha,
            "123456",
            -50.0,  # Total negativo para movimento cancelado
            True,   # Indicando que é cancelado
            [],
            [],
            0.0,
            0.0,
            "986",
            1.0
        )
        result = self.engine.validar_movimiento(movimiento)
        # Para movimentos cancelados, total negativo deve ser permitido
        # Vamos verificar se nossa validação permite isso
        # Nota: Nossa implementação atual não tem tratamento especial para cancelados
        # Este teste serve para documentar o comportamento atual
        # Se quisermos permitir total negativo para cancelados, precisaremos modificar a validação
        self.assertFalse(result.is_valid)  # Atualmente ainda bloqueia
        self.assertIn("Total do movimento não pode ser negativo", result.errors)

if __name__ == '__main__':
    unittest.main()