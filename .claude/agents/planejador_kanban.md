# Kanban do Planejador (Atlas)

## Responsabilidades
- Transformar demandas e ideias em tarefas executáveis
- Definir critérios de aceite
- Estimar complexidade e sugerir ordem de execução
- Trabalhar em conjunto com o PO para refinar o backlog
- Garantir que cada tarefa no kanban tenha: objetivo claro, escopo delimitado, critérios de aceite e dependências identificadas

## Colunas do Kanban
- [ ] Backlog (ideias e demandas brutas)
- [ ] Em Refinamento (tarefas sendo definidas)
- [ ] Pronto para Desenvolvimento (tarefas com todos os elementos definidos)
- [ ] Em Desenvolvimento (tarefas sendo implementadas pelos devs)
- [ ] Em Teste (tarefas sendo validadas pelo QA)
- [ ] Pronto para Produção (tarefas validadas e prontas para release)
- [ ] Concluído (tarefas entregues e validadas)

## Tarefas em Refinamento

## Tarefas Pronto para Desenvolvimento
- [ ] Tarefa 5: Implementar Suporte a PDF/Imagem para Cupons Fiscais
- [ ] Tarefa 6: Implementar Cache para Arquivos Grandes

## Tarefas Em Desenvolvimento

### Tarefa 4: Implementar Criação de Objeto Movimiento
**Objetivo:** Implementar método para criar objetos Movimiento a partir dos dados processados
**Escopo:**
- Receber dados do caso de teste, cupom e JSON da API
- Construir objeto Movimiento válido conforme models.py
- Aplicar regras de negócio para preenchimento de campos (prioridade: JSON > Cupom > Roteiro)
- Tratar inconsistências entre fontes de dados
- Validar campos obrigatórios antes da criação do objeto
**Critérios de Aceite:**
- Cria objetos Movimiento válidos a partir de dados de teste (JSON, cupom XML, roteiro)
- Resolve conflitos entre fontes de dados conforme regra de prioridade definida
- Gera mensagens de erro claros quando dados são insuficientes ou inconsistentes
- Mantém rastreabilidade entre dados de origem e objeto criado (log de fonte utilizada por campo)
- Passar nos testes unitários cobrindo cenários de conflito e validação
**Dependências:** Tarefa 1, 2 e 3
**Complexidade:** Alta (13 story points)
**Status:** Em Desenvolvimento - Implementação em progresso por Orion (Dev Backend)

## Tarefas Concluído

### Tarefa 1: Parser XML para Cupons Fiscais (CONCLUÍDA)
**Objetivo:** Implementar parser completo para extrair dados de cupons fiscais no formato XML conforme estrutura da Scanntech 3.0
**Escopo:** 
- Ler arquivos XML de cupons fiscais
- Extrair campos obrigatórios: fecha, numero, total, cancelacion, detalles, pagos, descuentoTotal, recargoTotal, codigoMoneda, cotizacion
- Tratar variações comuns no formato XML
- Validar estrutura básica antes do processamento
**Critérios de Aceite:**
- Parser consegue ler XML de exemplo fornecido
- Todos os campos obrigatórios são extraídos corretamente
- Erros de formatação são tratados com mensagens claras
- Performance adequada para arquivos até 10MB
**Dependências:** Nenhuma
**Complexidade:** Média (8 story points)
**Status:** Implementado por Orion com testes unitários

### Tarefa 2: Parser CSV/XLSX para Roteiro de Testes (CONCLUÍDA)
**Objetivo:** Implementar parser para extrair casos de teste de planilhas CSV e XLSX
**Escopo:**
- Suportar ambos os formatos CSV e XLSX
- Mapear colunas da planilha para campos do caso de teste
- Tratar diferentes encodings e delimitadores (para CSV)
- Validar dados obrigatórios nos casos de teste
**Critérios de Aceite:**
- Parser lida com arquivos CSV e XLSX de exemplo
- Campos obrigatórios são validados (ID Teste, Descrição, etc.)
- Mensagens de erro claros para formatos inválidos
- Performance adequada para planilhas com até 1000 linhas
**Dependências:** Nenhuma
**Complexidade:** Média (5 story points)
**Status:** Implementado por Orion com testes unitários

### Tarefa 3: Processamento do JSON da API (CONCLUÍDA)
**Objetivo:** Implementar processamento completo do payload JSON da API para validação
**Escopo:**
- Extrair dados relevantes do JSON conforme schema_etapa01.json
- Mapear campos JSON para objeto Movimiento
- Tratar campos opcionais e valores padrão
- Validar estrutura JSON antes do processamento
**Critérios de Aceite:**
- Processa JSON de exemplo conforme schema
- Cria objeto Movimiento válido
- Trata campos ausentes com valores padrão quando apropriado
- Mensagens de erro claros para JSON inválido
**Dependências:** Tarefa 1 e 2 (para fluxo completo)
**Complexidade:** Baixa (3 story points)
**Status:** Implementado por Orion com testes unitários

## Métricas do Planejador
- Taxa de refinamento: >80% das tarefas entram na coluna "Pronto para Desenvolvimento" em até 2 dias
- Precisão de estimativa: +/- 20% da estimativa inicial
- Clareza dos critérios de aceite: <10% de retrabalho devido a ambiguidade
- Satisfação da equipe: Feedback positivo dos devs e QA sobre qualidade das tarefas

## Reuniões e Ritualos
- Reunião de refinamento: 3x por semana (segunda, quarta, sexta)
- Reunião de planejamento sprint: a cada 2 semanas
- Retrospectiva: a cada 2 semanas