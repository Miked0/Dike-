# Guia de Setup para Desenvolvedores

Este documento descreve os passos para configurar o ambiente de desenvolvimento, executar a aplicação e rodar os testes.

## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- Git (opcional, para clonar o repositório)

## Instalação

1. Clone o repositório (se ainda não tiver o código localmente):

   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd Dike-
   ```

2. Crie e ative um ambiente virtual (recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

## Executando a Aplicação

A aplicação principal é um app Streamlit. Para executá-la:

```bash
streamlit run main.py
```

Ou, se estiver usando o arquivo com nome especial:

```bash
streamlit run "Dikē .py"
```

A aplicação estará disponível em `http://localhost:8501` por padrão.

## Executando os Testes

Os testes estão localizados no diretório `tests/`. Para executá-los, use o pytest:

```bash
pytest
```

Para executar com cobertura (se o pacote `pytest-cov` estiver instalado):

```bash
pytest --cov=src
```

## Variáveis de Ambiente

O projeto pode utilizar variáveis de ambiente para configuração. Atualmente, não há variáveis obrigatórias, mas verifique o arquivo `.env.example` (se existir) ou o código para quaisquer configurações opcionais.

## Estrutura do Projeto

Uma visão geral da estrutura de diretórios:

```
Dike-/
├── docs/                 # Documentação técnica (este diretório)
├── src/                  # Código-fonte da aplicação
│   ├── core/             # Módulos centrais
│   ├── models/           # Modelos de dados (SQLAlchemy ou classes simples)
│   ├── parsers/          # Parsers para diferentes formatos (XML, JSON, etc.)
│   ├── services/         # Lógica de serviço (processamento, exportação)
│   ├── utils/            # Utilitários auxiliares
│   └── validators/       # Módulos de validação de dados
├── tests/                # Testes automatizados
├── config/               # Arquivos de configuração (esquemas JSON, etc.)
├── requirements.txt      # Dependências do Python
├── main.py               # Ponto de entrada da aplicação Streamlit
└── README.md             # Este arquivo (visão geral do projeto)
```

## Contribuindo

1. Fork o repositório.
2. Crie uma branch para sua feature ou correção: `git checkout -b feature/nome-da-feature`.
3. Faça suas alterações e commit: `git commit -m 'Adiciona alguma feature'`.
4. Push para a branch: `git push origin feature/nome-da-feature`.
5. Abra um Pull Request.

## Suporte

Em caso de dúvidas, consulte o WORKSPACE_GUIDE.md para entender a estrutura de trabalho com agentes ou entre em contato com o time de desenvolvimento.