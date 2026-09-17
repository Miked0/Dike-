"""Testes unitários para o parser XML de Cupons Fiscais - Scanntech 3.0"""

import pytest
from decimal import Decimal
from src.parsers.xml_parser import (
    parse_xml_cupom_fiscal,
    parse_xml_file,
    CupomFiscalParsed,
    ItemDetalhado,
    FormaPagamento,
    XMLStructureError,
    XMLValidationError,
)


# === XML DE TESTE CT-001: Cupom Válido ===
XML_CT001 = """<?xml version="1.0" encoding="UTF-8"?>
<CupomFiscal versao="3.0">
    <Identificacao>
        <Numero>000123</Numero>
        <DataEmissao>2026-09-15</DataEmissao>
        <HoraEmissao>14:30:00</HoraEmissao>
        <CodigoCaixa>001</CodigoCaixa>
        <CodigoOperador>OP001</CodigoOperador>
    </Identificacao>
    <Emitente>
        <CNPJ>12345678000195</CNPJ>
        <RazaoSocial>SUPERMERCADO EXEMPLO LTDA</RazaoSocial>
    </Emitente>
    <Detalhes>
        <ItemDetalhado>
            <NumeroItem>1</NumeroItem>
            <Codigo>7891000123456</Codigo>
            <Descricao>ARROZ AGULHA 5KG</Descricao>
            <Quantidade>2</Quantidade>
            <Unidade>KG</Unidade>
            <ValorUnitario>25.90</ValorUnitario>
            <ValorTotalItem>51.80</ValorTotalItem>
            <IndicadorTotalizador>1</IndicadorTotalizador>
        </ItemDetalhado>
        <ItemDetalhado>
            <NumeroItem>2</NumeroItem>
            <Codigo>7891000123457</Codigo>
            <Descricao>FEIJAO CARIOCA 1KG</Descricao>
            <Quantidade>1</Quantidade>
            <Unidade>KG</Unidade>
            <ValorUnitario>8.50</ValorUnitario>
            <ValorTotalItem>8.50</ValorTotalItem>
            <IndicadorTotalizador>1</IndicadorTotalizador>
        </ItemDetalhado>
    </Detalhes>
    <Totalizadores>
        <ValorTotalBruto>60.30</ValorTotalBruto>
        <ValorDesconto>5.00</ValorDesconto>
        <ValorTotal>55.30</ValorTotal>
        <ValorSubtotal>55.30</ValorSubtotal>
    </Totalizadores>
    <Pagamentos>
        <FormaPagamento>
            <Tipo>Dinheiro</Tipo>
            <Valor>55.30</Valor>
        </FormaPagamento>
    </Pagamentos>
</CupomFiscal>"""

# === XML DE TESTE CT-002: Desconto Excessivo ===
XML_CT002 = """<?xml version="1.0" encoding="UTF-8"?>
<CupomFiscal versao="3.0">
    <Identificacao>
        <Numero>000124</Numero>
        <DataEmissao>2026-09-15</DataEmissao>
        <HoraEmissao>14:35:00</HoraEmissao>
        <CodigoCaixa>001</CodigoCaixa>
        <CodigoOperador>OP001</CodigoOperador>
    </Identificacao>
    <Emitente>
        <CNPJ>12345678000195</CNPJ>
        <RazaoSocial>SUPERMERCADO EXEMPLO LTDA</RazaoSocial>
    </Emitente>
    <Detalhes>
        <ItemDetalhado>
            <NumeroItem>1</NumeroItem>
            <Codigo>7891000123456</Codigo>
            <Descricao>ARROZ AGULHA 5KG</Descricao>
            <Quantidade>1</Quantidade>
            <Unidade>KG</Unidade>
            <ValorUnitario>25.90</ValorUnitario>
            <ValorTotalItem>25.90</ValorTotalItem>
            <IndicadorTotalizador>1</IndicadorTotalizador>
        </ItemDetalhado>
    </Detalhes>
    <Totalizadores>
        <ValorTotalBruto>25.90</ValorTotalBruto>
        <ValorDesconto>30.00</ValorDesconto>
        <ValorTotal>-4.10</ValorTotal>
        <ValorSubtotal>-4.10</ValorSubtotal>
    </Totalizadores>
    <Pagamentos>
        <FormaPagamento>
            <Tipo>Dinheiro</Tipo>
            <Valor>0.00</Valor>
        </FormaPagamento>
    </Pagamentos>
</CupomFiscal>"""

