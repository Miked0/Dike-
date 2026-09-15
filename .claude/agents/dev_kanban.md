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

### Tarefa DEV-001: Implementar Parser XML para Cupons Fiscais
**Descrição:** Criar módulo para parsear arquivos XML de cupons fiscais conforme schema_etapa01.json
**Localização:** src/parsers/ (criar xml_parser.py se necessário ou estender pdf_parser.py)
**Entrada:** Conteúdo bytes do arquivo XML
**Saída:** Dicionário com todos os campos del movimiento conforme modelo
**Requisitos:**
- Lidar con namespaces XML comunes
- Validar campos obligatorios
- Converter tipos de datos apropiadamente (strings para datetime, floats, etc.)
- Tratar campos opcionales con valores padrão
- Fornecer mensagens de erro claras para XML inválido
- Suportar estructuras XML variadas dentro del patrón Scanntech
**Critérios de Aceite:**
- Parser lê arquivos XML de teste fornecidos pelo QA
- Todos los campos obligatorios están extraídos correctamente
- Tipos de datos están correctos (datetime, float, bool, etc.)
- Errores de parsing generan excepciones específicas con mensajes útiles
- Performance adecuada (<1s para archivos hasta 5MB)
- Código sigue los estándares del proyecto (pep8, imports claros, etc.)
**Dependencias:** Nenhuma
**Estimativa:** 8 horas

### Tarefa DEV-002: Implementar Parser CSV/XLSX para Roteiro de Testes
**Descrição:** Criar módulo para extrair casos de teste de planilhas CSV e XLSX
**Localização:** src/parsers/ (criar teste_parser.py ou similar)
**Entrada:** Conteúdo bytes do arquivo CSV/XLSX
**Saída:** Lista de dicionários, cada um representando um caso de teste
**Requisitos:**
- Suportar ambos CSV e XLSX
- Auto-detectar delimitador para CSV (vírgula, ponto e vírgula, tab)
- Lidar con diferentes encodings (UTF-8, Latin-1, etc.)
- Mapear colunas da planilha para campos do caso de teste
- Validar campos obrigatórios nos casos de teste
- Tratar linhas vazias e comentários
**Critérios de Aceite:**
- Parser processa arquivos CSV e XLSX de teste
- Campos obligatorios son validados y extraídos
- Mensajes de error claros para formatos inválidos
- Performance adecuada (<2s para planilhas con 1000 líneas)
- Código reutilizável y bien documentado
**Dependencias:** Nenhuma
**Estimativa:** 6 horas

### Tarefa DEV-004: Implementar Criação de Objeto Movimiento
**Descrição:** Implementar método para criar objetos Movimiento a partir dos dados processados
**Localização:** src/services/validation_service.py (método _criar_movimiento_desde_dados)
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

### Tarefa DEV-005: Implementar Validações Completas do ValidationEngine
**Descrição:** Completar las validaciones pendentes no ValidationEngine conforme schema_etapa01.json
**Localización:** src/validators/validation_engine.py
**Requisitos:**
- Implementar _validar_detalles con reglas específicas conforme estructura real
- Implementar _validar_pagos con reglas específicas conforme estructura real
- Completar _validar_consistencia_total_detalles con cálculo real
- Completar _validar_consistencia_total_pagos con cálculo real
- Revisar y mejorar _validar_desconto_recargo conforme necesario
- Agregar validaciones adicionales conforme descubrimos en el esquema
**Critérios de Aceite:**
- Todas las validaciones obligatorias del schema están implementadas
- Las validaciones detectan correctamente inconsistencias reales
- Mensajes de error son específicos y útiles
- Rendimiento adecuado para validación de lote
- Código bien probado unitariamente
**Dependencias:** Entendimiento de la estructura real de los detalles y pagos (a ser proporcionado por QA/PO)
**Estimativa:** 12 horas

## Tarefas Em Desenvolvimento

### Tarefa DEV-003: Implementar Processamento do JSON da API
**Descrição:** Criar módulo para processar e validar o payload JSON da API conforme schema_etapa01.json, garantinte a compatibilidade com o ValidationService e preparando para a criação do objeto Movimiento.
**Localização:** src/parsers/json_parser.py
**Entrada:** Conteúdo bytes do arquivo JSON
**Saída:** Dicionário válido conforme schema_etapa01.json com todos os campos obrigatórios e tipos corretos.
**Requisitos:**
- Validar estructura JSON contra schema_etapa01.json (arquivo: config/schemas/schema_etapa01.json)
- Aplicar valores padrão definidos no schema para campos opcionais ausentes
- Converter tipos de datos apropiadamente conforme definido no schema (string para data, número para valores monetários, boolean para flags, etc.)
- Fornecer mensagens de erro claras y específicas para JSON malformed o inválido contra el schema
- Lidar con codificación UTF-8 padrão
- Implementar funciones de apoyo para extração de subestruturas (detalles, pagos) se necesario para validações futuras
- Manter consistencia con el estilo do projeto (docstrings, tratamento de exceções, logging)
**Critérios de Aceite:**
- Processa JSON válido conforme schema_etapa01.json e retorna dicionário com todos os campos
- Aplica corretamente valores padrão conforme definido no schema
- Detecta e relata erros de validação de schema con mensagens específicas (campo ausente, tipo incorreto, etc.)
- Mensagens de erro incluyen caminho do campo problemático para facilitar depuración
- Performance adecuada (<500ms para payloads típicos de até 10KB)
- Código sigue padrões do projeto (PEP 8, imports claros, docstrings completas)
- Compatível con el ValidationService existente (não quebra funcionalidade atual)
**Dependencias:**
- schema_etapa01.json debe existir en config/schemas/
- Nenhuma dependencia externa além da biblioteca padrão
**Estimativa:** 4 horas

[Nenhuma no momento]

## Tarefas Em Code Review

[Nenhuma no momento]

## Tarefas Pronto para Teste

[Nenhuma no momento]

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
3. Escribir pruebas unitarias para nuevas funcionalidades
4. Documentar funciones públicas con docstrings
5. Tratar excedentes específicamente, no usar excepciones genéricas
6. Hacer pequeños commits con mensajes claros
7. Consultar a QA cuando haya duda sobre reglas de negocio
8. Consultar al Planner cuando haya ambigüedad en el alcance
9. Consultar al PO cuando haya conflicto de prioridades o riesgo de alucinación
10. Mantener el enfoque en el archivo/módulo específico que se está trabajando