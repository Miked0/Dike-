"""Parser XML para Cupons Fiscais - Scanntech 3.0

Este módulo implementa a extração de dados de cupons fiscais no formato XML
conforme estrutura da Scanntech 3.0.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from xml.etree import ElementTree as ET
import re


@dataclass
class ItemDetalhado:
    """Representa um item detalhado do cupom fiscal."""
    numero_item: int
    codigo: str
    descricao: str
    quantidade: Decimal
    unidade: str
    valor_unitario: Decimal
    valor_total_item: Decimal
    indicador_totalizador: int


@dataclass
class FormaPagamento:
    """Representa uma forma de pagamento do cupom fiscal."""
    tipo: str
    valor: Decimal


@dataclass
class CupomFiscalParsed:
    """Resultado do parsing do cupom fiscal com todos os campos obrigatórios."""
    fecha: str  # Data de emissão no formato YYYY-MM-DD
    numero: str  # Número do cupom
    total: Decimal  # Valor total do cupom
    cancelacion: bool  # Indica se o cupom foi cancelado
    detalles: list[ItemDetalhado]  # Lista de itens detalhados
    pagos: list[FormaPagamento]  # Lista de formas de pagamento
    descuentoTotal: Decimal  # Total de descontos
    recargoTotal: Decimal  # Total de recargos
    codigoMoneda: str  # Código da moeda (ex: BRL)
    cotizacion: Decimal  # Cotação da moeda


class XMLParserError(Exception):
    """Exceção base para erros do parser XML."""
    pass


class XMLStructureError(XMLParserError):
    """Erro na estrutura do XML (elementos obrigatórios ausentes)."""
    pass


class XMLValidationError(XMLParserError):
    """Erro de validação dos dados extraídos."""
    pass


def _get_text(element: Optional[ET.Element], path: str, default: str = "") -> str:
    """Extrai texto de um elemento XML de forma segura."""
    if element is None:
        return default
    found = element.find(path)
    return found.text.strip() if found is not None and found.text else default


def _get_decimal(element: Optional[ET.Element], path: str, default: Decimal = Decimal("0")) -> Decimal:
    """Extrai valor decimal de um elemento XML de forma segura."""
    text = _get_text(element, path)
    if not text:
        return default
    try:
        return Decimal(text.replace(",", "."))
    except Exception:
        return default


def _get_int(element: Optional[ET.Element], path: str, default: int = 0) -> int:
    """Extrai valor inteiro de um elemento XML de forma segura."""
    text = _get_text(element, path)
    if not text:
        return default
    try:
        return int(text)
    except Exception:
        return default


def _parse_date(data_emissao: str, hora_emissao: str) -> str:
    """Concatena data e hora e retorna no formato ISO."""
    if not data_emissao:
        return ""
    if hora_emissao:
        return f"{data_emissao}T{hora_emissao}"
    return data_emissao


def _detect_cancelacion(root: ET.Element) -> bool:
    """Detecta se o cupom foi cancelado baseado em indicadores no XML."""
    # Verifica se há indicador de cancelamento
    cancelado = root.find(".//Cancelado")
    if cancelado is not None and cancelado.text:
        return cancelado.text.strip().lower() in ("true", "1", "sim", "yes")
    
    # Verifica se valor total é negativo ou zero com itens
    total_elem = root.find(".//Totalizadores/ValorTotal")
    if total_elem is not None and total_elem.text:
        try:
            total = Decimal(total_elem.text.replace(",", "."))
            if total < 0:
                return True
        except Exception:
            pass
    
    return False


def _extract_detalhes(root: ET.Element) -> list[ItemDetalhado]:
    """Extrai a lista de itens detalhados do cupom."""
    detalhes = []
    detalhes_elem = root.find("Detalhes")
    if detalhes_elem is None:
        return detalhes
    
    for item_elem in detalhes_elem.findall("ItemDetalhado"):
        item = ItemDetalhado(
            numero_item=_get_int(item_elem, "NumeroItem"),
            codigo=_get_text(item_elem, "Codigo"),
            descricao=_get_text(item_elem, "Descricao"),
            quantidade=_get_decimal(item_elem, "Quantidade"),
            unidade=_get_text(item_elem, "Unidade"),
            valor_unitario=_get_decimal(item_elem, "ValorUnitario"),
            valor_total_item=_get_decimal(item_elem, "ValorTotalItem"),
            indicador_totalizador=_get_int(item_elem, "IndicadorTotalizador"),
        )
        detalhes.append(item)
    
    return detalhes


def _extract_pagamentos(root: ET.Element) -> list[FormaPagamento]:
    """Extrai a lista de formas de pagamento do cupom."""
    pagamentos = []
    pagamentos_elem = root.find("Pagamentos")
    if pagamentos_elem is None:
        return pagamentos
    
    for forma_elem in pagamentos_elem.findall("FormaPagamento"):
        forma = FormaPagamento(
            tipo=_get_text(forma_elem, "Tipo"),
            valor=_get_decimal(forma_elem, "Valor"),
        )
        pagamentos.append(forma)
    
    return pagamentos


def _validate_required_fields(root: ET.Element) -> list[str]:
    """Valida campos obrigatórios e retorna lista de erros."""
    errors = []
    
    identificacao = root.find("Identificacao")
    if identificacao is None:
        errors.append("Elemento 'Identificacao' obrigatório não encontrado")
    else:
        if _get_text(identificacao, "Numero") == "":
            errors.append("Campo obrigatório 'Numero' ausente em Identificacao")
        if _get_text(identificacao, "DataEmissao") == "":
            errors.append("Campo obrigatório 'DataEmissao' ausente em Identificacao")
    
    emitente = root.find("Emitente")
    if emitente is None:
        errors.append("Elemento 'Emitente' obrigatório não encontrado")
    else:
        if _get_text(emitente, "CNPJ") == "":
            errors.append("Campo obrigatório 'CNPJ' ausente em Emitente")
    
    totalizadores = root.find("Totalizadores")
    if totalizadores is None:
        errors.append("Elemento 'Totalizadores' obrigatório não encontrado")
    else:
        if _get_text(totalizadores, "ValorTotal") == "":
            errors.append("Campo obrigatório 'ValorTotal' ausente em Totalizadores")
    
    return errors


def parse_xml_cupom_fiscal(xml_content: str) -> CupomFiscalParsed:
    """
    Parses XML de cupom fiscal e retorna objeto com todos os campos obrigatórios.
    
    Args:
        xml_content: String contendo o XML do cupom fiscal
        
    Returns:
        CupomFiscalParsed com todos os campos extraídos
        
    Raises:
        XMLStructureError: Se a estrutura XML for inválida ou campos obrigatórios faltarem
        XMLValidationError: Se os dados extraídos falharem na validação
    """
    if not xml_content or not xml_content.strip():
        raise XMLStructureError("Conteúdo XML vazio")
    
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise XMLStructureError(f"XML malformado: {e}")
    
    # Valida estrutura básica
    validation_errors = _validate_required_fields(root)
    if validation_errors:
        raise XMLStructureError("; ".join(validation_errors))
    
    identificacao = root.find("Identificacao")
    emitente = root.find("Emitente")
    totalizadores = root.find("Totalizadores")
    
    # Extrai campos obrigatórios
    numero = _get_text(identificacao, "Numero")
    data_emissao = _get_text(identificacao, "DataEmissao")
    hora_emissao = _get_text(identificacao, "HoraEmissao")
    
    fecha = _parse_date(data_emissao, hora_emissao)
    
    total = _get_decimal(totalizadores, "ValorTotal")
    descuentoTotal = _get_decimal(totalizadores, "ValorDesconto")
    
    # RecargoTotal não está presente nos exemplos, assume 0
    recargoTotal = _get_decimal(totalizadores, "ValorRecargo", Decimal("0"))
    # Se não existe ValorRecargo, tenta ValorAcrescimo
    if recargoTotal == 0:
        recargoTotal = _get_decimal(totalizadores, "ValorAcrescimo", Decimal("0"))
    
    detalhes = _extract_detalhes(root)
    pagos = _extract_pagamentos(root)
    
    cancelacion = _detect_cancelacion(root)
    
    # Código da moeda e cotação - defaults para BRL
    codigoMoneda = "BRL"
    cotizacion = Decimal("1.0")
    
    # Tenta extrair do emitente ou totalizadores se disponível
    moeda_elem = root.find(".//CodigoMoeda") or root.find(".//Moeda")
    if moeda_elem is not None and moeda_elem.text:
        codigoMoneda = moeda_elem.text.strip()
    
    cotacao_elem = root.find(".//Cotacao") or root.find(".//Cotizacion")
    if cotacao_elem is not None and cotacao_elem.text:
        try:
            cotizacion = Decimal(cotacao_elem.text.replace(",", "."))
        except Exception:
            pass
    
    return CupomFiscalParsed(
        fecha=fecha,
        numero=numero,
        total=total,
        cancelacion=cancelacion,
        detalles=detalhes,
        pagos=pagos,
        descuentoTotal=descuentoTotal,
        recargoTotal=recargoTotal,
        codigoMoneda=codigoMoneda,
        cotizacion=cotizacion,
    )


def parse_xml_file(filepath: str) -> CupomFiscalParsed:
    """
    Parses um arquivo XML de cupom fiscal.
    
    Args:
        filepath: Caminho para o arquivo XML
        
    Returns:
        CupomFiscalParsed com todos os campos extraídos
        
    Raises:
        XMLStructureError: Se o arquivo não existir ou XML for inválido
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise XMLStructureError(f"Arquivo não encontrado: {filepath}")
    except UnicodeDecodeError:
        # Tenta latin-1 se utf-8 falhar
        with open(filepath, "r", encoding="latin-1") as f:
            content = f.read()
    
    return parse_xml_cupom_fiscal(content)