# === XML DE TESTE CT-003: Pagos Insuficientes ===
XML_CT003 = """<?xml version="1.0" encoding="UTF-8"?>
<CupomFiscal versao="3.0">
    <Identificacao>
        <Numero>000125</Numero>
        <DataEmissao>2026-09-15</DataEmissao>
        <HoraEmissao>14:40:00</HoraEmissao>
        <CodigoCaixa>001</CodigoCaixa>
        <CodigoOperador>OP001</CodigoOperador>
    </Identificacao>
    <Emitente>
        <CNPJ>12345678000195</CNPJ>
        <RazaoSocial>SUPERMERCADO EXEMPLO LTDA</RazaoSocial>
    </Emitente>
    <Detalhes>
        <ItemDetalhado>
            <NumeroItem>1</NumeroItem>
            <Codigo>7891000123456</Codigo>
            <Descricao>ARROZ AGULHA 5KG</Descricao>
            <Quantidade>1</Quantidade>
            <Unidade>KG</Unidade>
            <ValorUnitario>25.90</ValorUnitario>
            <ValorTotalItem>25.90</ValorTotalItem>
            <IndicadorTotalizador>1</IndicadorTotalizador>
        </ItemDetalhado>
    </Detalhes>
    <Totalizadores>
        <ValorTotalBruto>25.90</ValorTotalBruto>
        <ValorDesconto>0.00</ValorDesconto>
        <ValorTotal>25.90</ValorTotal>
        <ValorSubtotal>25.90</ValorSubtotal>
    </Totalizadores>
    <Pagamentos>
        <FormaPagamento>
            <Tipo>Dinheiro</Tipo>
            <Valor>20.00</Valor>
        </FormaPagamento>
    </Pagamentos>
</CupomFiscal>"""

# === XML DE TESTE CT-004: Campo Obrigatório Ausente ===
XML_CT004 = """<?xml version="1.0" encoding="UTF-8"?>
<CupomFiscal versao="3.0">
    <Identificacao>
        <!-- CAMPO NUMERO AUSENTE PROPOSITALMENTE -->
        <DataEmissao>2026-09-15</DataEmissao>
        <HoraEmissao>14:45:00</HoraEmissao>
        <CodigoCaixa>001</CodigoCaixa>
        <CodigoOperador>OP001</CodigoOperador>
    </Identificacao>
    <Emitente>
        <CNPJ>12345678000195</CNPJ>
        <RazaoSocial>SUPERMERCADO EXEMPLO LTDA</RazaoSocial>
    </Emitente>
    <Detalhes>
        <ItemDetalhado>
            <NumeroItem>1</NumeroItem>
            <Codigo>7891000123456</Codigo>
            <Descricao>ARROZ AGULHA 5KG</Descricao>
            <Quantidade>1</Quantidade>
            <Unidade>KG</Unidade>
            <ValorUnitario>25.90</ValorUnitario>
            <ValorTotalItem>25.90</ValorTotalItem>
            <IndicadorTotalizador>1</IndicadorTotalizador>
        </ItemDetalhado>
    </Detalhes>
    <Totalizadores>
        <ValorTotalBruto>25.90</ValorTotalBruto>
        <ValorDesconto>0.00</ValorDesconto>
        <ValorTotal>25.90</ValorTotal>
        <ValorSubtotal>25.90</ValorSubtotal>
    </Totalizadores>
    <Pagamentos>
        <FormaPagamento>
            <Tipo>Dinheiro</Tipo>
            <Valor>25.90</Valor>
        </FormaPagamento>
    </Pagamentos>
</CupomFiscal>"""

