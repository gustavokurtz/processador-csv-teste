# Serviço de Processamento de Dados CSV

Este é um serviço web que permite processar arquivos CSV para calcular a média de duas notas e adicionar o resultado como uma nova coluna no arquivo.

## Visão Geral

O serviço foi projetado para ser simples, flexível e fácil de usar. Ele fornece uma API REST com endpoints bem definidos e documentação interativa via Swagger UI.

### Principais Funcionalidades

- Upload de arquivos CSV
- Detecção automática de colunas de notas
- Suporte a diferentes formatos numéricos
- Cálculo e arredondamento da média das notas
- Download do arquivo processado

## Arquitetura

O projeto foi implementado com uma arquitetura minimalista, utilizando os seguintes arquivos principais:

- `app.py`: Contém toda a lógica da aplicação, incluindo os endpoints da API, processamento de dados e cálculos
- `test_app.py`: Contém os testes automatizados para validar o funcionamento da aplicação
- `requirements.txt`: Lista as dependências necessárias

### Decisões Técnicas

1. **Abordagem monolítica simplificada**: 
   - Todo o código está contido em um único arquivo `app.py`, facilitando a manutenção e entendimento
   - Esta abordagem foi escolhida para manter o projeto simples, sem a necessidade de estruturas de projeto complexas
   
2. **Dependências essenciais**:
   - python-multipart: Necessário para processar uploads de arquivos via FastAPI
   - Apenas as dependências estritamente necessárias foram incluídas no requirements.txt
   
2. **FastAPI como framework web**:
   - Escolhido pela sua alta performance, facilidade de uso e documentação automática via Swagger UI
   - Permite definir claramente os endpoints e seus parâmetros

3. **Pandas para manipulação de dados**:
   - Proporciona uma maneira poderosa e eficiente de processar dados tabulares
   - Facilita a leitura, manipulação e escrita de arquivos CSV

4. **Detecção flexível de colunas**:
   - Implementada uma lógica em duas etapas para identificar colunas de notas:
     1. Primeiro tenta encontrar correspondências exatas com nomes predefinidos
     2. Se falhar, usa uma abordagem mais flexível buscando colunas que contenham "nota" e os números "1" ou "2"
   - Esta abordagem permite que o serviço funcione com uma grande variedade de formatos de CSV

5. **Tratamento robusto de formatos numéricos**:
   - Conversão automática de diferentes formatos numéricos:
     - Números com vírgula como separador decimal (ex: "7,5")
     - Números com ponto como separador decimal (ex: "7.5")
     - Números inteiros (ex: "7")
   - Implementada usando `astype(str).str.replace(',', '.').astype(float)`

6. **Arredondamento de resultados**:
   - As médias são arredondadas para 2 casas decimais para evitar problemas de precisão com números de ponto flutuante
   - Implementado usando o método `.round(2)` do pandas

7. **Tratamento de erros**:
   - Implementado um sistema robusto de tratamento de erros com mensagens claras e informativas
   - Quando há erro na detecção de colunas, o sistema informa quais colunas estão disponíveis no arquivo

## Testes

O projeto inclui uma suíte completa de testes automatizados para garantir que todas as funcionalidades estejam funcionando corretamente.

### Abordagem de Testes

Os testes foram implementados usando o framework pytest em conjunto com o TestClient do FastAPI, permitindo testar a API de forma rápida e eficiente, sem a necessidade de iniciar um servidor HTTP real.

### Bibliotecas Utilizadas para Testes

- **pytest**: Framework de testes
- **fastapi.testclient**: Cliente de teste específico para aplicações FastAPI
- **pandas**: Para manipulação e verificação de dados nos testes
- **io**: Biblioteca padrão para manipulação de streams de bytes ao verificar respostas
- **shutil**: Biblioteca padrão para limpeza de arquivos temporários
- **os**: Biblioteca padrão para operações de sistema de arquivos
- **uuid** e **numpy**: Incluídos para compatibilidade com diversas operações

### Casos de Teste Implementados

1. **Teste do endpoint raiz**: Verifica se a API está funcionando corretamente
2. **Teste com arquivo CSV válido**: Verifica o processamento correto de um arquivo com formato padrão
3. **Teste com nomes de colunas diferentes**: Valida a detecção automática de colunas com nomenclaturas variadas
4. **Teste com colunas faltantes**: Verifica se a API retorna erro apropriado quando faltam colunas necessárias
5. **Teste com arquivo inválido**: Confirma que a API rejeita adequadamente arquivos que não são CSV
6. **Teste com números usando vírgulas**: Valida a conversão automática de números com vírgula como separador decimal

### Estrutura de Testes

Os testes utilizam fixtures para criar arquivos CSV temporários com diferentes formatos e configurações, que são então enviados para a API. Os resultados são verificados para garantir que o processamento foi realizado corretamente.

Funções de limpeza garantem que todos os arquivos temporários sejam removidos após a execução dos testes.

### Como Executar os Testes

Os testes são executados diretamente através do script de teste:

```bash
python test_app.py
```

Este comando executará todos os casos de teste e mostrará o status de cada um no terminal.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal
- **FastAPI**: Framework web para construção da API
- **Pandas**: Biblioteca para manipulação de dados
- **Uvicorn**: Servidor ASGI para executar a aplicação
- **python-multipart**: Biblioteca para processamento de formulários/arquivos multipart
- **pytest**: Framework para testes automatizados
- **httpx**: Cliente HTTP para testes de API
- **pytest-asyncio**: Suporte para testes assíncronos

## Como Executar

### Pré-requisitos

- Python 3.13.2 versão utilizada
- Pip (gerenciador de pacotes Python)

### Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

### Execução

Execute o servidor com o seguinte comando:

```bash
python app.py
```

O servidor será iniciado em `http://localhost:8000`

### Uso da API

1. Acesse a documentação Swagger UI em `http://localhost:8000/docs`
2. Use o endpoint `/processar-csv/` para enviar um arquivo CSV
3. O sistema processará o arquivo e retornará a versão processada com a nova coluna de média

## Formatos Suportados

### Nomes de Colunas

O sistema detecta automaticamente colunas de notas nos seguintes formatos:

- Para a primeira nota: `nota_1`, `nota1`, `Nota 1`, `Nota1`, etc.
- Para a segunda nota: `nota_2`, `nota2`, `Nota 2`, `Nota2`, etc.

### Formatos Numéricos

O sistema aceita os seguintes formatos numéricos:

- Números com vírgula como separador decimal: `7,5`
- Números com ponto como separador decimal: `7.5`
- Números inteiros: `7`

## Exemplos de Uso

### Exemplo de CSV de Entrada

```csv
nome,nota 1,nota 2
Ana Silva,8,5
João Santos,6,9
Maria Oliveira,7,8
```

### Exemplo de CSV de Saída

```csv
nome,nota 1,nota 2,nota_pesquisa
Ana Silva,8,5,6.5
João Santos,6,9,7.5
Maria Oliveira,7,8,7.5
```

## Considerações Finais

Este serviço foi projetado para ser simples, mas robusto o suficiente para lidar com diferentes formatos de dados. A abordagem minimalista facilita a manutenção e entendimento do código, enquanto as funcionalidades implementadas atendem às necessidades de processamento de notas em arquivos CSV.