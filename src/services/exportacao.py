import pandas as pd
import json
from io import BytesIO, StringIO
import base64
from datetime import datetime

def exportar_resultados(df: pd.DataFrame, formato: str = "csv") -> bytes:
    """
    Exporta DataFrame de resultados para diversos formatos.
    
    Args:
        df: DataFrame com os resultados da validação
        formato: Formato de exportação ('csv', 'json', 'xlsx', 'html', 'markdown')
        
    Returns:
        Bytes contendo o arquivo exportado
    """
    formato = formato.lower()
    
    if formato == "csv":
        return df.to_csv(index=False).encode('utf-8')
    
    elif formato == "json":
        return df.to_json(orient='records', force_ascii=False, indent=2).encode('utf-8')
    
    elif formato == "xlsx":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')
        return output.getvalue()
    
    elif formato == "html":
        # Gerar HTML estilizado
        html_str = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resultado da Validação - Dikē</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .status-aprovado {{ color: #27ae60; font-weight: bold; }}
                .status-falha-leve {{ color: #f39c12; font-weight: bold; }}
                .status-falha-mediana {{ color: #e67e22; font-weight: bold; }}
                .status-falha-grave {{ color: #e74c3c; font-weight: bold; }}
                .status-impossivel {{ color: #95a5a6; font-weight: bold; }}
                .severidade-nenhuma {{ color: #27ae60; }}
                .severidade-leve {{ color: #f39c12; }}
                .severidade-mediana {{ color: #e67e22; }}
                .severidade-grave {{ color: #e74c3c; }}
                .severidade-gravissima {{ color: #8e44ad; }}
                .footer {{ margin-top: 30px; font-size: 0.9em; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <h1>Resultado da Validação - Dikē</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            {df.to_html(index=False, escape=False, classes='resultado-table')}
            <div class="footer">
                Relatório gerado pelo Dikē - Validador API Scanntech 3.0
            </div>
        </body>
        </html>
        """
        return html_str.encode('utf-8')
    
    elif formato == "markdown":
        # Gerar tabela Markdown
        md_str = f"# Resultado da Validação - Dikē\n\n"
        md_str += f"*Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n\n"
        md_str += df.to_markdown(index=False)
        md_str += "\n\n---\n*Relatório gerado pelo Dikē - Validador API Scanntech 3.0*"
        return md_str.encode('utf-8')
    
    else:
        raise ValueError(f"Formato não suportado: {formato}. Use: csv, json, xlsx, html ou markdown")

def gerar_relatorio_resumido(df: pd.DataFrame, formato: str = "html") -> bytes:
    """
    Gera um relatório resumido com estatísticas da validação.
    
    Args:
        df: DataFrame com os resultados da validação
        formato: Formato de exportação ('html' ou 'markdown')
        
    Returns:
        Bytes contendo o relatório resumido
    """
    formato = formato.lower()
    
    # Estatísticas
    total = len(df)
    aprovados = len(df[df['Status'] == 'Aprovado']) if 'Status' in df.columns else 0
    falhas = total - aprovados
    
    if 'Severidade' in df.columns:
        severidade_counts = df['Severidade'].value_counts().to_dict()
    else:
        severidade_counts = {}
    
    if formato == "html":
        html_str = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório Resumido - Dikē</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #2c3e50; }}
                .stats-container {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{
                    border: 1px solid #bdc3c7;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                    min-width: 120px;
                }}
                .stat-number {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
                .stat-label {{ font-size: 0.9em; color: #7f8c8d; }}
                .aprovado {{ border-color: #27ae60; }}
                .aprovado .stat-number {{ color: #27ae60; }}
                .falha {{ border-color: #e74c3c; }}
                .falha .stat-number {{ color: #e74c3c; }}
                .footer {{ margin-top: 30px; font-size: 0.9em; color: #7f8c8d; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>📊 Relatório Resumido da Validação</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>

            <div class="stats-container">
                <div class="stat-box aprovado">
                    <div class="stat-number">{aprovados}</div>
                    <div class="stat-label">Aprovados</div>
                </div>
                <div class="stat-box falha">
                    <div class="stat-number">{falhas}</div>
                    <div class="stat-label">Falhas</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">Total</div>
                </div>
            </div>

            <h2>Distribuição por Severidade</h2>
            <ul>
        """

        for severidade, count in severidade_counts.items():
            cor = {
                'Nenhuma': '#27ae60',
                'Leve': '#f39c12',
                'Mediana': '#e67e22',
                'Grave': '#e74c3c',
                'Gravíssima': '#8e44ad'
            }.get(severidade, '#95a5a6')

            html_str += f'<li><strong style="color: {cor};">{severidade}:</strong> {count}</li>\n'

        html_str += f"""
            </ul>
            <div class="footer">
                Relatório gerado pelo Dikē - Validador API Scanntech 3.0
            </div>
        </body>
        </html>
        """
        return html_str.encode('utf-8')
    
    elif formato == "markdown":
        md_str = f"# 📊 Relatório Resumido da Validação\n\n"
        md_str += f"*Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n\n"
        md_str += f"## Estatísticas Gerais\n\n"
        md_str += f"- **Aprovados:** {aprovados}\n"
        md_str += f"- **Falhas:** {falhas}\n"
        md_str += f"- **Total:** {total}\n\n"

        md_str += f"## Distribuição por Severidade\n\n"
        for severidade, count in severidade_counts.items():
            md_str += f"- **{severidade}:** {count}\n"

        md_str += f"\n---\n*Relatório gerado pelo Dikē - Validador API Scanntech 3.0*"
        return md_str.encode('utf-8')
    
    else:
        raise ValueError(f"Formato não suportado para relatório resumido: {formato}. Use: html ou markdown")