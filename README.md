# Serviço de Processamento de Dados CSV

Este projeto foi desenvolvido como parte de um desafio técnico, com o objetivo de criar um serviço web para processar arquivos CSV, calculando a média de duas notas e adicionando o resultado como uma nova coluna.

## O que o projeto faz

O serviço web permite:
- Fazer upload de arquivos CSV contendo dados com colunas de notas
- Detectar automaticamente as colunas de notas, mesmo com nomenclaturas variadas
- Calcular a média entre as duas notas
- Adicionar uma nova coluna com o resultado calculado
- Baixar o arquivo processado com a nova coluna

## Por que criei assim

Ao iniciar este projeto, meu objetivo principal era criar uma solução robusta e eficiente, sem adicionar complexidade desnecessária. Optei por uma abordagem minimalista, mantendo todo o código no arquivo `app.py` para facilitar a manutenção e o entendimento.

### Decisões técnicas que tomei

1. **Escolha do FastAPI:**
   - Escolhi o FastAPI por sua alta performance, facilidade de uso e documentação automática via Swagger
   - A sintaxe limpa e moderna do FastAPI permite definir claramente os endpoints e seus parâmetros
   - A documentação automática facilita o teste e a utilização da API

2. **Por que monolítico:**
   - Decidi manter a estrutura simples com todo o código em um único arquivo
   - Para um projeto deste escopo, uma estrutura mais complexa seria desnecessária
   - A manutenção se torna mais direta com menos arquivos para navegar

3. **Pandas para processamento de dados:**
   - Pandas é a biblioteca mais poderosa para manipulação de dados tabulares em Python
   - Oferece alto desempenho para operações em conjuntos de dados
   - A familiaridade com a API do Pandas me permitiu implementar o processamento de forma eficiente

4. **Algoritmo de detecção flexível:**
   - Implementei uma detecção em duas etapas para as colunas de notas:
     1. Primeiro tenta correspondências exatas com nomes conhecidos
     2. Se falhar, adota uma abordagem mais flexível com correspondências parciais
   - Esta abordagem permite que o serviço funcione com uma grande variedade de formatos de CSV

5. **Tratamento de diferentes formatos numéricos:**
   - Adicionei suporte para diferentes representações de números:
     - Números com vírgula como separador decimal (formato brasileiro)
     - Números com ponto como separador decimal (formato internacional)
     - Números inteiros
   - Isso torna o serviço mais flexível para uso em diferentes contextos culturais

6. **Robustez no tratamento de erros:**
   - Implementei mensagens de erro claras e informativas
   - Quando ocorre um erro na detecção de colunas, o sistema informa quais colunas estão disponíveis
   - Adicionei validações em diferentes etapas do processamento para capturar problemas o mais cedo possível

## Tecnologias utilizadas

- **Python 3.13.2** - Linguagem de programação principal
- **FastAPI** - Framework web para construção da API
- **Pandas** - Biblioteca para manipulação de dados
- **Uvicorn** - Servidor ASGI para execução da aplicação
- **python-multipart** - Para processamento de formulários/arquivos multipart
- **pytest** - Framework para testes automatizados
- **httpx** - Cliente HTTP para testes de API

## Como executar o projeto

### Pré-requisitos

- Python 3.13.2 ou superior
- Pip (gerenciador de pacotes Python)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/gustavokurtz/processador-csv-teste.git
cd processador-csv-teste
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executando a aplicação

Para iniciar o servidor:

```bash
python app.py
```

O servidor estará disponível em `http://localhost:8000`

### Como usar a API

1. Acesse a documentação Swagger em `http://localhost:8000/docs`
2. Use o endpoint `/processar-csv/` para enviar um arquivo CSV
3. A API processará o arquivo e retornará a versão com a nova coluna de média

## Como testei a aplicação

O projeto inclui testes automatizados abrangentes. Implementei testes para verificar:

- Funcionamento básico da API
- Processamento correto de arquivos CSV
- Detecção automática de colunas com nomenclaturas variadas
- Tratamento adequado de erros quando faltam colunas
- Rejeição de arquivos inválidos
- Conversão correta de diferentes formatos numéricos

Para executar os testes:

```bash
python test_app.py
```

## Desafios e soluções

Durante o desenvolvimento, enfrentei alguns desafios interessantes:

1. **Detecção de colunas**: Criei um sistema em duas etapas que primeiro tenta encontrar nomes exatos e depois utiliza uma abordagem mais flexível.

2. **Tratamento de formatos numéricos**: Implementei uma solução que converte automaticamente números com vírgula ou ponto como separador decimal.

3. **Robustez de leitura CSV**: Adicionei múltiplas tentativas com diferentes configurações para garantir que o CSV seja lido corretamente, independente do formato.

## Possíveis melhorias futuras

Se tivesse mais tempo, consideraria implementar:

- Suporte a mais operações além da média (soma, min, max, etc.)
- Interface web simples para upload e visualização dos dados
- Opção para processar múltiplos arquivos em lote
- Persistência de dados em um banco de dados
- Análises estatísticas mais avançadas

## Formatos suportados

### Nomes de colunas detectados automaticamente

- Primeira nota: `nota_1`, `nota1`, `Nota 1`, `Nota1`, etc.
- Segunda nota: `nota_2`, `nota2`, `Nota 2`, `Nota2`, etc.

### Formatos numéricos suportados

- Números com vírgula: `7,5`
- Números com ponto: `7.5`
- Números inteiros: `7`

## Exemplo

**Entrada (CSV):**
```csv
nome,nota 1,nota 2
Ana Silva,8,5
João Santos,6,9
Maria Oliveira,7,8
```

**Saída (CSV):**
```csv
nome,nota 1,nota 2,nota_pesquisa
Ana Silva,8,5,6.5
João Santos,6,9,7.5
Maria Oliveira,7,8,7.5
```
