# Dikē - Validador API Scanntech 3.0

> Dikē, na mitologia grega, é a deusa da justiça e do julgamento correto. Este projeto carrega seu nome como símbolo de precisão e equidade na validação de dados.

## 📋 Descrição

Dikē é uma aplicação Streamlit projetada para validar respostas de API contra roteiros de testes e cupons fiscais, garantindo conformidade com os padrões da Scanntech 3.0.

## 🚀 Funcionalidades

- Upload de roteiro de testes (XLSX/CSV)
- Upload de cupons fiscais (XML/PDF/JPEG/PNG)
- Upload de payload JSON da API
- Validação automática contra regras de negócio
- Geração de relatórios detalhados de validação
- Exportação de resultados em múltiplos formatos (CSV, JSON, XLSX, HTML)

## 📁 Estrutura do Projeto

```
projeto01/
├── main.py                 # Aplicação Streamlit principal
├── README.md               # Este arquivo
├── config/                 # Configurações e esquemas
│   └── schema_etapa01.json # Esquema de validação para Etapa 01
├── models/                 # Modelos de dados
├── parsers/                # Parsers para diferentes formatos de arquivo
├── services/               # Lógica de serviço (exportação, processamento, etc.)
├── utils/                  # Utilitários auxiliares
└── validators/             # Módulos de validação de dados
```

## 🛠️ Como Executar

1. Clone este repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```bash
   streamlit run main.py
   ```

## 📝 Licença

Este projeto está sob a licença MIT.

---

*Named after Dikē, the Greek goddess of justice, embodying fairness and correctness in data validation.*