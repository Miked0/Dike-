# Dikē - Validador API Scanntech 3.0

> Dikē, na mitologia grega, é a deusa da justiça e do julgamento correto. Este projeto carrega seu nome como símbolo de precisão e equidade na validação de dados.

## 📋 Descrição

Dikē é uma aplicação Streamlit projetada para validar respostas de API contra roteiros de testes e cupons fiscais, garantindo conformidade com os padrões da Scanntech 3.0.

## 👥 Desenvolvimento com Agentes Especializados

Este projeto utiliza uma abordagem de desenvolvimento com agentes especializados, cada um com responsabilidades bem definidas:

- **PO (Mike) - Orquestrador**: Visão geral do projeto, priorização de demandas, alinhamento de escopo, delegação de tarefas e validação final
- **Planejador (Atlas)**: Transforma demandas em tarefas executáveis, define critérios de aceite e estima complexidade
- **QA (Vega)**: Revisão de roteiros de teste, validação de cenários, análise de JSONs/XMLs e conferência de regras de negócio
- **Dev Backend (Orion)**: Implementação de scripts Python, automações e integrações
- **DevOps/Suporte (Lynx)**: Apoio em infraestrutura leve, documentação técnica e validação de ambientes

Consulte o [WORKSPACE_GUIDE.md](WORKSPACE_GUIDE.md) para detalhes completos sobre a estrutura de trabalho com agentes.

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
├── main.py                 # ou Dikē .py - Aplicação Streamlit principal
├── README.md               # Este arquivo
├── WORKSPACE_GUIDE.md      # Guia da estrutura de trabalho com agentes
├── .claude/                # Configurações e kanbans dos agentes
│   └── agents/
│       ├── po_kanban.md           # Kanban do PO/Orquestrador
│       ├── planejador_kanban.md   # Kanban do Planejador
│       ├── qa_kanban.md           # Kanban do QA
│       ├── dev_kanban.md          # Kanban do Desenvolvedor Backend
│       └── devops_kanban.md       # Kanban do DevOps/Suporte
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
   ou
   ```bash
   streamlit run Dikē .py
   ```

## 📝 Licença

Este projeto está sob a licença MIT.

---

*Named after Dikē, the Greek goddess of justice, embodying fairness and correctness in data validation.*