# Kanban do QA (Vega)

## Responsabilidades
- Revisão de roteiros de teste
- Validação de cenários
- Análise de JSONs/XMLs
- Conferência de regras de negócio
- Validação de saídas de automação
- Manter kanban próprio com tarefas de validação, bugs encontrados, cenários cobertos e pendências de teste
- Abrir tarefa para o agente de desenvolvimento ou acionar o PO/Planejador para reavaliação de escopo ao identificar inconsistências

## Colunas do Kanban
- [ ] Cenários a Elaborar
- [ ] Cenários Elaborados
- [ ] Em Teste
- [ ] Bugs Encontrados
- [ ] Cenários Cobertos
- [ ] Pendências de Teste
- [ ] Concluído

## Tipos de Tarefa
- CT: Caso de Teste
- BUG: Bug encontrado durante teste
- VAL: Validação de artefato
- EXP: Exploração de cenário edge case
- DOC: Documentação de teste

## Cenários a Elaborar

**Descrição CT-010:** Validar que quando houver inconsistência entre JSON da API e Cupom Fiscal, o sistema prioriza o JSON da API
**Pré-condições:**
- Roteiro de teste com caso definido
- Cupom fiscal XML com dado divergente do JSON da API
- JSON da API com dado válido e diferente do cupom
**Passos:**
1. Carregar roteiro de teste
2. Carregar cupom fiscal com dado inconsistente
3. Carregar JSON da API com dado válido e diferente do cupom
4. Executar validação
5. Verificar que o sistema usa o dado do JSON da API e ignora o dado inconsistente do cupom
**Critérios de Aceite:**
- Sistema retorna status apropriado baseado no JSON da API
- Sistema relata claramente que identificou inconsistência e optou pelo JSON da API
- Tempo de resposta < 3s
**Dados de Teste:**
- Roteiro: ID Teste TST-010, Descrição "Precedência JSON sobre Cupom"
- Cupom: CNPJ válido, data atual, total 90.00 (inconsistente)
- JSON: Payload conforme schema com total 100.00 (válido, deve prevalecer)
**Complexidade:** Média

**Descrição CT-011:** Validar que quando houver inconsistência entre JSON da API e Roteiro de Testes, o sistema prioriza o JSON da API
**Pré-condições:**
- Roteiro de teste com dado divergente do JSON da API
- Cupom fiscal XML com dados consistentes com o JSON da API
- JSON da API com dado válido e diferente do roteiro
**Passos:**
1. Carregar roteiro de teste com dado inconsistente
2. Carregar cupom fiscal com dados consistentes com JSON
3. Carregar JSON da API com dado válido e diferente do roteiro
4. Executar validação
5. Verificar que o sistema usa o dado do JSON da API e ignora o dado inconsistente do roteiro
**Critérios de Aceite:**
- Sistema retorna status apropriado baseado no JSON da API
- Sistema relata claramente que identificou inconsistência e optou pelo JSON da API
- Tempo de resposta < 3s
**Dados de Teste:**
- Roteiro: ID Teste TST-011, Descrição "Precedência JSON sobre Roteiro", descrição "Teste para validar precedência"
- Cupom: CNPJ válido, data atual, total 100.00, detalhes consistentes com JSON
- JSON: Payload conforme schema com total 100.00 (válido, deve prevalecer)
**Complexidade:** Média

**Descrição CT-012:** Validar que quando houver inconsistência entre Cupom Fiscal e Roteiro de Testes, o sistema prioriza o Cupom Fiscal
**Pré-condições:**
- Roteiro de teste com dado divergente do Cupom Fiscal
- Cupom fiscal XML com dado válido
- JSON da API com dados consistentes com o cupom (ou ausente)
**Passos:**
1. Carregar roteiro de teste com dado inconsistente
2. Carregar cupom fiscal com dado válido e diferente do roteiro
3. Carregar JSON da API com dados consistentes com o cupom
4. Executar validação
5. Verificar que o sistema usa o dado do cupom fiscal e ignora o dado inconsistente do roteiro
**Critérios de Aceite:**
- Sistema retorna status apropriado baseado no cupom fiscal
- Sistema relata claramente que identificou inconsistência e optou pelo cupom fiscal
- Tempo de resposta < 3s
**Dados de Teste:**
- Roteiro: ID Teste TST-012, Descrição "Precedência Cupom sobre Roteiro", descrição "Teste para validar precedência"
- Cupom: CNPJ válido, data atual, total 100.00 (válido, deve prevalecer)
- JSON: Payload conforme schema com total 100.00 (consistente com cupom)
**Complexidade:** Média

