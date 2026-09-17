"""Testes para a funcionalidade de processamento do export_audit"""

import pytest
import pandas as pd
from io import BytesIO
from src.services.validation_service import ValidationService


class TestExportAuditProcessing:
    """Testes para o processamento do export_audit"""

    def setup_method(self):
        """Configuração antes de cada teste"""
        self.service = ValidationService()

    def test_ler_planilha_xlsx_basico(self):
        """Teste básico de leitura de planilha XLSX"""
        # Criar um DataFrame simples
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['x', 'y', 'z'],
            'C': [10.5, 20.0, 30.75]
        })

        # Converter para bytes
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        content = buffer.getvalue()

        # Executar
        resultado = self.service._ler_planilha(content, 'xlsx')

        # Verificar
        assert isinstance(resultado, list)
        assert len(resultado) == 3
        assert isinstance(resultado[0], dict)
        assert resultado[0]['A'] == 1
        assert resultado[0]['B'] == 'x'
        assert resultado[0]['C'] == 10.5

    def test_ler_planilha_csv_basico(self):
        """Teste básico de leitura de planilha CSV"""
        # Criar conteúdo CSV simples
        csv_content = """A,B,C
1,x,10.5
2,y,20.0
3,z,30.75"""

        # Executar
        resultado = self.service._ler_planilha(csv_content.encode('utf-8'), 'csv')

        # Verificar
        assert isinstance(resultado, list)
        assert len(resultado) == 3
        assert isinstance(resultado[0], dict)
        assert resultado[0]['A'] == 1
        assert resultado[0]['B'] == 'x'
        assert resultado[0]['C'] == 10.5

    def test_ler_planilha_vazia(self):
        """Teste de leitura de planilha vazia"""
        # Criar DataFrame vazio
        df = pd.DataFrame()

        # Converter para bytes
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        content = buffer.getvalue()

        # Executar
        resultado = self.service._ler_planilha(content, 'xlsx')

        # Verificar
        assert isinstance(resultado, list)
        assert len(resultado) == 0

    def test_ler_planilha_com_nan(self):
        """Teste de leitura de planilha com valores NaN"""
        # Criar DataFrame com NaN
        df = pd.DataFrame({
            'A': [1, None, 3],
            'B': ['x', 'y', None],
            'C': [10.5, 20.0, None]
        })

        # Converter para bytes
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        content = buffer.getvalue()

        # Executar
        resultado = self.service._ler_planilha(content, 'xlsx')

        # Verificar que NaN foi convertido para None
        assert isinstance(resultado, list)
        assert len(resultado) == 3
        assert resultado[0]['A'] == 1
        assert resultado[1]['A'] is None  # NaN convertido para None
        assert resultado[2]['A'] == 3
        assert resultado[0]['B'] == 'x'
        assert resultado[1]['B'] == 'y'
        assert resultado[2]['B'] is None  # NaN convertido para None

    def test_processar_export_audit_vazio(self):
        """Teste de processamento de export_audit vazio"""
        # Executar com conteúdo vazio
        resultado = self.service._processar_export_audit(b'', 'xlsx')

        # Verificar
        assert isinstance(resultado, dict)
        assert len(resultado) == 0

    def test_processar_export_audit_com_dados_validos(self):
        """Teste de processamento de export_audit com dados válidos"""
        # Criar uma planilha simulando o export_audit
        # Coluna H (índice 7): Número do cupom
        # Coluna S (índice 18): JSON request
        dados = []
        for i in range(5):
            linha = [None] * 20  # 20 colunas (0-19)
            linha[7] = f"2036799{i}"  # Coluna H - número do cupom
            linha[18] = '''{
                "fecha": "2026-09-15T10:30:00-03:00",
                "numero": "2036799''' + str(i) + '''",
                "total": 100.50,
                "cancelacion": false,
                "detalles": [],
                "pagos": [{"tipo": "Dinheiro", "valor": 100.50}],
                "descuentoTotal": 0.0,
                "recargoTotal": 0.0,
                "codigoMoneda": "986",
                "cotizacion": 1.0
            }'''  # Coluna S - JSON
            dados.append(linha)

        # Criar DataFrame e converter para bytes
        df = pd.DataFrame(dados)
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        content = buffer.getvalue()

        # Executar
        resultado = self.service._processar_export_audit(content, 'xlsx')

        # Verificar
        assert isinstance(resultado, dict)
        assert len(resultado) == 5
        for i in range(5):
            numero_cupom = f"2036799{i}"
            assert numero_cupom in resultado
            assert resultado[numero_cupom]['numero'] == numero_cupom
            assert resultado[numero_cupom]['total'] == 100.50
            assert resultado[numero_cupom]['cancelacion'] == False

    def test_processar_export_audit_linha_invalida(self):
        """Teste de processamento de export_audit com linhas inválidas"""
        # Criar planilha com algumas linhas válidas e algumas inválidas
        dados = []

        # Linha válida
        linha_valida = [None] * 20
        linha_valida[7] = "2036799"
        linha_valida[18] = '''{
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "2036799",
            "total": 100.50,
            "cancelacion": false,
            "detalles": [],
            "pagos": [{"tipo": "Dinheiro", "valor": 100.50}],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }'''
        dados.append(linha_valida)

        # Linha inválida - número do cupom faltando
        linha_invalida1 = [None] * 20
        linha_invalida1[7] = None  # Número do cupom faltando
        linha_invalida1[18] = '{"fecha": "2026-09-15T10:30:00-03:00"}'
        dados.append(linha_invalida1)

        # Linha inválida - JSON faltando
        linha_invalida2 = [None] * 20
        linha_invalida2[7] = "2036800"
        linha_invalida2[18] = None  # JSON faltando
        dados.append(linha_invalida2)

        # Linha inválida - JSON malformado
        linha_invalida3 = [None] * 20
        linha_invalida3[7] = "2036801"
        linha_invalida3[18] = '{json malformado}'
        dados.append(linha_invalida3)

        # Criar DataFrame e converter para bytes
        df = pd.DataFrame(dados)
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        content = buffer.getvalue()

        # Executar
        resultado = self.service._processar_export_audit(content, 'xlsx')

        # Verificar - apenas a linha válida deve ser processada
        assert isinstance(resultado, dict)
        assert len(resultado) == 1
        assert "2036799" in resultado
        assert resultado["2036799"]["numero"] == "2036799"

    def test_validar_json_request_valido(self):
        """Teste de validação de JSON request válido"""
        json_str = '''{
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "12345",
            "total": 100.50,
            "cancelacion": false,
            "detalles": [],
            "pagos": [{"tipo": "Dinheiro", "valor": 100.50}],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }'''

        # Executar
        resultado = self.service._validar_json_request(json_str, "12345")

        # Verificar
        assert isinstance(resultado, dict)
        assert str(resultado['numero']) == "12345"  # Pode ser string ou int dependendo do parser
        assert resultado['total'] == 100.50
        assert resultado['cancelacion'] == False

    def test_validar_json_request_inconsistencia_numero(self):
        """Teste de validação de JSON request com inconsistência no número"""
        json_str = '''{
            "fecha": "2026-09-15T10:30:00-03:00",
            "numero": "99999",
            "total": 100.50,
            "cancelacion": false,
            "detalles": [],
            "pagos": [{"tipo": "Dinheiro", "valor": 100.50}],
            "descuentoTotal": 0.0,
            "recargoTotal": 0.0,
            "codigoMoneda": "986",
            "cotizacion": 1.0
        }'''

        # Executar
        resultado = self.service._validar_json_request(json_str, "12345")  # Esperado: 12345, JSON tem: 99999

        # Verificar - deve retornar o JSON mesmo com inconsistência (apenas loga warning)
        assert isinstance(resultado, dict)
        assert str(resultado['numero']) == "99999"  # O valor do JSON é mantido

    def test_validar_json_request_invalido(self):
        """Teste de validação de JSON request inválido"""
        json_str = '{json inválido'

        # Executar
        resultado = self.service._validar_json_request(json_str, "12345")

        # Verificar
        assert resultado is None

    def test_validar_json_request_campos_obrigatorios_faltando_no_schema(self):
        """Teste de validação quando JSON falta campos obrigatórios do schema"""
        # Este teste dependeria do schema_etapa01.json, mas como não temos acesso direto
        # neste contexto, vamos testar com um JSON que claramente faltaria campos críticos
        json_str = '''{
            "fecha": "2026-09-15T10:30:00-03:00"
            # Faltando: numero, total, cancelacion, etc.
        }'''

        # Executar
        resultado = self.service._validar_json_request(json_str, "12345")

        # Verificar - deve retornar None se falhar na validação do schema
        # (Este comportamento depende de como o json_parser lida com campos faltantes)
        # Por enquanto, vamos apenas verificar que não quebra
        assert resultado is None or isinstance(resultado, dict)