# === XML DE TESTE CT-005: Detalhes Informados mas Vazios ===
XML_CT005 = """<?xml version="1.0" encoding="UTF-8"?>
<CupomFiscal versao="3.0">
    <Identificacao>
        <Numero>000126</Numero>
        <DataEmissao>2026-09-15</DataEmissao>
        <HoraEmissao>14:50:00</HoraEmissao>
        <CodigoCaixa>001</CodigoCaixa>
        <CodigoOperador>OP001</CodigoOperador>
    </Identificacao>
    <Emitente>
        <CNPJ>12345678000195</CNPJ>
        <RazaoSocial>SUPERMERCADO EXEMPLO LTDA</RazaoSocial>
    </Emitente>
    <Detalhes>
        <!-- ARRAY DETALHES PRESENTE MAS VAZIO -->
    </Detalhes>
    <Totalizadores>
        <ValorTotalBruto>0.00</ValorTotalBruto>
        <ValorDesconto>0.00</ValorDesconto>
        <ValorTotal>0.00</ValorTotal>
        <ValorSubtotal>0.00</ValorSubtotal>
    </Totalizadores>
    <Pagamentos>
        <FormaPagamento>
            <Tipo>Dinheiro</Tipo>
            <Valor>0.00</Valor>
        </FormaPagamento>
    </Pagamentos>
</CupomFiscal>"""


class TestCT001CupomValido:
    """Testes para CT-001: Cupom Válido com todos os campos corretos"""
    
    def test_parse_ct001_sucesso(self):
        result = parse_xml_cupom_fiscal(XML_CT001)
        
        assert isinstance(result, CupomFiscalParsed)
        assert result.numero == "000123"
        assert result.fecha == "2026-09-15T14:30:00"
        assert result.total == Decimal("55.30")
        assert result.cancelacion is False
        assert result.descuentoTotal == Decimal("5.00")
        assert result.recargoTotal == Decimal("0")
        assert result.codigoMoneda == "BRL"
        assert result.cotizacion == Decimal("1.0")
    
    def test_parse_ct001_detalhes_corretos(self):
        result = parse_xml_cupom_fiscal(XML_CT001)
        
        assert len(result.detalles) == 2
        
        item1 = result.detalles[0]
        assert item1.numero_item == 1
        assert item1.codigo == "7891000123456"
        assert item1.descricao == "ARROZ AGULHA 5KG"
        assert item1.quantidade == Decimal("2")
        assert item1.unidade == "KG"
        assert item1.valor_unitario == Decimal("25.90")
        assert item1.valor_total_item == Decimal("51.80")
        assert item1.indicador_totalizador == 1
        
        item2 = result.detalles[1]
        assert item2.numero_item == 2
        assert item2.codigo == "7891000123457"
        assert item2.descricao == "FEIJAO CARIOCA 1KG"
        assert item2.quantidade == Decimal("1")
        assert item2.valor_unitario == Decimal("8.50")
        assert item2.valor_total_item == Decimal("8.50")
    
    def test_parse_ct001_pagamentos_corretos(self):
        result = parse_xml_cupom_fiscal(XML_CT001)
        
        assert len(result.pagos) == 1
        pagamento = result.pagos[0]
        assert pagamento.tipo == "Dinheiro"
        assert pagamento.valor == Decimal("55.30")


class TestCT002DescontoExcessivo:
    """Testes para CT-002: Cupom onde o desconto total é maior que o total do movimento"""
    
    def test_parse_ct002_sucesso(self):
        result = parse_xml_cupom_fiscal(XML_CT002)
        
        assert isinstance(result, CupomFiscalParsed)
        assert result.numero == "000124"
        assert result.total == Decimal("-4.10")
        assert result.descuentoTotal == Decimal("30.00")
        # Valor total negativo deve marcar como cancelado
        assert result.cancelacion is True
    
    def test_parse_ct002_detalhes_corretos(self):
        result = parse_xml_cupom_fiscal(XML_CT002)
        
        assert len(result.detalles) == 1
        item = result.detalles[0]
        assert item.numero_item == 1
        assert item.valor_total_item == Decimal("25.90")
    
    def test_parse_ct002_pagamento_zero(self):
        result = parse_xml_cupom_fiscal(XML_CT002)
        
        assert len(result.pagos) == 1
        assert result.pagos[0].valor == Decimal("0.00")


