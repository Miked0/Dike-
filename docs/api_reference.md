# Referência da API Interna

Este documento descreve a interface pública dos principais módulos do projeto Dikē.

## Módulo: `src.parsers.json_parser`

### Funções

#### `parse_json_payload(json_content: str) -> Dict[str, Any]`
Processa o payload JSON da API e retorna um dicionário com os dados validados.

**Parâmetros:**
- `json_content`: String contendo o JSON do payload da API

**Retorna:**
- Dicionário com os dados do payload validados e convertidos

**Exceções:**
- `json.JSONDecodeError`: Se o JSON for malformado
- `JSONSchemaValidationError`: Se o JSON não estiver conforme o schema
- `JSONTypeConversionError`: Se houver erro na conversão de tipos
- `JSONParserError`: Para outros erros de parsing

**Exemplo de uso:**
```python
from src.parsers.json_parser import parse_json_payload

json_string = '{"fecha": "2026-09-15T14:30:00-03:00", "numero": "123", "total": "100.50"}'
parsed_data = parse_json_payload(json_string)
# Resultado: {'fecha': '2026-09-15T14:30:00-03:00', 'numero': '123', 'total': 100.5, ...}
```

#### `parse_json_file(filepath: str) -> Dict[str, Any]`
Processa um arquivo JSON da API.

**Parâmetros:**
- `filepath`: Caminho para o arquivo JSON

**Retorna:**
- Dicionário com os dados do payload validados e convertidos

**Exceções:**
- `JSONParserError`: Se o arquivo não existir ou JSON for inválido

#### `validate_json_payload(json_content: str) -> bool`
Apenas valida o JSON contra o schema sem processar.

**Parâmetros:**
- `json_content`: String contendo o JSON do payload da API

**Retorna:**
- True se válido

**Exceções:**
- `json.JSONDecodeError`: Se o JSON for malformado
- `JSONSchemaValidationError`: Se o JSON não estiver conforme o schema

### Classes de Exceção

#### `JSONParserError`
Exceção base para erros do parser JSON.

#### `JSONSchemaValidationError(JSONParserError)`
Erro de validação contra o schema JSON.

#### `JSONTypeConversionError(JSONParserError)`
Erro de conversão de tipos.

## Módulo: `src.parsers.xml_parser`

### Funções

#### `parse_xml_cupom_fiscal(xml_content: str) -> CupomFiscalParsed`
Parses XML de cupom fiscal e retorna objeto com todos os campos obrigatórios.

**Parâmetros:**
- `xml_content`: String contendo o XML do cupom fiscal

**Retorna:**
- `CupomFiscalParsed` com todos os campos extraídos

**Exceções:**
- `XMLStructureError`: Se a estrutura XML for inválida ou campos obrigatórios faltarem
- `XMLValidationError`: Se os dados extraídos falharem na validação

#### `parse_xml_file(filepath: str) -> CupomFiscalParsed`
Parses um arquivo XML de cupom fiscal.

**Parâmetros:**
- `filepath`: Caminho para o arquivo XML

**Retorna:**
- `CupomFiscalParsed` com todos os campos extraídos

**Exceções:**
- `XMLStructureError`: Se o arquivo não existir ou XML for inválido

### Classes de Dados

#### `@dataclass ItemDetalhado`
Representa um item detalhado do cupom fiscal.
- `numero_item: int`
- `codigo: str`
- `descricao: str`
- `quantidade: Decimal`
- `unidade: str`
- `valor_unitario: Decimal`
- `valor_total_item: Decimal`
- `indicador_totalizador: int`

#### `@dataclass FormaPagamento`
Representa uma forma de pagamento do cupom fiscal.
- `tipo: str`
- `valor: Decimal`

#### `@dataclass CupomFiscalParsed`
Resultado do parsing do cupom fiscal com todos os campos obrigatórios.
- `fecha: str`  # Data de emissão no formato YYYY-MM-DD
- `numero: str`  # Número do cupom
- `total: Decimal`  # Valor total do cupom
- `cancelacion: bool`  # Indica se o cupom foi cancelado
- `detalhes: list[ItemDetalhado]`  # Lista de itens detalhados
- `pagos: list[FormaPagamento]`  # Lista de formas de pagamento
- `descuentoTotal: Decimal`  # Total de descontos
- `recargoTotal: Decimal`  # Total de recargos
- `codigoMoneda: str`  # Código da moeda (ex: BRL)
- `cotizacion: Decimal`  # Cotação da moeda

