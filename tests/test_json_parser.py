"""Testes unitários para o parser JSON de payload da API - Scanntech 3.0"""

import pytest
import json
from src.parsers.json_parser import (
    parse_json_payload,
    parse_json_file,
    validate_json_payload,
    JSONParserError,
    JSONSchemaValidationError,
    JSONTypeConversionError,
)


# === JSON VÁLIDO COMPLETO ===
JSON_VALIDO_COMPLETO = {
    "fecha": "2026-09-15T14:30:00-03:00",
    "numero": "000123",
    "total": 55.30,
    "cancelacion": False,
    "detalles": [
        {"numeroItem": 1, "codigo": "7891000123456", "quantidade": 2, "valorUnitario": 25.90},
        {"numeroItem": 2, "codigo": "7891000123457", "quantidade": 1, "valorUnitario": 8.50}
    ],
    "pagos": [
        {"tipo": "Dinheiro", "valor": 55.30}
    ],
    "descuentoTotal": 5.00,
    "recargoTotal": 0.00,
    "codigoMoneda": "986",
    "cotizacion": 1.00
}

JSON_VALIDO_COMPLETO_STR = json.dumps(JSON_VALIDO_COMPLETO)

# === JSON VÁLIDO MÍNIMO (apenas campos obrigatórios) ===
JSON_VALIDO_MINIMO = {
    "fecha": "2026-09-15T14:30:00-03:00",
    "numero": "000124",
    "total": 25.90,
    "cancelacion": False,
    "detalles": [
        {"numeroItem": 1, "codigo": "7891000123456", "quantidade": 1, "valorUnitario": 25.90}
    ],
    "pagos": [
        {"tipo": "Dinheiro", "valor": 25.90}
    ]
}

JSON_VALIDO_MINIMO_STR = json.dumps(JSON_VALIDO_MINIMO)

# === JSON COM CAMPOS OPCIONAIS COMO STRINGS (teste de conversão) ===
JSON_COM_STRINGS = {
    "fecha": "2026-09-15T14:30:00-03:00",
    "numero": "000125",
    "total": "55.30",  # string que deve virar float
    "cancelacion": "false",  # string que deve virar bool
    "detalles": [],
    "pagos": [],
    "descuentoTotal": "5.00",
    "recargoTotal": "0.00",
    "codigoMoneda": "986",
    "cotizacion": "1.00"
}

JSON_COM_STRINGS_STR = json.dumps(JSON_COM_STRINGS)

# === JSON COM CANCELACAO TRUE ===
JSON_CANCELADO = {
    "fecha": "2026-09-15T14:30:00-03:00",
    "numero": "000126",
    "total": -4.10,
    "cancelacion": True,
    "detalles": [
        {"numeroItem": 1, "codigo": "7891000123456", "quantidade": 1, "valorUnitario": 25.90}
    ],
    "pagos": [
        {"tipo": "Dinheiro", "valor": 0.00}
    ]
}

JSON_CANCELADO_STR = json.dumps(JSON_CANCELADO)


class TestParseJsonPayloadSucesso:
    """Testes para parsing bem-sucedido de JSON válido"""
    
    def test_parse_json_completo_sucesso(self):
        result = parse_json_payload(JSON_VALIDO_COMPLETO_STR)
        
        assert isinstance(result, dict)
        assert result["fecha"] == "2026-09-15T14:30:00-03:00"
        assert result["numero"] == "000123"
        assert result["total"] == 55.30
        assert result["cancelacion"] is False
        assert len(result["detalles"]) == 2
        assert len(result["pagos"]) == 1
        assert result["descuentoTotal"] == 5.00
        assert result["recargoTotal"] == 0.00
        assert result["codigoMoneda"] == "986"
        assert result["cotizacion"] == 1.00
    
    def test_parse_json_minimo_sucesso(self):
        result = parse_json_payload(JSON_VALIDO_MINIMO_STR)
        
        assert isinstance(result, dict)
        assert result["fecha"] == "2026-09-15T14:30:00-03:00"
        assert result["numero"] == "000124"
        assert result["total"] == 25.90
        assert result["cancelacion"] is False
        assert len(result["detalles"]) == 1
        assert len(result["pagos"]) == 1
        # Campos opcionais devem ter defaults aplicados
        assert result["descuentoTotal"] == 0.0
        assert result["recargoTotal"] == 0.0
        assert result["codigoMoneda"] == "986"
        assert result["cotizacion"] == 1.00
    
    def test_parse_json_com_strings_converte_tipos(self):
        result = parse_json_payload(JSON_COM_STRINGS_STR)
        
        assert isinstance(result["total"], float)
        assert result["total"] == 55.30
        assert isinstance(result["cancelacion"], bool)
        assert result["cancelacion"] is False
        assert isinstance(result["descuentoTotal"], float)
        assert result["descuentoTotal"] == 5.00
        assert isinstance(result["recargoTotal"], float)
        assert result["recargoTotal"] == 0.00
        assert isinstance(result["cotizacion"], float)
        assert result["cotizacion"] == 1.00
    
    def test_parse_json_cancelado_true(self):
        result = parse_json_payload(JSON_CANCELADO_STR)
        
        assert result["cancelacion"] is True
        assert result["total"] == -4.10


