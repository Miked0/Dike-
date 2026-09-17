# Kanban do DevOps/Suporte (Lynx)

## Responsabilidades
- Apoio em tarefas de infraestrutura leve do projeto
- Organização de arquivos de configuração
- Scripts auxiliares
- Validação de ambientes
- Documentação técnica
- Ajustes de scripts de execução
- Atuar como "backup" de Orion em tarefas de desenvolvimento
- Apoio ao QA em cenários de teste mais técnicos (ex: preparar massa de dados, rodar scripts de validação em lote)
- Manter kanban próprio com tarefas integradas ao fluxo geral do projeto01

## Colunas do Kanban
- [ ] Backlog de Infraestrutura
- [ ] Pronto para Iniciar
- [ ] Em Desenvolvimento
- [ ] Em Validação
- [ ] Pronto para Produção
- [ ] Concluído

## Áreas de Atuação
1. **Infraestrutura Leve:** Configurações, scripts de setup, variáveis de ambiente
2. **Automação de Tarefas:** Scripts para build, deploy, testes
3. **Ambiente e Dependências:** Gerenciamento de requisitos, virtual environments
4. **Documentação:** READMEs técnicos, guias de setup, documentação de API
5. **Suporte Técnico:** Auxílio em troubleshooting, otimização de performance leve
6. **Backup de Desenvolvimento:** Auxílio em tarefas de programação quando necessário
7. **Suporte ao QA:** Preparação de dados de teste, execução de testes em lote

## Tarefas Pronto para Iniciar

### Tarefa DEVOPS-001: Mejorar Scripts de Execução e Deploy
**Descrição:** Criar ou melhorar scripts para facilitar a execução e deploy da aplicação
**Localização:** Raiz do projeto ou diretorio scripts/
**Requisitos:**
- Script para instalação de dependências (requirements.txt)
- Script para execução da aplicação Streamlit
- Script para execução de testes (quando implementados)
- Script para validação de ambiente
- Documentação de uso dos scripts
**Critérios de Aceite:**
- Scripts funcionam no ambiente Windows (PowerShell e/ou Batch)
- Scripts são idempotentes quando apropriado
- Mensagens de erro claros e úteis
- Scripts seguem convenções de nomeação do projeto
- Instruções claras no README sobre como usar os scripts
**Estimativa:** 4 horas

### Tarefa DEVOPS-002: Preparar Ambiente de Teste com Massa de Dados
**Descrição:** Criar conjunto de dados de teste para uso pelo QA e desenvolvimento
**Localização:** diretorio tests/data/ ou similar
**Requisitos:**
- Arquivos de exemplo para cada tipo de entrada (XML, CSV, XLSX, JSON, PDF)
- Dados cobrindo cenários de teste básicos e edge cases
- Scripts para gerar ou popolare dados de teste
- Documentação sobre o conteúdo e uso dos dados de teste
- Versionamento simples dos dados de teste
**Critérios de Aceite:**
- Dados de teste cobrem pelo menos 80% dos cenários identificados pelo QA
- Arquivos são válidos e podem ser processados pelos parsers
- Scripts de geração são reutilizáveis e parametrizáveis
- Dados são realistas e refletem cenários de uso real
- Fácil de atualizar e expandir conforme necessário
**Estimativa:** 6 horas

### Tarefa DEVOPS-003: Melhorar Documentação Técnica
**Descrição:** Aprimorar documentação técnica do projeto para desenvolvedores e usuários
**Localização:** docs/ directory ou arquivos específicos
**Requisitos:**
- Guia de setup para desenvolvedores
- Documentação da API interna (funções e módulos principais)
- Explicação do fluxo de validação
- Instruções para contribuição e boas práticas
- Troubleshooting guide para problemas comuns
**Critérios de Aceite:**
- Documentação está clara, atualizada e fácil de seguir
- Exemplos de código são funcionais e testados
- Estrutura de documentação é lógica e navegável
- Inclui diagramas de fluxo quando apropriado
- Disponível em português (langue do projeto)
**Estimativa:** 5 horas

### Tarefa DEVOPS-004: Implementar Scripts de Validação em Lote
**Descrição:** Criar scripts para executar validações em lote (útil para QA e performance testing)
**Localização:** scripts/ directory
**Requisitos:**
- Script para processar múltiplos arquivos de entrada
- Geração de relatórios consolidados
- Opções de configurabilidade (pastas, formatos, saída)
- Logging detalhado para troubleshooting
- Tratamento de erros em lote (continuar apesar de falhas individuais)
**Critérios de Aceite:**
- Script processa lote de arquivos de teste
- Relatório consolidado mostra estatísticas gerais
- Script continua processando mesmo com arquivos inválidos
- Logs ajudam a identificar problemas específicos
- Performance aceitável para lotes razoáveis
**Estimativa:** 6 horas

### Tarefa DEVOPS-005: Otimizar Configurações e Variáveis de Ambiente
**Descrição:** Organizar e melhorar o gerenciamento de configurações do projeto
**Localização:** config/ directory
**Requisitos:**
- Revisar estrutura atual de configurações
- Separar configurações de ambiente (dev, test, prod)
- Melhorar uso de variáveis de ambiente
- Documentar todas as opções de configuração
- Validar configurações na inicialização
**Critérios de Aceite:**
- Configurações estão bem organizadas e fáceis de modificar
- Ambientes diferentes podem ser configurados facilmente
- Variáveis de ambiente são usadas apropriadamente
- Erros de configuração são detectados early e com mensagens claras
- Documentação completa das opções disponíveis
**Estimativa:** 4 horas

## Tarefas Em Desenvolvimento

