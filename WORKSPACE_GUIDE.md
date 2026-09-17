# Workspace de Desenvolvimento - Projeto Dikē

Este documento descreve a estrutura de trabalho com agentes especializados para o desenvolvimento do projeto Dikē - Validador API Scanntech 3.0.

## Estrutura de Agentes

### Agentes Free-claude (Maestri) - Modelo fcc-claude padrão

#### PO (Mike) - Orquestrador
- **Responsabilidade:** Visão geral do projeto, priorização de demandas, alinhamento de escopo, delegação de tarefas, validação final de entregas
- **Kanban:** `.claude/agents/po_kanban.md` - Kanban macro do projeto (épicos, frentes, prioridades)
- **Localização:** Trabalha em nível estratégico, mantendo visão do produto completo

#### Planejador (Atlas)
- **Responsabilidade:** Transformar demandas em tarefas executáveis, definir critérios de aceite, estimar complexidade, sugerir ordem de execução
- **Kanban:** `.claude/agents/planejador_kanban.md` - Kanban de refinamento e planejamento (backlog, tarefas em definição, pronto para desenvolvimento)
- **Localização:** Trabalha em conjunto com o PO para refinar o backlog

### Agentes Hermes (Terminal) - Modelo nemotron-3-120b

#### QA (Vega) - perfil: projeto01-qa
- **Responsabilidade:** Revisão de roteiros de teste, validação de cenários, análise de JSONs/XMLs, conferência de regras de negócio, validação de saídas de automação
- **Kanban:** `.claude/agents/qa_kanban.md` - Kanban de testes (cenários a validar, bugs encontrados, cenários cobertos, pendências de teste)
- **Localização:** Terminal dedicado ao QA

#### Python / Automação / Backend (Orion) - perfil: projeto01-dev
- **Responsabilidade:** Implementação de scripts Python, automações, integrações, manipulação de arquivos (JSON, XML, CSV), chamadas a APIs, estruturação de módulos do projeto
- **Kanban:** `.claude/agents/dev_kanban.md` - Kanban de desenvolvimento (features, refatorações, correções)
- **Localização:** Terminal dedicado ao desenvolvimento backend
- **Restrições:** 
  - Deve seguir a estrutura de pastas já existente do projeto01
  - Evitar criar subpastas infinitas
  - Novas pastas somente com justificativa clara de organização e reaproveitamento
  - Trabalhar diretamente na estrutura disponível

#### DevOps / Suporte (Lynx) - perfil: projeto01-dev ou genérico de suporte
- **Responsabilidade:** Apoio em tarefas de infraestrutura leve (configuração, scripts auxiliares, validação de ambientes, documentação técnica, ajustes de scripts de execução)
- **Kanban:** `.claude/agents/devops_kanban.md` - Kanban de tarefas de apoio e infraestrutura leve
- **Localização:** Terminal dedicado ao DevOps/Suporte
- **Funções adicionais:**
  - Backup de Orion em tarefas de desenvolvimento
  - Apoio ao QA em cenários de teste técnicos (preparar massa de dados, rodar scripts de validação em lote)

## Regras de Arquitetura e Operação

### Estrutura de Pastas
Todos os agentes devem seguir a estrutura existente:
```
projeto01/
├── main.py                 # ou Dikē .py - Aplicação Streamlit principal
├── README.md
├── config/                 # Configurações e esquemas
│   └── schema_etapa01.json
├── models/                 # Modelos de dados
├── parsers/                # Parsers para diferentes formatos de arquivo
├── services/               # Lógica de serviço
├── utils/                  # Utilitários auxiliares
└── validators/             # Módulos de validação de dados
```

### Princípios de Trabalho
1. **Evitar subpastas infinitas:** Novas pastas somente quando houver clara necessidade de separação de responsabilidades e reaproveitamento
2. **Coerência:** Manter nomenclatura, organização de módulos e padrões de import existentes
3. **Comunicação:** Em caso de dúvida, risco de alucinação ou necessidade de decisão de arquitetura, acionar o agente apropriado (PO, Planejador ou QA) antes de prosseguir
4. **Delegação:** Respeitar organograma ágil: PO → Planejador → Dev Backend → QA → DevOps/Suporte (como apoio)

### Fluxo de Trabalho
1. **PO** define prioridades e visão de produto
2. **Planejador** transforma isso em tarefas executáveis com critérios de aceite claros
3. **Dev Backend** implementa as tarefas seguindo a estrutura do projeto
4. **QA** valida a implementação contra critérios de aceite e regras de negócio
5. **DevOps/Suporte** fornece sustentação e ajuda em tarefas transversas
6. Em caso de conflitos ou dúvidas, retornar ao agente anterior no fluxo para esclarecimento

## Canais de Comunicação
- Agentes devem usar suas respectivas áreas de trabalho (kanbans) para acompanhamento de tarefas
- Em caso de bloqueio ou necessidade de esclarecimento, solicitar apoio ao agente apropriado
- Todos os agentes devem manter seus kanbans atualizados com status das tarefas
- Reuniões de sincronização podem ocorrer conforme necessário entre os agentes

## Instruções para Iniciar Trabalho
1. Cada agente deve revisar seu kanban específico para entender suas responsabilidades iniciais
2. O Planejador deve trabalhar com o PO para definir as primeiras prioridades
3. O Dev Backend deve aguardar tarefas "Pronto para Iniciar" no seu kanban
4. O QA deve começar elaborando cenários de teste baseados no conhecimento atual do projeto
5. O DevOps/Suporte deve preparar o ambiente de trabalho e melhorar a documentação inicial

## Monitoramento e Melhoria Contínua
- Kanbans devem ser revisados e atualizados diariamente
- Retrospectivas devem ocorrer a cada duas semanas para melhorar o processo
- Métricas específicas de cada agente devem ser acompanhadas para identificar melhorias
- Qualquer agente pode sugerir melhorias no processo de trabalho através do Planejador ou PO