class TestParseJsonPayloadErros:
    """Testes para tratamento de erros"""
    
    def test_json_vazio_levanta_erro(self):
        with pytest.raises(JSONParserError) as exc_info:
            parse_json_payload("")
        assert "vazio" in str(exc_info.value).lower()
    
    def test_json_apenas_espacos_levanta_erro(self):
        with pytest.raises(JSONParserError) as exc_info:
            parse_json_payload("   ")
        assert "vazio" in str(exc_info.value).lower()
    
    def test_json_malformado_levanta_erro(self):
        json_invalido = '{"fecha": "2026-09-15", "numero": "123"'  # faltando }
        with pytest.raises(json.JSONDecodeError) as exc_info:
            parse_json_payload(json_invalido)
        assert "malformado" in str(exc_info.value).lower()
    
    def test_json_sem_campo_obrigatorio_fecha(self):
        json_sem_fecha = {k: v for k, v in JSON_VALIDO_MINIMO.items() if k != "fecha"}
        with pytest.raises(JSONSchemaValidationError) as exc_info:
            parse_json_payload(json.dumps(json_sem_fecha))
        assert "fecha" in str(exc_info.value).lower()
    
    def test_json_sem_campo_obrigatorio_numero(self):
        json_sem_numero = {k: v for k, v in JSON_VALIDO_MINIMO.items() if k != "numero"}
        with pytest.raises(JSONSchemaValidationError) as exc_info:
            parse_json_payload(json.dumps(json_sem_numero))
        assert "numero" in str(exc_info.value).lower()
    
    def test_json_sem_campo_obrigatorio_total(self):
        json_sem_total = {k: v for k, v in JSON_VALIDO_MINIMO.items() if k != "total"}
        with pytest.raises(JSONSchemaValidationError) as exc_info:
            parse_json_payload(json.dumps(json_sem_total))
        assert "total" in str(exc_info.value).lower()
    
    def test_json_sem_campo_obrigatorio_cancelacion(self):
        json_sem_cancel = {k: v for k, v in JSON_VALIDO_MINIMO.items() if k != "cancelacion"}
        with pytest.raises(JSONSchemaValidationError) as exc_info:
            parse_json_payload(json.dumps(json_sem_cancel))
        assert "cancelacion" in str(exc_info.value).lower()
    
    def test_json_sem_campo_obrigatorio_detalles(self):
        json_sem_detalhes = {k: v for k, v in JSON_VALIDO_MINIMO.items() if k != "detalles"}
        with pytest.raises(JSONSchemaValidationError) as exc_info:
            parse_json_payload(json.dumps(json_sem_detalhes))
        assert "detalles" in str(exc_info.value).lower()
    
    def test_json_sem_campo_obrigatorio_pagos(self):
        json_sem_pagos = {k: v for k, v in JSON_VALIDO_MINIMO.items() if k != "pagos"}
        with pytest.raises(JSONSchemaValidationError) as exc_info:
            parse_json_payload(json.dumps(json_sem_pagos))
        assert "pagos" in str(exc_info.value).lower()
    
    def test_json_total_negativo_como_numero(self):
        # total pode ser negativo (cupom cancelado), schema permite
        json_total_neg = JSON_VALIDO_MINIMO.copy()
        json_total_neg["total"] = -10.00
        result = parse_json_payload(json.dumps(json_total_neg))
        assert result["total"] == -10.00
    
    def test_json_total_string_invalida(self):
        json_total_invalido = JSON_VALIDO_MINIMO.copy()
        json_total_invalido["total"] = "abc"
        with pytest.raises(JSONTypeConversionError) as exc_info:
            parse_json_payload(json.dumps(json_total_invalido))
        assert "total" in str(exc_info.value).lower()
    
    def test_json_cancelacion_string_invalida(self):
        json_cancel_invalido = JSON_VALIDO_MINIMO.copy()
        json_cancel_invalido["cancelacion"] = "talvez"
        # Deve converter para bool (qualquer string não-vazia vira True)
        result = parse_json_payload(json.dumps(json_cancel_invalido))
        assert result["cancelacion"] is True  # "talvez" é truthy
    
    def test_json_detalles_nao_e_lista(self):
        json_detalhes_invalido = JSON_VALIDO_MINIMO.copy()
        json_detalhes_invalido["detalles"] = "nao-e-lista"
        with pytest.raises(JSONTypeConversionError) as exc_info:
            parse_json_payload(json.dumps(json_detalhes_invalido))
        assert "detalles" in str(exc_info.value).lower()
    
    def test_json_pagos_nao_e_lista(self):
        json_pagos_invalido = JSON_VALIDO_MINIMO.copy()
        json_pagos_invalido["pagos"] = "nao-e-lista"
        with pytest.raises(JSONTypeConversionError) as exc_info:
            parse_json_payload(json.dumps(json_pagos_invalido))
        assert "pagos" in str(exc_info.value).lower()
    
    def test_json_propriedade_adicional_nao_permitida(self):
        # additionalProperties: false no schema
        json_com_extra = JSON_VALIDO_MINIMO.copy()
        json_com_extra["campo_extra"] = "nao-permitido"
        with pytest.raises(JSONSchemaValidationError) as exc_info:
            parse_json_payload(json.dumps(json_com_extra))
        assert "extra" in str(exc_info.value).lower() or "additional" in str(exc_info.value).lower()


