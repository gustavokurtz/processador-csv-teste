from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
import io
import os
from typing import Optional
import uuid
import uvicorn

app = FastAPI(
    title="Serviço de Processamento de Dados CSV",
    description="API para manipulação de dados em arquivos CSV e cálculo de notas",
    version="1.0.0",
)

# Pasta para armazenar os arquivos processados
UPLOAD_FOLDER = "processed_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/processar-csv/", summary="Processa arquivo CSV e calcula notas")
async def processar_csv(
    file: UploadFile = File(...),
    coluna_resultado: str = "nota_pesquisa"
):
    """
    Processa um arquivo CSV adicionando uma coluna de nota calculada.
    
    - **file**: Arquivo CSV a ser processado
    - **coluna_resultado**: Nome da coluna a ser adicionada com o resultado (padrão: 'nota_pesquisa')
    
    O sistema detectará automaticamente as colunas de notas em vários formatos:
    - Para a primeira nota: 'nota_1', 'nota1', 'Nota 1', 'Nota1', etc.
    - Para a segunda nota: 'nota_2', 'nota2', 'Nota 2', 'Nota2', etc.
    
    Retorna o arquivo CSV processado.
    """
    try:
        # Verificando extensão do arquivo
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="O arquivo deve ser um CSV")
        
        # Lendo o conteúdo do arquivo
        contents = await file.read()
        
        # Convertendo para DataFrame
        try:
            # Tentar diferentes configurações de leitura para maior robustez
            try:
                # Tentar primeiro com configuração padrão
                df = pd.read_csv(io.BytesIO(contents))
            except Exception as e1:
                try:
                    # Tentar com diferentes separadores
                    for sep in [',', ';', '\t', '|']:
                        try:
                            df = pd.read_csv(io.BytesIO(contents), sep=sep)
                            # Se temos mais de uma coluna, consideramos bem-sucedido
                            if len(df.columns) > 1:
                                print(f"CSV lido com separador: {sep}")
                                break
                        except:
                            continue
                    
                    # Se ainda não conseguimos ler, tentar com mais opções
                    if 'df' not in locals() or len(df.columns) <= 1:
                        df = pd.read_csv(io.BytesIO(contents), sep=None, engine='python')
                except Exception as e2:
                    # Como último recurso, tentar com configurações mais flexíveis
                    df = pd.read_csv(io.BytesIO(contents), sep=None, engine='python', 
                                     on_bad_lines='skip', encoding_errors='ignore')
            
            # Verificar se o DataFrame foi criado corretamente
            if len(df.columns) <= 1:
                raise ValueError("O arquivo parece não ter colunas suficientes ou está malformatado")
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao ler o CSV: {str(e)}")
        
        # Possíveis nomes para as colunas de nota (padrões mais comuns)
        possibilidades_nota1 = ['nota_1', 'nota1', 'Nota_1', 'Nota1', 'Nota 1', 'NOTA_1', 'NOTA1', 'NOTA 1']
        possibilidades_nota2 = ['nota_2', 'nota2', 'Nota_2', 'Nota2', 'Nota 2', 'NOTA_2', 'NOTA2', 'NOTA 2'] 
        
        # Imprime as colunas disponíveis para debug
        print(f"Colunas disponíveis no CSV: {list(df.columns)}")
        
        # Encontrando as colunas de nota no DataFrame (verificação exata)
        coluna_nota1 = None
        for col in possibilidades_nota1:
            if col in df.columns:
                coluna_nota1 = col
                break
                
        coluna_nota2 = None
        for col in possibilidades_nota2:
            if col in df.columns:
                coluna_nota2 = col
                break
        
        # Se não encontrou com verificação exata, tenta uma abordagem mais flexível
        if coluna_nota1 is None or coluna_nota2 is None:
            print("Tentando encontrar colunas de notas com abordagem mais flexível...")
            
            # Tenta encontrar qualquer coluna que contenha "nota" e "1" ou "nota" e "2"
            for col in df.columns:
                col_lower = col.lower()
                if coluna_nota1 is None and ('nota' in col_lower and '1' in col_lower):
                    coluna_nota1 = col
                    print(f"Encontrou coluna para nota 1: {col}")
                if coluna_nota2 is None and ('nota' in col_lower and '2' in col_lower):
                    coluna_nota2 = col
                    print(f"Encontrou coluna para nota 2: {col}")
        
        # Verificando se as colunas foram encontradas
        if coluna_nota1 is None or coluna_nota2 is None:
            # Lista todas as colunas disponíveis no erro para ajudar o usuário
            colunas_disponiveis = ", ".join(df.columns)
            raise HTTPException(
                status_code=400, 
                detail=f"Colunas de notas não encontradas. O CSV deve conter colunas para nota 1 e nota 2. " +
                       f"Colunas disponíveis no seu arquivo: [{colunas_disponiveis}]"
            )
        
        # Limpeza e normalização do DataFrame antes do processamento
        try:
            # 1. Remover linhas completamente vazias
            df = df.dropna(how='all').reset_index(drop=True)
            
            # 2. Detectar o nome da coluna da empresa (geralmente a primeira coluna)
            coluna_empresa = df.columns[0]
            
            # 3. Preencher valores faltantes na coluna da empresa
            # Se uma linha não tem nome de empresa mas tem dados nas outras colunas,
            # preenche com o valor da última linha válida
            ultimo_valor_empresa = None
            for idx in range(len(df)):
                if pd.notna(df.iloc[idx][coluna_empresa]):
                    ultimo_valor_empresa = df.iloc[idx][coluna_empresa]
                elif ultimo_valor_empresa is not None and pd.isna(df.iloc[idx][coluna_empresa]):
                    if not df.iloc[idx].isna().all():  # Se há outros dados na linha
                        df.loc[idx, coluna_empresa] = ultimo_valor_empresa
            
            # 4. Garantir que todas as colunas sejam do tipo adequado
            # Para colunas que devem ser numéricas (qualquer coluna com 'nota' no nome)
            for col in df.columns:
                if 'nota' in col.lower() and col != coluna_resultado:
                    # Converter para string primeiro, substituir vírgulas por pontos, depois para float
                    df[col] = df[col].astype(str).str.replace(',', '.').replace('nan', np.nan)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 5. Remover linhas onde as notas estão vazias (não faz sentido calcular a média)
            df = df.dropna(subset=[coluna_nota1, coluna_nota2]).reset_index(drop=True)
            
            print(f"DataFrame normalizado com sucesso. Formato final: {df.shape}")
        except Exception as e:
            print(f"Erro durante a normalização do DataFrame: {str(e)}")
            # Continuar com o processamento mesmo com erro na normalização

        # Calculando a média e adicionando a coluna
        try:
            # Convertendo as colunas para números, tratando tanto ponto quanto vírgula como separador decimal
            df[coluna_nota1] = df[coluna_nota1].astype(str).str.replace(',', '.').astype(float)
            df[coluna_nota2] = df[coluna_nota2].astype(str).str.replace(',', '.').astype(float)
            
            # Calculando a média e arredondando para 2 casas decimais
            df[coluna_resultado] = ((df[coluna_nota1] + df[coluna_nota2]) / 2).round(2)
            
            # Limpeza final e verificação de consistência
            # 1. Garantir que a coluna de resultado tenha apenas valores válidos
            df[coluna_resultado] = pd.to_numeric(df[coluna_resultado], errors='coerce')
            
            # 2. Verificar consistência entre valores de entrada e resultado
            for idx in range(len(df)):
                if pd.notna(df.iloc[idx][coluna_nota1]) and pd.notna(df.iloc[idx][coluna_nota2]):
                    if pd.isna(df.iloc[idx][coluna_resultado]):
                        # Recalcular se o resultado está vazio mas temos as duas notas
                        valor1 = float(df.iloc[idx][coluna_nota1])
                        valor2 = float(df.iloc[idx][coluna_nota2])
                        df.loc[idx, coluna_resultado] = round((valor1 + valor2) / 2, 2)
            
            # 3. Aplicar formatação consistente (opcional)
            # Garantir que as colunas numéricas tenham o mesmo número de casas decimais
            for col in [coluna_nota1, coluna_nota2, coluna_resultado]:
                if col in df.columns:
                    df[col] = df[col].round(2)
            
            # 4. Organizar colunas em uma ordem lógica
            # Primeiro as colunas de identificação, depois notas, por último o resultado
            colunas_ordenadas = [col for col in df.columns if 'nota' not in col.lower()]
            colunas_notas = [col for col in df.columns if 'nota' in col.lower() and col != coluna_resultado]
            colunas_ordenadas.extend(colunas_notas)
            colunas_ordenadas.append(coluna_resultado)
            
            # Aplicar a ordem apenas para colunas que existem
            colunas_existentes = [col for col in colunas_ordenadas if col in df.columns]
            df = df[colunas_existentes]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao calcular as notas: {str(e)}")
        
        # Gerando nome único para o arquivo processado
        output_filename = f"{uuid.uuid4()}.csv"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Salvando o DataFrame como CSV
        df.to_csv(output_path, index=False)
        
        # Retornando o arquivo processado
        return FileResponse(
            path=output_path, 
            filename=f"processado_{file.filename}",
            media_type="text/csv"
        )
        
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
        raise

@app.get("/", summary="Raiz da API")
async def root():
    """
    Endpoint raiz que exibe uma mensagem de boas-vindas.
    """
    return {
        "mensagem": "API de Processamento de Dados CSV",
        "instrucoes": "Use o endpoint /processar-csv/ para enviar um arquivo CSV e adicionar a coluna de nota calculada."
    }



@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Redireciona para a documentação Swagger
    """
    return FileResponse(path="/docs")


# Ambiente de desenvolvimento
# if __name__ == "__main__":
#     uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

# Ambiente de Prod
if __name__ == "__main__":
   
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    uvicorn.run("app:app", host=host, port=port, reload=True)