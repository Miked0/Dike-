"""
Parser JSON para payload da API - Scanntech 3.0

Este módulo implementa a validação e processamento do payload JSON da API
conforme estrutura do schema_etapa01.json.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, Any, Optional


class JSONParserError(Exception):
    """Exceção base para erros do parser JSON."""
    pass


class JSONSchemaValidationError(JSONParserError):
    """Erro de validação contra o schema JSON."""
    pass


class JSONTypeConversionError(JSONParserError):
    """Erro de conversão de tipos."""
    pass


# Carrega o schema uma vez na importação
_SCHEMA_PATH = Path(__file__).parent.parent.parent / "config" / "schemas" / "schema_etapa01.json"
_SCHEMA: Optional[Dict[str, Any]] = None


def _load_schema() -> Dict[str, Any]:
    """Carrega o schema JSON do arquivo."""
    global _SCHEMA
    if _SCHEMA is None:
        try:
            with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
                _SCHEMA = json.load(f)
        except FileNotFoundError:
            raise JSONParserError(f"Arquivo de schema não encontrado: {_SCHEMA_PATH}")
        except json.JSONDecodeError as e:
            raise JSONParserError(f"Schema JSON malformado: {e}")
    return _SCHEMA


def _apply_defaults(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Aplica valores padrão do schema para campos opcionais ausentes."""
    result = data.copy()
    properties = schema.get("properties", {})
    
    for field_name, field_schema in properties.items():
        if field_name not in result and "default" in field_schema:
            result[field_name] = field_schema["default"]
    
    return result


def _convert_types(data: Dict[str, Any]) -> Dict[str, Any]:
    """Converte tipos dos campos conforme especificação do schema."""
    result = data.copy()
    
    # fecha: string (date-time) → mantém como string ISO 8601
    if "fecha" in result and result["fecha"] is not None:
        result["fecha"] = str(result["fecha"])
    
    # numero: string → str
    if "numero" in result and result["numero"] is not None:
        result["numero"] = str(result["numero"])
    
    # total: number → float (aceita string numérica)
    if "total" in result and result["total"] is not None:
        try:
            result["total"] = float(result["total"])
        except (ValueError, TypeError) as e:
            raise JSONTypeConversionError(f"Campo 'total' deve ser numérico: {e}")
    
    # cancelacion: boolean → bool (aceita string "true"/"false", vazia como False)
    if "cancelacion" in result and result["cancelacion"] is not None:
        val = result["cancelacion"]
        if isinstance(val, str):
            # Trata string vazia como False
            # Trata "false", "0", "no", "não" como False (case-insensitive)
            # Demais strings como True
            if val == "":
                result["cancelacion"] = False
            else:
                lower_val = val.lower()
                result["cancelacion"] = lower_val not in {"false", "0", "no", "não"}
        else:
            result["cancelacion"] = bool(val)
    
    # detalhes: array → list
    if "detalles" in result and result["detalles"] is not None:
        if not isinstance(result["detalles"], list):
            raise JSONTypeConversionError("Campo 'detalles' deve ser uma lista")
        result["detalles"] = list(result["detalles"])
    
    # pagos: array → list
    if "pagos" in result and result["pagos"] is not None:
        if not isinstance(result["pagos"], list):
            raise JSONTypeConversionError("Campo 'pagos' deve ser uma lista")
        result["pagos"] = list(result["pagos"])
    
    # descuentoTotal: number → float (opcional, default 0)
    if "descuentoTotal" in result and result["descuentoTotal"] is not None:
        try:
            result["descuentoTotal"] = float(result["descuentoTotal"])
        except (ValueError, TypeError) as e:
            raise JSONTypeConversionError(f"Campo 'descuentoTotal' deve ser numérico: {e}")
    
    # recargoTotal: number → float (opcional, default 0)
    if "recargoTotal" in result and result["recargoTotal"] is not None:
        try:
            result["recargoTotal"] = float(result["recargoTotal"])
        except (ValueError, TypeError) as e:
            raise JSONTypeConversionError(f"Campo 'recargoTotal' deve ser numérico: {e}")
    
    # codigoMoneda: string → str (opcional, default "986")
    if "codigoMoneda" in result and result["codigoMoneda"] is not None:
        result["codigoMoneda"] = str(result["codigoMoneda"])
    
    # cotizacion: number → float (opcional, default 1.00)
    if "cotizacion" in result and result["cotizacion"] is not None:
        try:
            result["cotizacion"] = float(result["cotizacion"])
        except (ValueError, TypeError) as e:
            raise JSONTypeConversionError(f"Campo 'cotizacion' deve ser numérico: {e}")
    
    return result


def parse_json_payload(json_content: str) -> Dict[str, Any]:
    """
    Processa o payload JSON da API e retorna um dicionário com os dados validados.
    
    Args:
        json_content: String contendo o JSON do payload da API
        
    Returns:
        Dicionário com os dados do payload validados e convertidos
        
    Raises:
        json.JSONDecodeError: Se o JSON for malformado
        JSONSchemaValidationError: Se o JSON não estiver conforme o schema
        JSONTypeConversionError: Se houver erro na conversão de tipos
    """
    if not json_content or not json_content.strip():
        raise JSONParserError("Conteúdo JSON vazio")
    
    # Parse JSON
    try:
        data = json.loads(json_content)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"JSON malformado: {e.msg}", e.doc, e.pos)
    
    # Carrega schema
    schema = _load_schema()
    
    # Aplica defaults para campos opcionais ANTES da conversão
    data = _apply_defaults(data, schema)
    
    # Converte tipos ANTES da validação do schema
    # Isso permite aceitar strings numéricas, "true"/"false", etc.
    data = _convert_types(data)
    
    # Valida contra schema APÓS conversão de tipos
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        raise JSONSchemaValidationError(f"Validação do schema falhou: {e.message}")
    
    return data


def parse_json_file(filepath: str) -> Dict[str, Any]:
    """
    Processa um arquivo JSON da API.
    
    Args:
        filepath: Caminho para o arquivo JSON
        
    Returns:
        Dicionário com os dados do payload validados e convertidos
        
    Raises:
        JSONParserError: Se o arquivo não existir ou JSON for inválido
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise JSONParserError(f"Arquivo não encontrado: {filepath}")
    except UnicodeDecodeError:
        # Tenta latin-1 se utf-8 falhar
        with open(filepath, "r", encoding="latin-1") as f:
            content = f.read()
    
    return parse_json_payload(content)


def validate_json_payload(json_content: str) -> bool:
    """
    Apenas valida o JSON contra o schema sem processar.
    
    Args:
        json_content: String contendo o JSON do payload da API
        
    Returns:
        True se válido
        
    Raises:
        json.JSONDecodeError: Se o JSON for malformado
        JSONSchemaValidationError: Se o JSON não estiver conforme o schema
    """
    if not json_content or not json_content.strip():
        raise JSONParserError("Conteúdo JSON vazio")
    
    try:
        data = json.loads(json_content)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"JSON malformado: {e.msg}", e.doc, e.pos)
    
    schema = _load_schema()
    
    # Para validação simples, aplica defaults e converte antes de validar
    data = _apply_defaults(data, schema)
    data = _convert_types(data)
    
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        raise JSONSchemaValidationError(f"Validação do schema falhou: {e.message}")
    
    return True