class TestParseJsonFile:
    """Testes para parse_json_file"""
    
    def test_parse_json_file_sucesso(self, tmp_path):
        file_path = tmp_path / "payload_teste.json"
        file_path.write_text(JSON_VALIDO_COMPLETO_STR, encoding="utf-8")
        
        result = parse_json_file(str(file_path))
        
        assert isinstance(result, dict)
        assert result["numero"] == "000123"
    
    def test_parse_json_file_nao_encontrado(self):
        with pytest.raises(JSONParserError) as exc_info:
            parse_json_file("/caminho/inexistente/payload.json")
        assert "não encontrado" in str(exc_info.value).lower()


class TestValidateJsonPayload:
    """Testes para validate_json_payload"""
    
    def test_validate_json_valido_retorna_true(self):
        assert validate_json_payload(JSON_VALIDO_COMPLETO_STR) is True
    
    def test_validate_json_invalido_levanta_erro(self):
        json_invalido = '{"fecha": "2026-09-15"}'  # incompleto
        with pytest.raises(JSONSchemaValidationError):
            validate_json_payload(json_invalido)


class TestCasosEdge:
    """Testes para casos edge"""
    
    def test_campos_opcionais_com_valor_zero(self):
        json_com_zeros = JSON_VALIDO_MINIMO.copy()
        json_com_zeros["descuentoTotal"] = 0
        json_com_zeros["recargoTotal"] = 0
        json_com_zeros["cotizacion"] = 0
        
        result = parse_json_payload(json.dumps(json_com_zeros))
        
        assert result["descuentoTotal"] == 0.0
        assert result["recargoTotal"] == 0.0
        assert result["cotizacion"] == 0.0
    
    def test_codigo_moeda_enum_valido(self):
        # O schema só permite "986"
        json_moeda = JSON_VALIDO_MINIMO.copy()
        json_moeda["codigoMoneda"] = "986"
        result = parse_json_payload(json.dumps(json_moeda))
        assert result["codigoMoneda"] == "986"
    
    def test_codigo_moeda_enum_invalido(self):
        json_moeda_invalida = JSON_VALIDO_MINIMO.copy()
        json_moeda_invalida["codigoMoneda"] = "USD"
        with pytest.raises(JSONSchemaValidationError) as exc_info:
            parse_json_payload(json.dumps(json_moeda_invalida))
        assert "enum" in str(exc_info.value).lower() or "986" in str(exc_info.value)
    
    def test_detalhes_array_vazio(self):
        json_detalhes_vazio = JSON_VALIDO_MINIMO.copy()
        json_detalhes_vazio["detalles"] = []
        json_detalhes_vazio["pagos"] = []
        
        result = parse_json_payload(json.dumps(json_detalhes_vazio))
        
        assert result["detalles"] == []
        assert result["pagos"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])