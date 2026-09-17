# Kanban do PO/Orquestrador (Mike)

## Visão Geral do Projeto
Projeto: Dikē - Validador API Scanntech 3.0
Objetivo: Aplicação Streamlit para validar respostas de API contra roteiros de testes e cupons fiscais, garantindo conformidade com os padrões da Scanntech 3.0.

## Épicos e Frentes de Trabalho

### Épico 1: Fundação e Estrutura (Concluído)
- [x] Estrutura básica do projeto Streamlit
- [x] Configuração inicial de modelos e validação
- [x] Interface básica de upload e resultados

### Épico 2: Implementação Completa da Validação (Em Andamento)
- [x] Implementar parsers completos para roteiro de testes (XLSX/CSV)
- [x] Implementar parsers completos para cupons fiscais (XML)
- [x] Implementar processamento completo do JSON da API
- [ ] Implementar criação de objetos Movimiento a partir dos dados processados
- [ ] Implementar validações completas conforme schema_etapa01.json
- [ ] Implementar suporte a PDF e imagem para cupons fiscais

### Épico 3: Melhorias de Usabilidade e Performance
- [ ] Otimizar performance da validação em lote
- [ ] Melhorar experiência do usuário com feedback visual aprimorado
- [ ] Implementar cache para arquivos grandes
- [ ] Adicionar suporte a mais formatos de exportação

### Épico 4: Testes e Qualidade
- [ ] Implementar testes unitários para todos os módulos
- [ ] Implementar testes de integração
- [ ] Criar cenários de teste abrangentes
- [ ] Estabelecer métricas de qualidade

## Próximas Prioridades (Definidas pelo Planejador)
1. [ ] Concluir implementação da criação de objeto Movimiento (DEV-004)
2. [ ] Concluir implementação das validações completas do ValidationEngine (DEV-005)
3. [ ] Implementar suporte a PDF/imagem para cupons fiscais
4. [ ] Implementar testes de integração para validar o fluxo completo
5. [ ] Executar validação com massa de dados preparada pelo DevOps

## Métricas de Sucesso
- Precisão de validação: 99.9% de conformidade com regras de negócio
- Tempo de processamento: <5s para lote de 100 cupons
- Satisfação do usuário: Feedback positivo em usabilidade
- Cobertura de testes: >80% de código coberto por testes automatizados

## Decisões Pendentes
- Definir estratégia de tratamento de erros para arquivos malformados
- Estabelecer limites de tamanho para upload de arquivos
- Definir política de retenção de logs e resultados
- Definir regras de negócio para tratamento de inconsistências entre fontes de dados

## Atualizações Recentes
- [2026-09-15] Primeira etapa concluída: parsers XML, CSV/XLSX e JSON implementados e testados
- [2026-09-15] Planejador refinou especificações para DEV-004 e DEV-005
- [2026-09-15] QA elaborou cenários de teste iniciais (CT-001 a CT-005)
- [2026-09-15] DevOps preparou scripts básicos e ambiente de teste