# Kanban do Desenvolvedor Backend (Orion)

## Responsabilidades
- Implementação de scripts Python
- Automações
- Integrações
- Manipulação de arquivos (JSON, XML, CSV)
- Chamadas a APIs
- Estruturação de módulos do projeto
- Seguir a estrutura de pastas já existente do projeto01
- Evitar criar subpastas infinitas
- Criar novas pastas apenas com justificativa clara de organização e reaproveitamento
- Trabalhar diretamente na estrutura disponível
- Manter coerência com o padrão do projeto (nomenclatura, organização de módulos, imports, etc.)

## Colunas do Kanban
- [ ] Backlog de Desenvolvimento
- [ ] Pronto para Iniciar
- [ ] Em Desenvolvimento
- [ ] Em Code Review
- [ ] Pronto para Teste
- [ ] Concluído

## Princípios de Implementação
1. **Coerência:** Seguir padrões existentes de nomenclatura e organização
2. **Reaproveitamento:** Utilizar componentes existentes quando possível
3. **Simplicidade:** Evitar sobre-engenharia
4. **Testabilidade:** Código fácil de testar unitariamente
5. **Documentação:** Comentários claros e docstrings quando necessario
6. **Tratamento de Erros:** Exceções específicas e mensagens claras

## Tarefas Pronto para Iniciar
- [ ] Nenhuma no momento

## Tarefas Em Desenvolvimento

### Tarefa DEV-004: Implementar Criação de Objeto Movimiento
**Descrição:** Implementar método para crear objetos Movimiento a partir de los datos procesados
**Localización:** src/services/validation_service.py (método _criar_movimiento_desde_dados)
**Entrada:** 
- caso_teste: dict do roteiro de testes
- cupom_data: dict do parser XML
- api_payload: dict do parser JSON
**Saída:** Objeto Movimiento válido
**Requisitos:**
- Mapear datos de tres fuentes para campos del Movimiento
- Resolver conflictos conforme reglas de negocio definidas
- Aplicar validaciones de negocio antes de crear el objeto
- Tratar datos ausentes o inconsistentes adecuadamente
- Fornecer feedback claro cuando creacion no es posible
**Critérios de Aceite:**
- Cria objetos Movimiento válidos a partir de datos de prueba
- Resuelve conflictos de fuentes conforme prioridades establecidas
- Valida datos antes de crear objeto (evita crear objetos invalidos)
- Fornece mensagens de error claros cuando datos insuficientes
- Mantiene rastreabilidad (log o comentario sobre fuentes de datos)
**Dependencias:** DEV-001, DEV-002, DEV-003
**Estimativa:** 10 horas
**Status:** Concluído - Testes unitários abrangentes implementados para _criar_movimiento_desde_dados, cobrindo todos os cenários de prioridade de fontes, conversão de tipos, tratamento de erros e casos limite. Todos os testes passando.

### Tarefa DEV-005: Implementar Validações Completas do ValidationEngine
**Descrição:** Completar las validaciones pendentes no ValidationEngine conforme schema_etapa01.json
**Localización:** src/validators/validation_engine.py
**Requisitos:**
- Implementar _validar_detalles com regras específicas conforme estrutura real
- Implementar _validar_pagos com regras específicas conforme estrutura real
- Completar _validar_consistencia_total_detalles com cálculo real
- Completar _validar_consistencia_total_pagos com cálculo real
- Revisar y mejorar _validar_desconto_recargo conforme necesario
- Agregar validaciones adicionales conforme descubrimos en el esquema
**Critérios de Aceite:**
- Todas las validaciones obligatorias del schema están implementadas
- Las validaciones detectan correctamente inconsistencias reales
- Mensajes de error son específicos y útiles
- Rendimiento adecuado para validación de lote
- Código bem probado unitariamente
**Dependencias:** Entendimiento da estrutura real dos detalhes e pagos (a ser fornecido pelo QA/PO)
**Estimativa:** 12 horas
**Status:** Significativamente avançado - Implementados _validar_detalles e _validar_pagos com validação abrangente de identificadores e informações de valor; completados _validar_consistencia_total_detalles e _validar_consistencia_total_pagos com cálculos reais incluindo descontos/acréscimos; melhoradas validações de descontos/acréscimos com warnings para valores excessivos; criado suite abrangente de testes unitários (24 testes) cobrindo todos os cenários de validação. Todos os testes passando.

## Tarefas Em Code Review
- [ ] Nenhuma no momento

## Tarefas Pronto para Teste
- [ ] Nenhuma no momento

## Tarefas Concluído

### Tarefa DEV-001: Implementar Parser XML para Cupons Fiscais
**Descrição:** Criar módulo para parsear arquivos XML de cupons fiscais conforme schema_etapa01.json
**Localização:** src/parsers/xml_parser.py
**Entrada:** Conteúdo bytes do arquivo XML
**Saída:** Dicionário con todos los campos del movimiento conforme modelo
**Requisitos:**
- Lidar con namespaces XML comunes
- Validar campos obligatorios
- Converter tipos de datos apropiadamente (strings para datetime, floats, etc.)
- Tratar campos opcionales com valores padrão
- Fornecer mensagens de erro claros para XML inválido
- Suportar estructuras XML variadas dentro del patrón Scanntech
**Critérios de Aceite:**
- Parser lê arquivos XML de teste fornecidos pelo QA
- Todos los campos obligatorios están extraídos correctamente
- Tipos de datos estão correctos (datetime, float, bool, etc.)
- Errores de parsing generan excepciones específicas com mensagens úteis
- Performance adecuada (<1s para archivos hasta 5MB)
- Código sigue los estándares del proyecto (pep8, imports claros, etc.)
**Dependencias:** Nenhuma
**Estimativa:** 8 horas
**Status:** Concluído