### Tarefa DEVOPS-006: Suporte à Implementação de PDF/Imagem para Cupons Fiscais
**Descripción:** Apoiar a implementação de suporte a PDF e imagem para cupons fiscais, incluindo preparação de ambiente com Tesseract pré-instalado e documentos de teste
**Localización:** Vários (dependendo da necessidade)
**Requisitos:**
- Instalar e configurar bibliotecas OCR (Tesseract, etc.)
- Preparar ambientes de teste com documentos PDF/imagem de exemplo de qualidade variada
- Criar scripts de validação para o novo formato
- Documentar procedimentos de instalação e uso
- **Garantir que o ambiente de desenvolvimento tenha Tesseract OCR instalado e configurado**
- **Preparar pelo menos 3 documentos de teste PDF com diferentes qualidades**
- **Preparar pelo menos 3 imagens de teste (JPEG/PNG) com diferentes qualidades**
- **Ter script de validação em lote funcional para teste de desempenho**
**Critérios de Aceite:**
- Ambiente configurado para processar PDF e imagem
- Tesseract funcionando e acessível via linha de comando
- Pelo menos 3 documentos de teste PDF com diferentes qualidades disponíveis
- Pelo menos 3 imagens de teste (JPEG/PNG) com diferentes qualidades disponíveis
- Scripts de teste funcionam com os novos formatos
- Documentação de instalação disponível
- Script de validação em lote funcional
**Dependências:** Nenhuma
**Estimativa:** 8 horas
**Status:** Em Desenvolvimento - Prazo para conclusão: 1 dia útil (até 2026-09-17)
**Delegado por:** Product Owner (Mike) em 2026-09-16 com tarefa específica de preparação de ambiente

## Tarefas Em Validação
- [ ] Nenhuma no momento

## Tarefas Pronto para Produção
- [ ] Nenhuma no momento

## Tarefas Concluído

### Tarefa DEVOPS-001: Mejorar Scripts de Execução e Deploy
**Descrição:** Criar ou melhorar scripts para facilitar a execução e deploy da aplicação
**Localização:** Raiz do projeto ou diretorio scripts/
**Requisitos:**
- Script para instalação de dependências (requirements.txt)
- Script para execução da aplicação Streamlit
- Script para execução de testes (quando implementados)
- Script para validação de ambiente
- Documentação de uso dos scripts
**Critérios de Aceite:**
- Scripts funcionam no ambiente Windows (PowerShell e/ou Batch)
- Scripts são idempotentes quando apropriado
- Mensagens de erro claros e úteis
- Scripts seguem convenções de nomeação do projeto
- Instruções claras no README sobre como usar os scripts
**Estimativa:** 4 horas
**Status:** Concluído - Scripts criados para instalação, execução e testes

### Tarefa DEVOPS-002: Preparar Ambiente de Teste com Massa de Dados
**Descrição:** Criar conjunto de dados de teste para uso pelo QA e desenvolvimento
**Localização:** diretorio tests/data/ ou similar
**Requisitos:**
- Arquivos de exemplo para cada tipo de entrada (XML, CSV, XLSX, JSON, PDF)
- Dados cobrendo cenários de teste básicos e edge cases
- Scripts para gerar ou popolare dados de teste
- Documentação sobre o conteúdo e uso dos dados de teste
- Versionamento simples dos dados de teste
**Critérios de Aceite:**
- Dados de teste cobrem pelo menos 80% dos cenários identificados pelo QA
- Arquivos são válidos e podem ser processados pelos parsers
- Scripts de geração são reutilizáveis e parametrizáveis
- Dados são realistas e refletem cenários de uso real
- Fácil de atualizar e expandir conforme necessário
**Estimativa:** 6 horas
**Status:** Concluído - Dataset de teste preparado com exemplos para todos os tipos de entrada

## Métricas do DevOps/Suporte
- Disponibilidade de Ambiente: >95% do tempo o ambiente de desenvolvimento está funcional
- Velocidade de Setup: Novo desenvolvedor consegue rodar o projeto em <30 minutos
- Eficiência de Suporte: <4h tempo médio para resolver questões de infraestrutura
- Qualidade da Documentação: <10% de questões devido a documentação inadequada
- Automação: >50% de tarefas repetitivas automatizadas
- Satisfação da Equipe: Feedback positivo sobre suporte técnico e infraestrutura

## Boas Práticas a Seguir
1. Sempre validar mudanças em ambiente isolado antes de aplicar no principal
2. Manter backups de configurações críticas
3. Documentar procedimentos de recuperação e rollback
4. Testar scripts em diferentes condições (arquivos grandes, conexões lentas, etc.)
5. Seguir o princípio do menor privilégio em configurações
6. Manter logs adequados para troubleshooting
7. Consultar QA quando preparar dados de teste ou scripts de validação
8. Consultar Orion quando houver necessidade de mudanças no código para suportar infraestrutura
9. Consultar Planejador quando houver ambiguidade no escopo de tarefas de infraestrutura
10. Manter foco em soluções leves e práticas - evitar sobre-engenharia de infraestrutura

## Atualizações Recentes
- [2026-09-15] Concluído: Scripts de execução e deploy melhorados
- [2026-09-15] Concluído: Ambiente de teste com massa de dados preparado
- [2026-09-15] Preparado para iniciar: Melhoria da documentação técnica
- [2026-09-15] Preparado para iniciar: Scripts de validação em lote
- [2026-09-15] Preparado para iniciar: Otimização de configurações e variáveis de ambiente
- [2026-09-15] Adicionada nova tarefa: Suporte à implementação de PDF/imagem para cupons fiscais