class TestCT003PagosInsuficientes:
    """Testes para CT-003: Cupom onde a soma dos pagos é menor que o total"""
    
    def test_parse_ct003_sucesso(self):
        result = parse_xml_cupom_fiscal(XML_CT003)
        
        assert isinstance(result, CupomFiscalParsed)
        assert result.numero == "000125"
        assert result.total == Decimal("25.90")
        assert result.cancelacion is False  # Total positivo, não cancelado
    
    def test_parse_ct003_pagamento_menor_que_total(self):
        result = parse_xml_cupom_fiscal(XML_CT003)
        
        assert len(result.pagos) == 1
        assert result.pagos[0].valor == Decimal("20.00")
        assert result.pagos[0].valor < result.total


class TestCT004CampoObrigatorioAusente:
    """Testes para CT-004: Cupom com campos obrigatórios faltando (ex: numero)"""
    
    def test_parse_ct004_erro_campo_numero_ausente(self):
        with pytest.raises(XMLStructureError) as exc_info:
            parse_xml_cupom_fiscal(XML_CT004)
        
        assert "Numero" in str(exc_info.value)
        assert "ausente" in str(exc_info.value).lower()


class TestCT005DetalhesVazios:
    """Testes para CT-005: Cupom com detalhes informados mas vazios"""
    
    def test_parse_ct005_sucesso(self):
        result = parse_xml_cupom_fiscal(XML_CT005)
        
        assert isinstance(result, CupomFiscalParsed)
        assert result.numero == "000126"
        assert result.total == Decimal("0.00")
        assert result.cancelacion is False
    
    def test_parse_ct005_detalhes_lista_vazia(self):
        result = parse_xml_cupom_fiscal(XML_CT005)
        
        assert result.detalles == []
        assert len(result.detalles) == 0
    
    def test_parse_ct005_pagamento_zero(self):
        result = parse_xml_cupom_fiscal(XML_CT005)
        
        assert len(result.pagos) == 1
        assert result.pagos[0].valor == Decimal("0.00")


class TestErrosXML:
    """Testes para tratamento de erros de XML malformado ou inválido"""
    
    def test_xml_vazio_levanta_erro(self):
        with pytest.raises(XMLStructureError) as exc_info:
            parse_xml_cupom_fiscal("")
        assert "vazio" in str(exc_info.value).lower()
    
    def test_xml_malformado_levanta_erro(self):
        xml_invalido = "<CupomFiscal><Identificacao><Numero>123</Identificacao></CupomFiscal>"
        with pytest.raises(XMLStructureError) as exc_info:
            parse_xml_cupom_fiscal(xml_invalido)
        assert "malformado" in str(exc_info.value).lower()
    
    def test_xml_sem_identificacao_levanta_erro(self):
        xml_sem_id = """<?xml version="1.0"?>
<CupomFiscal>
    <Emitente><CNPJ>123</CNPJ></Emitente>
    <Totalizadores><ValorTotal>10.00</ValorTotal></Totalizadores>
</CupomFiscal>"""
        with pytest.raises(XMLStructureError) as exc_info:
            parse_xml_cupom_fiscal(xml_sem_id)
        assert "Identificacao" in str(exc_info.value)
    
    def test_xml_sem_emitente_levanta_erro(self):
        xml_sem_emit = """<?xml version="1.0"?>
<CupomFiscal>
    <Identificacao><Numero>123</Numero><DataEmissao>2026-09-15</DataEmissao></Identificacao>
    <Totalizadores><ValorTotal>10.00</ValorTotal></Totalizadores>
</CupomFiscal>"""
        with pytest.raises(XMLStructureError) as exc_info:
            parse_xml_cupom_fiscal(xml_sem_emit)
        assert "Emitente" in str(exc_info.value)
    
    def test_xml_sem_totalizadores_levanta_erro(self):
        xml_sem_tot = """<?xml version="1.0"?>
<CupomFiscal>
    <Identificacao><Numero>123</Numero><DataEmissao>2026-09-15</DataEmissao></Identificacao>
    <Emitente><CNPJ>123</CNPJ></Emitente>
</CupomFiscal>"""
        with pytest.raises(XMLStructureError) as exc_info:
            parse_xml_cupom_fiscal(xml_sem_tot)
        assert "Totalizadores" in str(exc_info.value)
    
    def test_xml_sem_valortotal_levanta_erro(self):
        xml_sem_vtotal = """<?xml version="1.0"?>
<CupomFiscal>
    <Identificacao><Numero>123</Numero><DataEmissao>2026-09-15</DataEmissao></Identificacao>
    <Emitente><CNPJ>123</CNPJ></Emitente>
    <Totalizadores><ValorDesconto>0.00</ValorDesconto></Totalizadores>
</CupomFiscal>"""
        with pytest.raises(XMLStructureError) as exc_info:
            parse_xml_cupom_fiscal(xml_sem_vtotal)
        assert "ValorTotal" in str(exc_info.value)