### Tarefa DEV-002: Implementar Parser CSV/XLSX para Roteiro de Testes
**Descrição:** Criar módulo para extrair casos de teste de planilhas CSV e XLSX
**Localização:** src/parsers/roteiro_parser.py
**Entrada:** Conteúdo bytes do arquivo CSV/XLSX
**Saída:** Lista de dicionários, cada un representando un caso de prueba
**Requisitos:**
- Suportar ambos CSV e XLSX
- Auto-detectar delimitador para CSV (vírgula, punto y coma, tab)
- Lidar con diferentes encodings (UTF-8, Latin-1, etc.)
- Mapear columnas de la planilla para campos del caso de prueba
- Validar campos obligatorios en los casos de prueba
- Tratar líneas vacías y comentarios
**Critérios de Aceite:**
- Parser procesa archivos CSV y XLSX de prueba
- Campos obligatorios son validados y extraídos
- Mensajes de error claros para formatos inválidos
- Performance adecuada (<2s para planilhas con 1000 líneas)
- Código reutilizable y bien documentado
**Dependencias:** Nenhuma
**Estimativa:** 6 horas
**Status:** Concluído

### Tarefa DEV-003: Implementar Processamento do JSON da API
**Descrição:** Crear módulo para procesar e validar el payload JSON da API conforme schema_etapa01.json, garantindo a compatibilidade com o ValidationService e preparando para a criação do objeto Movimiento.
**Localización:** src/parsers/json_parser.py
**Entrada:** Conteúdo bytes do arquivo JSON
**Saída:** Dicionário válido conforme schema_etapa01.json con todos os campos obrigatórios e tipos corretos.
**Requisitos:**
- Validar estructura JSON contra schema_etapa01.json (arquivo: config/schemas/schema_etapa01.json)
- Aplicar valores padrão definidos no schema para campos opcionais ausentes
- Converter tipos de datos apropiadamente conforme definido no schema (string para data, número para valores monetários, boolean para flags, etc.)
- Fornecer mensagens de erro claras y específicas para JSON malformed o inválido contra el schema
- Lidar con codificación UTF-8 padrão
- Implementar funciones de apoyo para extração de subestruturas (detalles, pagos) se necesario para validações futuras
- Manter consistencia con el estilo do projeto (docstrings, tratamento de exceções, logging)
**Critérios de Aceite:**
- Processa JSON válido conforme schema_etapa01.json e retorna dicionário con todos os campos
- Aplica corretamente valores padrão conforme definido no schema
- Detecta e relata erros de validação de schema con mensagens específicas (campo ausente, tipo incorreto, etc.)
- Mensagens de erro incluyen camino do campo problemático para facilitar depuración
- Performance adecuada (<500ms para payloads típicos de até 10KB)
- Código sigue padrões do projeto (PEP 8, imports claros, docstrings completas)
- Compatível con el ValidationService existente (não quebra funcionalidade atual)
**Dependencias:**
- schema_etapa01.json debe existir en config/schemas/
- Nenhuma dependencia externa além da biblioteca padrão
**Estimativa:** 4 horas
**Status:** Concluído

## Métricas de Desenvolvimento
- Velocidade: Historia por sprint (usando puntos de historia estimados)
- Qualidade: <2 bugs críticos por funcionalidad entregue
- Cobertura de Testes: >75% de código nuevo cubierto por pruebas unitarias
- Revisión de Código: <3 comentarios por PR en promedio
- Predictabilidad: +/- 20% de la estimativa de tiempo
- Reaproveitamiento: >30% del código reutiliza componentes existentes

## Boas Práticas a Seguir
1. Siempre leer el archivo existente antes de modificar (usar Read tool)
2. Seguir el estilo de codigo existente (nomenclación, comentarios, estructura)
3. Escribir pruebas unitarias para novas funcionalidades
4. Documentar funções públicas com docstrings
5. Tratar excedentes especificamente, no usar exceções genéricas
6. Hacer pequenos commits com mensagens claros
7. Consultar a QA quando tiver dúvida sobre regras de negócio
8. Consultar o Planner quando houver ambiguidade no alcance
9. Consultar o PO quando houver conflito de prioridades ou risco de alucinação
10. Manter o foco no arquivo/módulo específico que se está trabalhando

## Atualizações Recentes
- [2026-09-15] Concluído: Parser XML para cupons fiscais (DEV-001)
- [2026-09-15] Concluído: Parser CSV/XLSX para roteiro de testes (DEV-002)
- [2026-09-15] Concluído: Processamento do JSON da API (DEV-003)
- [2026-09-15] Em desenvolvimento: Criação de objeto Movimiento (DEV-004)
- [2026-09-15] Em desenvolvimento: Validações completas do ValidationEngine (DEV-005)