### Classes de Exceção

#### `XMLParserError`
Exceção base para erros do parser XML.

#### `XMLStructureError(XMLParserError)`
Erro na estrutura do XML (elementos obrigatórios ausentes).

#### `XMLValidationError(XMLParserError)`
Erro de validação dos dados extraídos.

## Módulo: `src.services.validation_service`

### Classe: `ValidationService`

#### `__init__()`
Inicializa o serviço de validação com uma instância do `ValidationEngine`.

#### `validar_arquivos(roteiro_content, cupons_content, json_content, roteiro_file_type=None) -> Tuple[List[dict], List[str]]`
Valida os arquivos de entrada e retorna os resultados.

**Parâmetros:**
- `roteiro_content`: Conteúdo do arquivo de roteiro de testes (XLSX/CSV)
- `cupons_content`: Lista de conteúdos dos arquivos de cupons (XML/PDF/Imagem)
- `json_content`: Conteúdo do arquivo JSON da API
- `roteiro_file_type`: Tipo do arquivo de roteiro (opcional, será detectado se não fornecido)

**Retorna:**
- Tuple contendo:
  - Lista de dicionários com resultados formatados para exibição
  - Lista de mensagens de erro

#### Métodos Privados

- `_detect_file_type(filename: str) -> str`: Detecta o tipo de arquivo baseado na extensão
- `_processar_roteiro(roteiro_content: Any, file_type: str) -> List[dict]`: Processa o arquivo de roteiro de testes
- `_processar_cupons(cupons_content: List[Any]) -> List[dict]`: Processa os arquivos de cupons fiscais
- `_processar_json_api(json_content: Any) -> dict`: Processa o arquivo JSON da API
- `_criar_movimiento_desde_dados(caso_teste: dict, cupom_data: dict, api_payload: dict) -> Movimiento`: Cria objeto Movimiento a partir dos dados processados

## Módulo: `src.validators.validation_engine`

### Classe: `ValidationResult`

#### `__init__()`
Inicializa o resultado da validação com listas vazias de erros e avisos, e `is_valid` como True.

#### `add_error(message: str)`
Adiciona um erro de validação e marca o resultado como inválido.

#### `add_warning(message: str)`
Adiciona um aviso de validação (não afeta o status de validade).

### Classe: `ValidationEngine`

#### `__init__()`
Inicializa o motor de validação.

#### `validar_movimiento(movimiento: Movimiento) -> ValidationResult`
Valida um movimento conforme as regras da Etapa 01.

**Parâmetros:**
- `movimiento`: O movimento a ser validado

**Retorna:**
- `ValidationResult`: Resultado da validação contendo erros, avisos e status de validade

#### Métodos Privados de Validação

- `_validar_detalles(detalles: List[Detalle], result: ValidationResult)`: Valida a lista de detalhes
- `_validar_pagos(pagos: List[Pago], result: ValidationResult)`: Valida a lista de pagos
- `_validar_consistencia_total_detalles(movimiento: Movimiento, result: ValidationResult)`: Valida consistência entre total e detalhes
- `_validar_consistencia_total_pagos(movimiento: Movimiento, result: ValidationResult)`: Valida consistência entre total e pagos
- `_validar_desconto_recargo(movimiento: Movimiento, result: ValidationResult)`: Valida campos de desconto e recargo

## Módulo: `src.models.models`

### Classes de Dados

#### `@dataclass Detalle`
Representa um item detalhe do movimento.
- `data: dict = field(default_factory=dict)`

#### `@dataclass Pago`
Representa um pagamento do movimento.
- `data: dict = field(default_factory=dict)`

#### `@dataclass Movimiento`
Representa um movimento conforme o schema_etapa01.json
- `fecha: datetime`
- `numero: str`
- `total: float`
- `cancelacion: bool`
- `detalhes: List[Detalle] = field(default_factory=list)`
- `pagos: List[Pago] = field(default_factory=list)`
- `descuento_total: float = 0.0`
- `recargo_total: float = 0.0`
- `codigo_moneda: str = "986"`
- `cotizacion: float = 1.0`

**Métodos:**
- `__post_init__()`: Validações após a inicialização (verifica que descontos, acréscimos e cotação sejam válidos)

**Exceções:**
- `ValueError`: Se campos tiverem valores inválidos (desconto/acréscimo negativo, cotação <= 0)