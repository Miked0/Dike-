import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from src.services.validation_service import ValidationService
from src.models.models import Movimiento, Detalle, Pago

class TestValidationService(unittest.TestCase):

    def setUp(self):
        self.service = ValidationService()

    def test_criar_movimiento_com_dados_completos_do_json(self):
        """Test creating Movimiento with all data from JSON (highest priority)"""
        caso_teste = {}
        cupom_data = {}
        api_payload = {
            "fecha": "2026-09-15T14:30:00-03:00",
            "numero": "2040001",
            "total": 100.50,
            "cancelacion": False,
            "detalles": [{"descricao": "Produto A", "valor": 50.25}, {"descricao": "Produto B", "valor": 50.25}],
            "pagos": [{"tipo": "Dinheiro", "valor": 100.50}],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }

        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)

        self.assertIsInstance(movimiento, Movimiento)
        self.assertEqual(movimiento.numero, "2040001")
        self.assertEqual(movimiento.total, 100.50)
        self.assertEqual(movimiento.cancelacion, False)
        self.assertEqual(len(movimiento.detalles), 2)
        self.assertEqual(len(movimiento.pagos), 1)
        self.assertEqual(movimiento.descuento_total, 0.0)
        self.assertEqual(movimiento.recargo_total, 0.0)
        self.assertEqual(movimiento.codigo_moneda, "986")
        self.assertEqual(movimiento.cotizacion, 1.0)

    def test_criar_movimiento_com_prioridade_json_sobre_cupom_roteiro(self):
        """Test that JSON data takes priority over cupom and roteiro"""
        caso_teste = {
            "fecha": "2026-09-14T10:00:00-03:00",  # Should be overridden
            "numero": "000000",  # Should be overridden
            "Valor": 999.00  # Should be overridden
        }
        cupom_data = {
            "fecha": "2026-09-13T10:00:00-03:00",  # Should be overridden
            "numero": "111111",  # Should be overridden
            "valor": 888.00  # Should be overridden
        }
        api_payload = {
            "fecha": "2026-09-15T14:30:00-03:00",
            "numero": "2040001",
            "total": 100.50,
            "cancelacion": False,
            "detalles": [],
            "pagos": [],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0
        }

        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)

        self.assertEqual(movimiento.fecha, datetime.fromisoformat("2026-09-15T14:30:00-03:00"))
        self.assertEqual(movimiento.numero, "2040001")
        self.assertEqual(movimiento.total, 100.50)

    def test_criar_movimiento_com_campos_obrigatorios_faltantes(self):
        """Test that missing required fields raise ValueError"""
        caso_teste = {}
        cupom_data = {}
        api_payload = {  # Missing required fields
            "fecha": "2026-09-15T14:30:00-03:00",
            # missing "numero"
            "total": 100.50,
            # missing "detalles"
            # missing "pagos"
            # missing "cancelacion"
        }

        with self.assertRaises(ValueError) as context:
            self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)

        self.assertIn("Campo obrigatório não encontrado", str(context.exception))

    def test_criar_movimiento_com_conversao_de_tipos(self):
        """Test type conversion for various fields"""
        caso_teste = {}
        cupom_data = {}
        api_payload = {
            "fecha": "2026-09-15T14:30:00-03:00",
            "numero": "2040001",
            "total": "100.50",  # String that should convert to float
            "cancelacion": "false",  # String that should convert to boolean False
            "detalles": [],
            "pagos": [],
            "descuentoTotal": "10.25",  # String to float
            "recargoTotal": "5.75",  # String to float
            "codigoMoneda": "986",
            "cotizacion": "1.5"  # String to float
        }

        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)

        self.assertEqual(movimiento.total, 100.50)
        self.assertEqual(movimiento.cancelacion, False)
        self.assertEqual(movimiento.descuento_total, 10.25)
        self.assertEqual(movimiento.recargo_total, 5.75)
        self.assertEqual(movimiento.cotizacion, 1.5)

    def test_criar_movimiento_com_cancelamento_true(self):
        """Test creating Movimiento with cancelacion = True"""
        caso_teste = {}
        cupom_data = {}
        api_payload = {
            "fecha": "2026-09-15T14:30:00-03:00",
            "numero": "2040001",
            "total": -50.00,  # Negative total allowed for cancelled
            "cancelacion": "true",  # String true
            "detalles": [],
            "pagos": [],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0
        }

        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)

        self.assertEqual(movimiento.cancelacion, True)
        self.assertEqual(movimiento.total, -50.00)

    def test_criar_movimiento_com_detalles_e_pagos_vazios(self):
        """Test handling of empty details and payments lists"""
        caso_teste = {}
        cupom_data = {}
        api_payload = {
            "fecha": "2026-09-15T14:30:00-03:00",
            "numero": "2040001",
            "total": 100.00,
            "cancelacion": False,
            "detalles": [],  # Empty list
            "pagos": [],  # Empty list
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0
        }

        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)

        self.assertEqual(len(movimiento.detalles), 0)
        self.assertEqual(len(movimiento.pagos), 0)

    def test_criar_movimiento_com_detalles_e_pagos_none(self):
        """Test handling of None values for details and payments (should become empty lists)"""
        caso_teste = {}
        cupom_data = {}
        api_payload = {
            "fecha": "2026-09-15T14:30:00-03:00",
            "numero": "2040001",
            "total": 100.00,
            "cancelacion": False,
            "detalles": None,  # Should be treated as empty
            "pagos": None,  # Should be treated as empty
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0
        }

        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)

        self.assertEqual(len(movimiento.detalles), 0)
        self.assertEqual(len(movimiento.pagos), 0)

    def test_criar_movimiento_com_valores_padrao(self):
        """Test that default values are applied correctly"""
        caso_teste = {}
        cupom_data = {}
        api_payload = {
            "fecha": "2026-09-15T14:30:00-03:00",
            "numero": "2040001",
            "total": 100.00,
            "cancelacion": False,
            "detalles": [],
            "pagos": [],
            # Missing optional fields that should get defaults
        }

        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)

        self.assertEqual(movimiento.descuento_total, 0.0)  # Default
        self.assertEqual(movimiento.recargo_total, 0.0)  # Default
        self.assertEqual(movimiento.codigo_moneda, "986")  # Default
        self.assertEqual(movimiento.cotizacion, 1.0)  # Default

if __name__ == '__main__':
    unittest.main()