**Descrição CT-013:** Validar tratamento quando todas as três fontes (roteiro, cupom, JSON) têm dados inconsistentes
**Pré-condições:**
- Roteiro de teste com dado específico
- Cupom fiscal XML com dado diferente do roteiro
- JSON da API com dado diferente tanto do roteiro quanto do cupom
**Passos:**
1. Carregar roteiro de teste com dado A
2. Carregar cupom fiscal com dado B (diferente de A)
3. Carregar JSON da API com dado C (diferente de A e B)
4. Executar validação
5. Verificar que o sistema aplica a ordem de precedência: JSON > Cupom > Roteiro
**Critérios de Aceite:**
- Sistema retorna status apropriado baseado no JSON da API (maior precedência)
- Sistema relata claramente que identificou inconsistências em todas as fontes e aplicou a regra de precedência
- Tempo de resposta < 3s
**Dados de Teste:**
- Roteiro: ID Teste TST-013, Descrição "Três Fontes Inconsistentes", descrição "Teste para validar precedência com três fontes"
- Cupom: CNPJ válido, data atual, total 90.00 (segunda precedência)
- JSON: Payload conforme schema com total 100.00 (maior precedência, deve prevalecer)
**Complexidade:** Média


## Cenários Elaborados
- [x] CT-001: Validação de Cupom Válido
- [x] CT-002: Validação de Desconto Excessivo
- [x] CT-003: Validação de Pagos Insuficientes
- [x] CT-004: Validação de Campos Obrigatórios Ausentes
- [x] CT-005: Validação de Detalhes Vazios
- [x] CT-010: Validação de Precedência JSON sobre Cupom
- [x] CT-011: Validação de Precedência JSON sobre Roteiro
- [x] CT-012: Validação de Precedência Cupom sobre Roteiro
- [x] CT-013: Validação com Três Fontes Inconsistentes
- [ ] CT-006: Validação de Fluxo Completo com Dados Consistentes
- [ ] CT-007: Validação de Inconsistência entre Fontes de Dados
- [ ] CT-008: Validação com PDF de Cupom Fiscal
- [ ] CT-009: Validação com Imagem de Cupom Fiscal
**Descrição:** Validar cupom com todos os campos corretos conforme schema_etapa01.json
**Pré-condições:**
- Roteiro de teste com caso válido
- Cupom XML válido
- JSON da API compatível
**Passos:**
1. Carregar roteiro de teste
2. Carregar cupom fiscal
3. Carregar JSON da API
4. Executar validação
5. Verificar resultado esperado: Aprovado
**Critérios de Aceite:**
- Sistema retorna status "Aprovado"
- Nenhum erro de processamento
- Tempo de resposta < 2s
**Dados de Teste:**
- Roteiro: ID Teste TST-001, Descrição "Todos os campos válidos"
- Cupom: CNPJ válido, data atual, total positivo, detalhes e pagos consistentes
- JSON: Payload conforme schema com todos os campos obrigatórios
**Complexidade:** Baixa

**Descrição:** Validar fluxo completo de validação com todos os dados consistentes entre roteiro, cupom e JSON
**Pré-condições:**
- Roteiro de teste com caso de teste definido
- Cupom fiscal XML com dados correspondentes ao roteiro
- JSON da API com dados correspondentes ao roteiro e cupom
**Passos:**
1. Carregar roteiro de teste
2. Carregar cupom fiscal correspondente
3. Carregar JSON da API correspondente
4. Executar validação completa
5. Verificar que todos os dados são consistentes entre as fontes
**Critérios de Aceite:**
- Sistema retorna status "Aprovado" quando todos os dados estão consistentes
- Detalhes de validação mostram correspondência entre roteiro, cupom e JSON
- Tempo de resposta < 3s
**Dados de Teste:**
- Roteiro: ID Teste TST-006, Descrição "Fluxo completo com consistência"
- Cupom: CNPJ, data, total e detalhes que correspondem exatamente ao roteiro
- JSON: Payload com mesmos valores do roteiro e cupom
**Complexidade:** Média

**Descrição:** Validar detecção de inconsistências entre diferentes fontes de dados (roteiro, cupom, JSON)
**Pré-condições:**
- Roteiro de teste com caso de teste definido
- Cupom fiscal XML com algum dado divergente do roteiro
- JSON da API com outro dado divergente (pode ser do roteiro ou do cupom)
**Passos:**
1. Carregar roteiro de teste com valores esperados
2. Carregar cupom fiscal com pelo menos um campo diferente do roteiro
3. Carregar JSON da API com pelo menos um campo diferente do roteiro ou cupom
4. Executar validação
5. Verificar que o sistema identifica e relata as inconsistências
**Critérios de Aceite:**
- Sistema retorna status indicando inconsistência (ex: "Inconsistente", "Revisão Necessária")
- Sistema relata claramente quais fontes têm quais discrepâncias
- Sistema não aprova o cupom quando há inconsistências críticas
**Dados de Teste:**
- Roteiro: ID Teste TST-007, Descrição "Inconsistência no total", Total esperado: 100.00
- Cupom: Total realmente presente: 90.00 (inconsistente)
- JSON: Total presente: 100.00 (consistente com roteiro, inconsistente com cupom)
**Complexidade:** Média

