import streamlit as st
import pandas as pd
import os
from src.services.validation_service import ValidationService
from src.services.exportacao import exportar_resultados

def main():
    st.set_page_config(
        page_title="DikÄ“ - Validador API Scanntech 3.0",
        page_icon="âš–ï¸",
        layout="wide"
    )

    st.title("âš–ï¸ DikÄ“ - Validador API Scanntech 3.0")
    st.markdown("---")

    # Zona de upload em 3 colunas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("ðŸ“‹ Roteiro de Testes")
        uploaded_roteiro = st.file_uploader(
            "Selecione o roteiro (XLSX/CSV)",
            type=["xlsx", "csv"],
            key="roteiro_uploader"
        )
        if uploaded_roteiro is not None:
            st.success(f"Roteiro carregado: {uploaded_roteiro.name}")

    with col2:
        st.subheader("ðŸ§¾ Cupons Fiscais")
        uploaded_cupons = st.file_uploader(
            "Selecione os cupons (XML/PDF/JPEG)",
            type=["xml", "pdf", "jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="cupons_uploader"
        )
        if uploaded_cupons:
            st.success(f"{len(uploaded_cupons)} cupom(ns) carregado(s)")

    with col3:
        st.subheader("ðŸ“¡ JSON da API")
        uploaded_json = st.file_uploader(
            "Selecione o payload JSON",
            type=["json"],
            key="json_uploader"
        )
        if uploaded_json is not None:
            st.success(f"JSON carregado: {uploaded_json.name}")

    st.markdown("---")

    # BotÃ£o de inÃ­cio
    if st.button("ðŸš€ Iniciar ValidaÃ§Ã£o", type="primary", use_container_width=True):
        # Verificar se todos os arquivos foram carregados
        if not uploaded_roteiro or not uploaded_cupons or not uploaded_json:
            st.error("Por favor, carregue todos os arquivos necessÃ¡rios (roteiro, cupons e JSON).")
            return

        # Barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Etapas de processamento
        steps = [
            "Carregando roteiro de testes...",
            "Processando cupons fiscais...",
            "Validando contra JSON da API...",
            "Classificando falhas...",
            "Gerando relatÃ³rio de resultados..."
        ]

        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) * 20)  # 20% por passo
            # Em uma implementaÃ§Ã£o real, aqui seria chamada a lÃ³gica de processamento
            # Por enquanto, apenas simulamos delay
            import time
            time.sleep(0.5)

        status_text.text("âœ… ValidaÃ§Ã£o concluÃ­da!")
        progress_bar.progress(100)

        # Processar os arquivos usando o novo serviÃ§o de validaÃ§Ã£o
        validation_service = ValidationService()\n\n        # Ler o conteÃºdo dos arquivos\n        roteiro_content = uploaded_roteiro.getvalue()\n        cupons_content = [cupom.getvalue() for cupom in uploaded_cupons]\n        json_content = uploaded_json.getvalue()\n\n        # Detectar o tipo de arquivo do roteiro\n        roteiro_file_type = None\n        if uploaded_roteiro.name:\n            if uploaded_roteiro.name.lower().endswith('.xlsx'):\n                roteiro_file_type = 'xlsx'\n            elif uploaded_roteiro.name.lower().endswith('.csv'):\n                roteiro_file_type = 'csv'\n\n        # Executar a validaÃ§Ã£o\n        resultados, erros = validation_service.validar_arquivos(\n            roteiro_content, cupons_content, json_content, roteiro_file_type\n        )
        
        # Exibir eventuais erros de processamento
        if erros:
            st.error("Erros durante o processamento:")
            for erro in erros:
                st.write(f"- {erro}")

        # Exibir resultados
        st.markdown("---")
        st.subheader("ðŸ“Š Resultados da ValidaÃ§Ã£o")

        # Converter resultados para DataFrame para exibiÃ§Ã£o
        if resultados:
            resultados_df = pd.DataFrame(resultados)
            
            st.dataframe(
                resultados_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Aprovado", "Falha Leve", "Falha Mediana", "Falha Grave", "ImpossÃ­vel Validar"],
                        required=True,
                    ),
                    "Severidade": st.column_config.SelectboxColumn(
                        "Severidade",
                        options=["Nenhuma", "Leve", "Mediana", "Grave", "GravÃ­ssima"],
                        required=True,
                    )
                }
            )
        else:
            st.warning("Nenhum resultado de validaÃ§Ã£o para exibir.")

        # BotÃµes de exportaÃ§Ã£o
        st.markdown("---")
        col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)

        # Preparar dados para exportaÃ§Ã£o (mesmo formato de antes)
        if 'resultados_df' in locals() and not resultados_df.empty:
            df_para_exportacao = resultados_df
        else:
            # Criar DataFrame vazio com as colunas esperadas para evitar erros
            df_para_exportacao = pd.DataFrame(columns=[
                "ID Teste", "Cupom Ref", "Status", "DescriÃ§Ã£o", "Severidade"
            ])

        with col_exp1:
            if st.button("ðŸ“¥ Exportar CSV", use_container_width=True):
                csv_data = exportar_resultados(df_para_exportacao, formato="csv")
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="resultado_validacao.csv",
                    mime="text/csv"
                )

        with col_exp2:
            if st.button("ðŸ“¥ Exportar JSON", use_container_width=True):
                json_data = exportar_resultados(df_para_exportacao, formato="json")
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="resultado_validacao.json",
                    mime="application/json"
                )

        with col_exp3:
            if st.button("ðŸ“¥ Exportar XLSX", use_container_width=True):
                xlsx_data = exportar_resultados(df_para_exportacao, formato="xlsx")
                st.download_button(
                    label="Download XLSX",
                    data=xlsx_data,
                    file_name="resultado_validacao.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        with col_exp4:
            if st.button("ðŸ“¥ Exportar HTML", use_container_width=True):
                html_data = exportar_resultados(df_para_exportacao, formato="html")
                st.download_button(
                    label="Download HTML",
                    data=html_data,
                    file_name="resultado_validacao.html",
                    mime="text/html"
                )

if __name__ == "__main__":
    main()

