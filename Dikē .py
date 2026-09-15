import streamlit as st
import pandas as pd
import os
from src.services.validation_service import ValidationService
from src.services.exportacao import exportar_resultados

def main():
    st.set_page_config(
        page_title="Dikē - Validador API Scanntech 3.0",
        page_icon="⚖️",
        layout="wide"
    )

    st.title("⚖️ Dikē - Validador API Scanntech 3.0")
    st.markdown("---")

    # Zona de upload em 3 colunas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📋 Roteiro de Testes")
        uploaded_roteiro = st.file_uploader(
            "Selecione o roteiro (XLSX/CSV)",
            type=["xlsx", "csv"],
            key="roteiro_uploader"
        )
        if uploaded_roteiro is not None:
            st.success(f"Roteiro carregado: {uploaded_roteiro.name}")

    with col2:
        st.subheader("🧾 Cupons Fiscais")
        uploaded_cupons = st.file_uploader(
            "Selecione os cupons (XML/PDF/JPEG)",
            type=["xml", "pdf", "jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="cupons_uploader"
        )
        if uploaded_cupons:
            st.success(f"{len(uploaded_cupons)} cupom(ns) carregado(s)")

    with col3:
        st.subheader("📡 JSON da API")
        uploaded_json = st.file_uploader(
            "Selecione o payload JSON",
            type=["json"],
            key="json_uploader"
        )
        if uploaded_json is not None:
            st.success(f"JSON carregado: {uploaded_json.name}")

    st.markdown("---")

    # Botão de início
    if st.button("🚀 Iniciar Validação", type="primary", use_container_width=True):
        # Verificar se todos os arquivos foram carregados
        if not uploaded_roteiro or not uploaded_cupons or not uploaded_json:
            st.error("Por favor, carregue todos os arquivos necessários (roteiro, cupons e JSON).")
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
            "Gerando relatório de resultados..."
        ]

        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) * 20)  # 20% por passo
            # Em uma implementação real, aqui seria chamada a lógica de processamento
            # Por enquanto, apenas simulamos delay
            import time
            time.sleep(0.5)

        status_text.text("✅ Validação concluída!")
        progress_bar.progress(100)

        # Processar os arquivos usando o novo serviço de validação
        validation_service = ValidationService()
        
        # Ler o conteúdo dos arquivos
        roteiro_content = uploaded_roteiro.getvalue()
        cupons_content = [cupom.getvalue() for cupom in uploaded_cupons]
        json_content = uploaded_json.getvalue()
        
        # Executar a validação
        resultados, erros = validation_service.validar_arquivos(
            roteiro_content, cupons_content, json_content
        )
        
        # Exibir eventuais erros de processamento
        if erros:
            st.error("Erros durante o processamento:")
            for erro in erros:
                st.write(f"- {erro}")

        # Exibir resultados
        st.markdown("---")
        st.subheader("📊 Resultados da Validação")

        # Converter resultados para DataFrame para exibição
        if resultados:
            resultados_df = pd.DataFrame(resultados)
            
            st.dataframe(
                resultados_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Aprovado", "Falha Leve", "Falha Mediana", "Falha Grave", "Impossível Validar"],
                        required=True,
                    ),
                    "Severidade": st.column_config.SelectboxColumn(
                        "Severidade",
                        options=["Nenhuma", "Leve", "Mediana", "Grave", "Gravíssima"],
                        required=True,
                    )
                }
            )
        else:
            st.warning("Nenhum resultado de validação para exibir.")

        # Botões de exportação
        st.markdown("---")
        col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)

        # Preparar dados para exportação (mesmo formato de antes)
        if 'resultados_df' in locals() and not resultados_df.empty:
            df_para_exportacao = resultados_df
        else:
            # Criar DataFrame vazio com as colunas esperadas para evitar erros
            df_para_exportacao = pd.DataFrame(columns=[
                "ID Teste", "Cupom Ref", "Status", "Descrição", "Severidade"
            ])

        with col_exp1:
            if st.button("📥 Exportar CSV", use_container_width=True):
                csv_data = exportar_resultados(df_para_exportacao, formato="csv")
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="resultado_validacao.csv",
                    mime="text/csv"
                )

        with col_exp2:
            if st.button("📥 Exportar JSON", use_container_width=True):
                json_data = exportar_resultados(df_para_exportacao, formato="json")
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="resultado_validacao.json",
                    mime="application/json"
                )

        with col_exp3:
            if st.button("📥 Exportar XLSX", use_container_width=True):
                xlsx_data = exportar_resultados(df_para_exportacao, formato="xlsx")
                st.download_button(
                    label="Download XLSX",
                    data=xlsx_data,
                    file_name="resultado_validacao.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        with col_exp4:
            if st.button("📥 Exportar HTML", use_container_width=True):
                html_data = exportar_resultados(df_para_exportacao, formato="html")
                st.download_button(
                    label="Download HTML",
                    data=html_data,
                    file_name="resultado_validacao.html",
                    mime="text/html"
                )

if __name__ == "__main__":
    main()