class TestParseFile:
    """Testes para parse_xml_file"""
    
    def test_parse_xml_file_sucesso(self, tmp_path):
        file_path = tmp_path / "cupom_teste.xml"
        file_path.write_text(XML_CT001, encoding="utf-8")
        
        result = parse_xml_file(str(file_path))
        
        assert isinstance(result, CupomFiscalParsed)
        assert result.numero == "000123"
    
    def test_parse_xml_file_nao_encontrado(self):
        with pytest.raises(XMLStructureError) as exc_info:
            parse_xml_file("/caminho/inexistente/cupom.xml")
        assert "não encontrado" in str(exc_info.value).lower()


class TestCasosEdge:
    """Testes para casos edge e variações de formato"""
    
    def test_valores_com_virgula_decimal(self):
        xml_com_virgula = """<?xml version="1.0"?>
<CupomFiscal>
    <Identificacao><Numero>123</Numero><DataEmissao>2026-09-15</DataEmissao></Identificacao>
    <Emitente><CNPJ>12345678000195</CNPJ></Emitente>
    <Totalizadores><ValorTotal>55,30</ValorTotal><ValorDesconto>5,00</ValorDesconto></Totalizadores>
    <Detalhes/>
    <Pagamentos><FormaPagamento><Tipo>Dinheiro</Tipo><Valor>55,30</Valor></FormaPagamento></Pagamentos>
</CupomFiscal>"""
        
        result = parse_xml_cupom_fiscal(xml_com_virgula)
        assert result.total == Decimal("55.30")
        assert result.descuentoTotal == Decimal("5.00")
        assert result.pagos[0].valor == Decimal("55.30")
    
    def test_apenas_data_sem_hora(self):
        xml_sem_hora = """<?xml version="1.0"?>
<CupomFiscal>
    <Identificacao><Numero>123</Numero><DataEmissao>2026-09-15</DataEmissao></Identificacao>
    <Emitente><CNPJ>12345678000195</CNPJ></Emitente>
    <Totalizadores><ValorTotal>10.00</ValorTotal></Totalizadores>
    <Detalhes/>
    <Pagamentos><FormaPagamento><Tipo>Dinheiro</Tipo><Valor>10.00</Valor></FormaPagamento></Pagamentos>
</CupomFiscal>"""
        
        result = parse_xml_cupom_fiscal(xml_sem_hora)
        assert result.fecha == "2026-09-15"
    
    def test_multiplas_formas_pagamento(self):
        xml_multi_pag = """<?xml version="1.0"?>
<CupomFiscal>
    <Identificacao><Numero>123</Numero><DataEmissao>2026-09-15</DataEmissao></Identificacao>
    <Emitente><CNPJ>12345678000195</CNPJ></Emitente>
    <Totalizadores><ValorTotal>100.00</ValorTotal></Totalizadores>
    <Detalhes/>
    <Pagamentos>
        <FormaPagamento><Tipo>Dinheiro</Tipo><Valor>50.00</Valor></FormaPagamento>
        <FormaPagamento><Tipo>Cartao Credito</Tipo><Valor>50.00</Valor></FormaPagamento>
    </Pagamentos>
</CupomFiscal>"""
        
        result = parse_xml_cupom_fiscal(xml_multi_pag)
        assert len(result.pagos) == 2
        assert result.pagos[0].tipo == "Dinheiro"
        assert result.pagos[0].valor == Decimal("50.00")
        assert result.pagos[1].tipo == "Cartao Credito"
        assert result.pagos[1].valor == Decimal("50.00")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])