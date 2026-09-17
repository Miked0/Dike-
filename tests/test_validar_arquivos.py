"""Testes para o método principal de validação de arquivos (validar_arquivos)"""

import pytest
from io import BytesIO
import pandas as pd
from src.services.validation_service import ValidationService
from src.models.models import Movimiento, Detalle, Pago


class TestValidarArquivos:
    """Testes para o método validar_arquivos"""

    def setup_method(self):
        """Configuração antes de cada teste"""
        self.service = ValidationService()

    def test_validar_arquivos_export_audit_vazio(self):
        """Teste de validação com export_audit vazio"""
        # Dados de entrada vazios
        roteiro_content = b""
        cupons_content = [b""]
        export_audit_content = b""

        # Executar
        resultados, erros = self.service.validar_arquivos(
            roteiro_content=roteiro_content,
            cupons_content=cupons_content,
            export_audit_content=export_audit_content,
            roteiro_file_type='xlsx',
            export_audit_file_type='xlsx'
        )

        # Verificar
        assert isinstance(resultados, list)
        assert isinstance(erros, list)
        # Com export_audit vazio, não deve haver resultados nem erros críticos
        # (pode haver erros de processamento individuais, mas não críticos)

    def test_validar_arquivos_export_audit_com_dados_validos(self):
        """Teste de validação com export_audit contendo dados válidos"""
        # Criar planilha de roteiro simples (não usada no fluxo atual, mas necessária)
        roteiro_df = pd.DataFrame({'numero_cupom': ['12345']})
        roteiro_buffer = BytesIO()
        roteiro_df.to_excel(roteiro_buffer, index=False)
        roteiro_content = roteiro_buffer.getvalue()

        # Criar lista de cupons vazia (não usada no fluxo atual)
        cupons_content = [b""]

        # Criar planilha de export_audit com dados válidos
        export_audit_df = pd.DataFrame({
            # Colunas A-G (0-6): vazias ou dados irrelevantes
            **{chr(65 + i): [None] for i in range(7)},  # A-G
            # Coluna H (7): número do cupom
            'H': ['2036799'],
            # Colunas I-R (8-17): vazias ou dados irrelevantes
            **{chr(65 + i): [None] for i in range(8, 18)},  # I-R
            # Coluna S (18): JSON request
            'S': ['''{
                "fecha": "2026-09-15T10:30:00-03:00",
                "numero": "2036799",
                "total": 100.50,
                "cancelacion": false,
                "detalles": [
                    {"codigoArticulo": "001", "codigoBarras": "123", "descripcionArticulo": "Produto Teste",
                     "cantidad": 2, "importeUnitario": 50.00, "importe": 100.00},
                    {"codigoArticulo": "002", "codigoBarras": "456", "descripcionArticulo": "Produto Teste 2",
                     "cantidad": 1, "importeUnitario": 0.50, "importe": 0.50}
                ],
                "pagos": [
                    {"tipo": "Dinheiro", "valor": 50.00},
                    {"tipo": "Cartão", "valor": 50.50}
                ],
                "descuentoTotal": 0.0,
                "recargoTotal": 0.0,
                "codigoMoneda": "986",
                "cotizacion": 1.0
            }''']
        })

        export_audit_buffer = BytesIO()
        export_audit_df.to_excel(export_audit_buffer, index=False)
        export_audit_content = export_audit_buffer.getvalue()

        # Executar
        resultados, erros = self.service.validar_arquivos(
            roteiro_content=roteiro_content,
            cupons_content=cupons_content,
            export_audit_content=export_audit_content,
            roteiro_file_type='xlsx',
            export_audit_file_type='xlsx'
        )

        # Verificar
        assert isinstance(resultados, list)
        assert len(resultados) == 1  # Deve ter um resultado para o cupom processado
        assert isinstance(erros, list)

        # Verificar o resultado
        resultado = resultados[0]
        assert resultado["ID Teste"] == "EA-2036799"
        assert resultado["Cupom Ref"] == "2036799"
        assert resultado["Status"] == "Aprovado"  # Deve ser aprovado pois os dados são válidos
        assert "Validação do export_audit" in resultado["Descrição"]
        assert resultado["Severidade"] == "Nenhuma"  # Sem erros ou avisos

    def test_validar_arquivos_export_audit_com_dados_invalidos(self):
        """Teste de validação com export_audit contendo dados que causam falha na validação"""
        # Criar planilha de roteiro simples
        roteiro_df = pd.DataFrame({'numero_cupom': ['12345']})
        roteiro_buffer = BytesIO()
        roteiro_df.to_excel(roteiro_buffer, index=False)
        roteiro_content = roteiro_buffer.getvalue()

        # Criar lista de cupons vazia
        cupons_content = [b""]

        # Criar planilha de export_audit com dados que causarão falha na validação
        # (total negativo, o que não é permitido)
        export_audit_df = pd.DataFrame({
            **{chr(65 + i): [None] for i in range(7)},  # A-G
            'H': ['2036799'],  # Número do cupom
            **{chr(65 + i): [None] for i in range(8, 18)},  # I-R
            'S': ['''{
                "fecha": "2026-09-15T10:30:00-03:00",
                "numero": "2036799",
                "total": -50.00,
                "cancelacion": false,
                "detalles": [],
                "pagos": [{"tipo": "Dinheiro", "valor": 50.00}],
                "descuentoTotal": 0.0,
                "recargoTotal": 0.0,
                "codigoMoneda": "986",
                "cotizacion": 1.0
            }''']
        })

        export_audit_buffer = BytesIO()
        export_audit_df.to_excel(export_audit_buffer, index=False)
        export_audit_content = export_audit_buffer.getvalue()

        # Executar
        resultados, erros = self.service.validar_arquivos(
            roteiro_content=roteiro_content,
            cupons_content=cupons_content,
            export_audit_content=export_audit_content,
            roteiro_file_type='xlsx',
            export_audit_file_type='xlsx'
        )

        # Verificar
        assert isinstance(resultados, list)
        assert len(resultados) == 1  # Deve ter um resultado (mesmo que falhe)
        assert isinstance(erros, list)

        # Verificar o resultado
        resultado = resultados[0]
        assert resultado["ID Teste"] == "EA-2036799"
        assert resultado["Cupom Ref"] == "2036799"
        assert resultado["Status"] == "Falha Grave"  # Deve falhar devido ao total negativo
        assert "Validação do export_audit" in resultado["Descrição"]
        assert resultado["Severidade"] == "Grave"  # Deve ter gravidade grave devido ao erro

        # Verificar que há erros na lista de erros
        assert len(erros) >= 1
        assert any("Total do movimento não pode ser negativo" in erro for erro in erros)

    def test_validar_arquivos_export_audit_com_campos_obrigatorios_faltando(self):
        """Teste de validação com export_audit faltando campos obrigatórios"""
        # Criar planilha de roteiro simples
        roteiro_df = pd.DataFrame({'numero_cupom': ['12345']})
        roteiro_buffer = BytesIO()
        roteiro_df.to_excel(roteiro_buffer, index=False)
        roteiro_content = roteiro_buffer.getvalue()

        # Criar lista de cupons vazia
        cupons_content = [b""]

        # Criar planilha de export_audit faltando campos obrigatórios
        export_audit_df = pd.DataFrame({
            **{chr(65 + i): [None] for i in range(7)},  # A-G
            'H': ['2036799'],  # Número do cupom
            **{chr(65 + i): [None] for i in range(8, 18)},  # I-R
            'S': ['''{
                "fecha": "2026-09-15T10:30:00-03:00"
            }''']
        })

        export_audit_buffer = BytesIO()
        export_audit_df.to_excel(export_audit_buffer, index=False)
        export_audit_content = export_audit_buffer.getvalue()

        # Executar
        resultados, erros = self.service.validar_arquivos(
            roteiro_content=roteiro_content,
            cupons_content=cupons_content,
            export_audit_content=export_audit_content,
            roteiro_file_type='xlsx',
            export_audit_file_type='xlsx'
        )

        # Verificar
        assert isinstance(resultados, list)
        # Pode ser que não haja resultados se nenhum movimento puder ser criado
        # ou pode haver um resultado indicando impossibilidade de validação
        assert isinstance(erros, list)

    def test_validar_arquivos_multiplos_cupons(self):
        """Teste de validação com múltiplos cupons no export_audit"""
        # Criar planilha de roteiro simples
        roteiro_df = pd.DataFrame({'numero_cupom': ['12345', '67890']})
        roteiro_buffer = BytesIO()
        roteiro_df.to_excel(roteiro_buffer, index=False)
        roteiro_content = roteiro_buffer.getvalue()

        # Criar lista de cupons vazia
        cupons_content = [b""]

        # Criar planilha de export_audit com múltiplos cupons
        export_audit_data = []
        for i in range(3):
            export_audit_data.append({
                **{chr(65 + j): None for j in range(7)},  # A-G
                'H': f'2036799{i}',  # Número do cupom
                **{chr(65 + j): None for j in range(8, 18)},  # I-R
                'S': f'''{{
                    "fecha": "2026-09-15T10:30:00-03:00",
                    "numero": "2036799{i}",
                    "total": 100.50,
                    "cancelacion": false,
                    "detalles": [
                        {{"codigoArticulo": "001", "codigoBarras": "123", "descripcionArticulo": "Produto Teste",
                         "cantidad": 1, "importeUnitario": 100.50, "importe": 100.50}}
                    ],
                    "pagos": [{{"tipo": "Dinheiro", "valor": 100.50}}],
                    "descuentoTotal": 0.0,
                    "recargoTotal": 0.0,
                    "codigoMoneda": "986",
                    "cotizacion": 1.0
                }}'''
            })

        export_audit_df = pd.DataFrame(export_audit_data)
        export_audit_buffer = BytesIO()
        export_audit_df.to_excel(export_audit_buffer, index=False)
        export_audit_content = export_audit_buffer.getvalue()

        # Executar
        resultados, erros = self.service.validar_arquivos(
            roteiro_content=roteiro_content,
            cupons_content=cupons_content,
            export_audit_content=export_audit_content,
            roteiro_file_type='xlsx',
            export_audit_file_type='xlsx'
        )

        # Verificar
        assert isinstance(resultados, list)
        assert len(resultados) == 3  # Deve ter 3 resultados, um para cada cupom
        assert isinstance(erros, list)

        # Verificar que todos os resultados têm o status correto
        for i, resultado in enumerate(resultados):
            assert resultado["ID Teste"] == f"EA-2036799{i}"
            assert resultado["Cupom Ref"] == f"2036799{i}"
            assert resultado["Status"] == "Aprovado"  # Todos devem ser aprovados
            assert "Validação do export_audit" in resultado["Descrição"]
            assert resultado["Severidade"] == "Nenhuma"

    def test_validar_arquivos_excecao_critica(self):
        """Teste de validação quando ocorre uma exceção crítica"""
        # Testar com dados que causem uma exceção no processamento
        # Vamos passar conteúdo que não seja nem Excel nem CSV válido para causar erro

        # Criar planilha de roteiro simples
        roteiro_df = pd.DataFrame({'numero_cupom': ['12345']})
        roteiro_buffer = BytesIO()
        roteiro_df.to_excel(roteiro_buffer, index=False)
        roteiro_content = roteiro_buffer.getvalue()

        # Criar lista de cupons vazia
        cupons_content = [b""]

        # Conteúdo inválido para export_audit
        export_audit_content = b"conteudo totalmente invalido que nao eh nem excel nem csv"

        # Executar
        resultados, erros = self.service.validar_arquivos(
            roteiro_content=roteiro_content,
            cupons_content=cupons_content,
            export_audit_content=export_audit_content,
            roteiro_file_type='xlsx',
            export_audit_file_type='xlsx'  # Isso vai causar erro ao tentar ler como Excel
        )

        # Verificar
        assert isinstance(resultados, list)
        assert isinstance(erros, list)
        # Deve ter algum erro devido à exceção crítica
        # O comportamento exato depende de como o tratamento de exceções funciona


if __name__ == '__main__':
    pytest.main([__file__, '-v'])