**Descrição:** Validar suporte a arquivos PDF de cupons fiscais como entrada
**Pré-condições:**
- Roteiro de teste válido
- Arquivo PDF contendo cupom fiscal legível
- JSON da API compatível (opcional para este teste)
**Passos:**
1. Carregar roteiro de teste
2. Carregar arquivo PDF do cupom fiscal
3. (Opcional) Carregar JSON da API
4. Executar validação (sistema deve extrair dados do PDF)
5. Verificar resultado baseado nos dados extraídos do PDF
**Critérios de Aceite:**
- Sistema consegue processar arquivos PDF de cupons fiscais
- Sistema extrai dados relevantes do PDF com precisão adequada
- Quando dados do PDF são consistentes com roteiro, retorna status apropriado
**Dados de Teste:**
- Roteiro: ID Teste TST-008, Descrição "Validação com PDF"
- PDF: Cupom fiscal legível com dados claros
- JSON: (opcional) Dados compatíveis
**Complexidade:** Alta (depende da implementação de extração de PDF)

**Descrição:** Validar suporte a arquivos de imagem (JPEG/PNG) de cupons fiscais como entrada
**Pré-condições:**
- Roteiro de teste válido
- Arquivo de imagem contendo cupom fiscal legível
- JSON da API compatível (opcional para este teste)
**Passos:**
1. Carregar roteiro de teste
2. Carregar arquivo de imagem do cupom fiscal
3. (Opcional) Carregar JSON da API
4. Executar validação (sistema deve extrair dados da imagem via OCR)
5. Verificar resultado baseado nos dados extraídos da imagem
**Critérios de Aceite:**
- Sistema consegue processar arquivos de imagem de cupons fiscais
- Sistema aplica OCR para extrair texto relevante da imagem
- Quando dados extraídos são consistentes com roteiro, retorna status apropriado
**Dados de Teste:**
- Roteiro: ID Teste TST-009, Descrição "Validação com Imagem"
- Imagem: Foto ou scan legível de cupom fiscal
- JSON: (opcional) Dados compatíveis
**Complexidade:** Alta (depende da implementação de OCR)

## Bugs Encontrados
- [x] BUG-001: Falha no Parse de XML com Namespace
- [x] BUG-002: Performance Degradada com Arquivos CSV Grandes
- [ ] BUG-003: Falha na Criação de Objeto Movimiento com Dados Conflitantes
- [ ] BUG-004: Validação Incorreta de Descontos em Cupons Cancelados
- [ ] BUG-005: Performance Degradada ao Processar JSON com Muitos Detalhes

## Cenários Cobertos
- [x] CT-001: Validação de Cupom Válido
- [x] CT-002: Validação de Desconto Excessivo
- [x] CT-003: Validação de Pagos Insuficientes
- [x] CT-004: Validação de Campos Obrigatórios Ausentes
- [x] CT-005: Validação de Detalhes Vazios

## Pendências de Teste
- [ ] Testar com arquivos PDF de cupons fiscais
- [ ] Testar com arquivos de imagem (JPEG/PNG) de cupons
- [ ] Validar comportamento com arquivos corrompidos
- [ ] Testar limites de tamanho de upload
- [ ] Verificar comportamento com encoding diferente em CSV
- [ ] Testar concurrentemente múltiplas validações
- [ ] Testar fluxo completo com dados consistentes (CT-006)
- [ ] Testar tratamento de inconsistências entre fontes (CT-007)
- [ ] Testar suporte a PDF/imagem para cupons fiscais
- [ ] Validar performance com lote de 100+ cupons
- [ ] Testar mecanismo de cache para arquivos repetidos

## Métricas do QA
- Eficiência de detecção: >90% dos bugs encontrados antes do release
- Cobertura de cenários: >80% das regras de negócio cobertas por casos de teste
- Precisão de validação: <5% de falsos positivos/negativos nos testes
- Turnaround de bugs: <24h para bugs críticos, <72h para bugs normais
- Satisfação do dev: Feedback positivo sobre qualidade dos relatos de bug

## Processo de Trabalho
1. Elaborar cenários de teste baseados nas regras de negócio e schema
2. Revisar cenários com o Planejador para garantir completude
3. Executar testes conforme implementação avança
4. Documentar resultados e abrir bugs quando necessário
5. Re-testar bugs após correções
6. Manter rastreabilidade entre requisitos, casos de teste e resultados

## Atualizações Recentes
- [2026-09-15] Elaborado CT-001: Validação de Cupom Válido
- [2026-09-15] Executado e validado CT-002 a CT-005: Todos os testes passaram
- [2026-09-15] Analisado BUG-001: Falha no Parse de XML com Namespace - Identificado problema no parser XML que não lida com namespaces
- [2026-09-15] Analisado BUG-002: Performance Degradada com Arquivos CSV Grandes - Testado com até 1M rows, performance aceitável (~3.2s)
- [2026-09-15] Elaborado CT-006 a CT-009: Cenários de teste avançados definidos