"""Testes unitários para o serviço de validação"""

import pytest
from datetime import datetime
from src.services.validation_service import ValidationService
from src.models.models import Movimiento, Detalle, Pago


class TestValidationService:
    """Testes para o ValidationService"""
    
    def setup_method(self):
        """Configuração antes de cada teste"""
        self.service = ValidationService()
    
    def test_criar_movimiento_desde_dados_basico(self):
        """Teste básico de criação de objeto Movimiento"""
        # Dados de teste
        caso_teste = {
            "ID Teste": "TST-001",
            "Descrição": "Teste básico",
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",
            "total": "100.50",
            "cancelado": "false"
        }
        
        cupom_data = {
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",
            "valor": "100.50",
            "cancelado": "false"
        }
        
        api_payload = {
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",
            "total": 100.50,
            "cancelacion": False,
            "detalles": [
                {"descricao": "Produto 1", "quantidade": 2, "valor_unitario": 25.00, "subtotal": 50.00},
                {"descricao": "Produto 2", "quantidade": 1, "valor_unitario": 0.50, "subtotal": 0.50}
            ],
            "pagos": [
                {"tipo": "Dinheiro", "valor": 50.00},
                {"tipo": "Cartão", "valor": 50.50}
            ],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }
        
        # Executar
        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
        
        # Verificar
        assert isinstance(movimiento, Movimiento)
        assert movimiento.fecha == datetime(2026, 9, 15, 10, 30, 0, tzinfo=datetime.now().astimezone().tzinfo)
        assert movimiento.numero == "12345"
        assert movimiento.total == 100.50
        assert movimiento.cancelacion == False
        assert len(movimiento.detalles) == 2
        assert len(movimiento.pagos) == 2
        assert movimiento.descuento_total == 0.0
        assert movimiento.recargo_total == 0.0
        assert movimiento.codigo_moneda == "986"
        assert movimiento.cotizacion == 1.0
        
        # Verificar que os detalhes e pagos foram encapsulados corretamente
        assert isinstance(movimiento.detalles[0], Detalle)
        assert isinstance(movimiento.pagos[0], Pago)
        assert movimiento.detalles[0].data["descricao"] == "Produto 1"
        assert movimiento.pagos[0].data["tipo"] == "Dinheiro"
    
    def test_criar_movimiento_desde_dados_prioridade_fontes(self):
        """Teste de prioridade de fontes: JSON > Cupom > Roteiro"""
        # Dados com conflitos intencionais para testar prioridade
        caso_teste = {  # Roteiro (prioridade mais baixa)
            "fecha": "2026-09-14T10:30:00-03:00",  # Data diferente
            "numero": "99999",  # Número diferente
            "total": "50.00",  # Total diferente
            "cancelado": "true"  # Status diferente
        }
        
        cupom_data = {  # Cupom (prioridade média)
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "11111",  # Número diferente
            "valor": "75.00",  # Total diferente
            "cancelado": "false"  # Status diferente
        }
        
        api_payload = {  # JSON (prioridade mais alta)
            "fecha": "2026-09-15T10:30:00-03:00",  # Deve ser usado
            "numero": "12345",  # Deve ser usado
            "total": 100.50,  # Deve ser usado
            "cancelacion": False,  # Deve ser usado
            "detalles": [],
            "pagos": [],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }
        
        # Executar
        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
        
        # Verificar que os valores do JSON (prioridade mais alta) foram usados
        assert movimiento.fecha == datetime(2026, 9, 15, 10, 30, 0, tzinfo=datetime.now().astimezone().tzinfo)
        assert movimiento.numero == "12345"
        assert movimiento.total == 100.50
        assert movimiento.cancelacion == False
        
    def test_criar_movimiento_desde_dados_campos_obrigatorios_faltantes(self):
        """Teste de erro quando campos obrigatórios estão faltando"""
        caso_teste = {}
        cupom_data = {}
        api_payload = {
            "detalles": [],
            "pagos": [],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
            # Faltando: fecha, numero, total, cancelacion
        }
        
        # Executar e verificar que levanta exceção
        with pytest.raises(ValueError, match="Campo obrigatório não encontrado"):
            self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
    
    def test_criar_movimiento_desde_dados_valores_padrao(self):
        """Teste de aplicação de valores padrão para campos opcionais"""
        caso_teste = {
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",
            "total": "100.00",
            "cancelado": "false"
        }
        
        cupom_data = {
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",
            "valor": "100.00",
            "cancelado": "false"
        }
        
        api_payload = {
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",
            "total": 100.00,
            "cancelacion": False
            # Faltando campos opcionais: devem usar valores padrão
        }
        
        # Executar
        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
        
        # Verificar valores padrão
        assert movimiento.descuento_total == 0.0
        assert movimiento.recargo_total == 0.0
        assert movimiento.codigo_moneda == "986"
        assert movimiento.cotizacion == 1.0
        assert len(movimiento.detalles) == 0
        assert len(movimiento.pagos) == 0

    def test_criar_movimiento_desde_dados_tipos_invalidos(self):
        """Teste de tratamento de tipos inválidos"""
        caso_teste = {
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",
            "total": "100.00",
            "cancelado": "false"
        }
        
        cupom_data = {
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",
            "valor": "100.00",
            "cancelado": "false"
        }
        
        # Testar total não numérico
        api_payload = {
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",
            "total": "não é um número",  # Inválido
            "cancelacion": False,
            "detalles": [],
            "pagos": [],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }
        
        with pytest.raises(ValueError, match="Campo 'total' deve ser numérico"):
            self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
        
        # Testar fecha inválida
        api_payload["total"] = 100.00  # Corrigir total
        api_payload["fecha"] = "data inválida"  # Inválido
        
        # Isso deveria fazer fallback para data atual e apenas logar warning, não levantar exceção
        # então não debería levantar ValueError aqui
        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
        # Só verificamos que não levantou exceção - o valor da data será a data atual (aproximada)
        assert isinstance(movimiento, Movimiento)
        
        # Testar campos booleanos inválidos para cancelacion
        api_payload["fecha"] = "2026-09-15T10:30:00-03:00"  # Corrigir fecha
        api_payload["cancelacion"] = "não é booleano"  # Inválido
        
        # Deveria tratar como False (string não vazia que não é "false"/"0"/"no"/"não")
        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
        assert isinstance(movimiento, Movimiento)
        # String não vazia que não é falso explícito -> True
        assert movimiento.cancelacion == True

    def test_ct010_precedencia_json_sobre_cupom(self):
        """Teste para CT-010: Validação de Precedência JSON sobre Cupom"""
        # Dados de teste
        caso_teste = {  # Roteiro (prioridade mais baixa)
            "fecha": "2026-09-14T10:30:00-03:00",  # Data diferente
            "numero": "99999",  # Número diferente
            "total": "50.00",  # Total diferente
            "cancelado": "true"  # Status diferente
        }
        
        cupom_data = {  # Cupom (prioridade média) - dado inconsistente
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "11111",  # Número diferente
            "valor": "90.00",  # Total diferente (inconsistente com JSON)
            "cancelado": "false"
        }
        
        api_payload = {  # JSON (prioridade mais alta) - dado válido que deve prevalecer
            "fecha": "2026-09-15T10:30:00-03:00",  # Deve ser usado
            "numero": "12345",  # Deve ser usado
            "total": 100.50,  # Deve ser usado (válido, deve prevalecer sobre cupom)
            "cancelacion": False,  # Deve ser usado
            "detalles": [],
            "pagos": [],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }
        
        # Executar
        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
        
        # Verificar que os valores do JSON (prioridade mais alta) foram usados
        assert movimiento.fecha == datetime(2026, 9, 15, 10, 30, 0, tzinfo=datetime.now().astimezone().tzinfo)
        assert movimiento.numero == "12345"
        assert movimiento.total == 100.50
        assert movimiento.cancelacion == False
        
    def test_ct011_precedencia_json_sobre_roteiro(self):
        """Teste para CT-011: Validação de Precedência JSON sobre Roteiro"""
        # Dados de teste
        caso_teste = {  # Roteiro (prioridade mais baixa) - dado inconsistente
            "fecha": "2026-09-14T10:30:00-03:00",  # Data diferente
            "numero": "99999",  # Número diferente
            "total": "50.00",  # Total diferente
            "cancelado": "true"  # Status diferente
        }
        
        cupom_data = {  # Cupom (prioridade média) - consistente com JSON
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",  # Consistente com JSON
            "valor": "100.00",  # Consistente com JSON
            "cancelado": "false"  # Consistente com JSON
        }
        
        api_payload = {  # JSON (prioridade mais alta) - dado válido que deve prevalecer
            "fecha": "2026-09-15T10:30:00-03:00",  # Deve ser usado
            "numero": "12345",  # Deve ser usado
            "total": 100.50,  # Deve ser usado (válido, deve prevalecer sobre roteiro)
            "cancelacion": False,  # Deve ser usado
            "detalles": [],
            "pagos": [],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }
        
        # Executar
        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
        
        # Verificar que os valores do JSON (prioridade mais alta) foram usados
        assert movimiento.fecha == datetime(2026, 9, 15, 10, 30, 0, tzinfo=datetime.now().astimezone().tzinfo)
        assert movimiento.numero == "12345"
        assert movimiento.total == 100.50
        assert movimiento.cancelacion == False
        
    def test_ct012_precedencia_cupom_sobre_roteiro(self):
        """Teste para CT-012: Validação de Precedência Cupom sobre Roteiro"""
        # Dados de teste
        caso_teste = {  # Roteiro (prioridade mais baixa) - dado inconsistente
            "fecha": "2026-09-14T10:30:00-03:00",  # Data diferente
            "numero": "99999",  # Número diferente
            "total": "50.00",  # Total diferente
            "cancelado": "true"  # Status diferente
        }
        
        cupom_data = {  # Cupom (prioridade média) - dado válido que deve prevalecer
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",  # Deve ser usado
            "valor": "100.50",  # Deve ser usado (válido, deve prevalecer sobre roteiro)
            "cancelado": "false"  # Deve ser usado
        }
        
        api_payload = {  # JSON (prioridade média, mas consistente com cupom)
            "fecha": "2026-09-15T10:30:00-03:00",  # Consistente com cupom
            "numero": "12345",  # Consistente com cupom
            "total": 100.50,  # Consistente com cupom
            "cancelacion": False,  # Consistente com cupom
            "detalles": [],
            "pagos": [],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }
        
        # Executar
        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
        
        # Verificar que os valores do cupom (prioridade média, mas prevalece sobre roteiro) foram usados
        assert movimiento.fecha == datetime(2026, 9, 15, 10, 30, 0, tzinfo=datetime.now().astimezone().tzinfo)
        assert movimiento.numero == "12345"
        assert movimiento.total == 100.50
        assert movimiento.cancelacion == False
        
    def test_ct013_tres_fontes_inconsistentes(self):
        """Teste para CT-013: Validação com Três Fontes Inconsistentes"""
        # Dados de teste
        caso_teste = {  # Roteiro (prioridade mais baixa) - dado A
            "fecha": "2026-09-14T10:30:00-03:00",  # Dado A: data antiga
            "numero": "99999",  # Dado A: número antigo
            "total": "50.00",  # Dado A: total baixo
            "cancelado": "true"  # Dado A: cancelado
        }
        
        cupom_data = {  # Cupom (prioridade média) - dado B (diferente de A)
            "fecha": "2026-09-15T10:30:00-03:00",  # Dado B: data atual
            "numero": "11111",  # Dado B: número diferente do roteiro
            "valor": "90.00",  # Dado B: total médio (segunda precedência)
            "cancelado": "false"  # Dado B: não cancelado
        }
        
        api_payload = {  # JSON (prioridade mais alta) - dado C (diferente de A e B)
            "fecha": "2026-09-15T10:30:00-03:00",  # Dado C: data atual (mesmo que cupom, mas vamos testar outro campo)
            "numero": "12345",  # Dado C: número diferente de ambos
            "total": 100.50,  # Dado C: total alto (maior precedência, deve prevalecer)
            "cancelacion": False,  # Dado C: não cancelado
            "detalles": [],
            "pagos": [],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }
        
        # Executar
        movimiento = self.service._criar_movimiento_desde_dados(caso_teste, cupom_data, api_payload)
        
        # Verificar que os valores do JSON (prioridade mais alta) foram usados
        assert movimiento.fecha == datetime(2026, 9, 15, 10, 30, 0, tzinfo=datetime.now().astimezone().tzinfo)
        assert movimiento.numero == "12345"
        assert movimiento.total == 100.50
        assert movimiento.cancelacion == False

