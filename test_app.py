import os
import pytest
from fastapi.testclient import TestClient
import pandas as pd
import io
import shutil
import uuid  # Adicionado para compatibilidade
import numpy as np  # Adicionado para compatibilidade
from app import app, UPLOAD_FOLDER

# Cliente de teste
client = TestClient(app)

# Criar diretório de testes se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Função para criar um arquivo CSV de teste
def create_test_csv(filename, data=None):
    if data is None:
        # Dados de exemplo para teste
        data = {
            'Empresa': ['Empresa A', 'Empresa B', 'Empresa C'],
            'nota_1': [7.5, 8.0, 6.5],
            'nota_2': [8.5, 7.0, 9.0]
        }
    
    df = pd.DataFrame(data)
    csv_path = os.path.join(os.path.dirname(__file__), filename)
    df.to_csv(csv_path, index=False)
    return csv_path

# Limpar arquivos após os testes
def teardown_module():
    try:
        # Remover arquivos de teste
        for file in os.listdir():
            if file.endswith('.csv') and file.startswith('test_'):
                os.remove(file)
        
        # Limpar pasta de arquivos processados
        if os.path.exists(UPLOAD_FOLDER):
            shutil.rmtree(UPLOAD_FOLDER)
            os.makedirs(UPLOAD_FOLDER)
    except Exception as e:
        print(f"Erro ao limpar arquivos: {e}")

# Testes
def test_root_endpoint():
    """Teste do endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "mensagem" in response.json()
    assert "API de Processamento de Dados CSV" in response.json()["mensagem"]

def test_process_csv_valid_file():
    """Teste com arquivo CSV válido"""
    # Criar arquivo de teste
    test_file = create_test_csv('test_valid.csv')
    
    # Abrir o arquivo e enviar para o endpoint
    with open(test_file, 'rb') as f:
        response = client.post(
            "/processar-csv/",
            files={"file": ("test_valid.csv", f, "text/csv")},
            params={"coluna_resultado": "nota_final"}
        )
    
    # Verificar resposta
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    # Verificar conteúdo do CSV retornado
    content = response.content
    df = pd.read_csv(io.BytesIO(content))
    
    # Verificar se a coluna de resultado foi criada
    assert "nota_final" in df.columns
    
    # Verificar cálculos
    for i in range(len(df)):
        nota1 = df.iloc[i]["nota_1"]
        nota2 = df.iloc[i]["nota_2"]
        nota_final = df.iloc[i]["nota_final"]
        # Considerando arredondamento para 2 casas decimais
        assert round((nota1 + nota2) / 2, 2) == nota_final

def test_process_csv_different_column_names():
    """Teste com nomes de colunas diferentes"""
    # Dados com nomes de colunas diferentes
    data = {
        'Empresa': ['Empresa X', 'Empresa Y', 'Empresa Z'],
        'Nota1': [7.5, 8.0, 6.5],
        'Nota2': [8.5, 7.0, 9.0]
    }
    
    test_file = create_test_csv('test_different_columns.csv', data)
    
    with open(test_file, 'rb') as f:
        response = client.post(
            "/processar-csv/",
            files={"file": ("test_different_columns.csv", f, "text/csv")}
        )
    
    assert response.status_code == 200
    content = response.content
    df = pd.read_csv(io.BytesIO(content))
    assert "nota_pesquisa" in df.columns  # Coluna padrão

def test_process_csv_missing_columns():
    """Teste com colunas faltantes"""
    # Dados sem colunas de notas
    data = {
        'Empresa': ['Empresa X', 'Empresa Y', 'Empresa Z'],
        'Outra_Coluna': [1, 2, 3]
    }
    
    test_file = create_test_csv('test_missing_columns.csv', data)
    
    with open(test_file, 'rb') as f:
        response = client.post(
            "/processar-csv/",
            files={"file": ("test_missing_columns.csv", f, "text/csv")}
        )
    
    # Deve retornar erro 400
    assert response.status_code == 400
    assert "Colunas de notas não encontradas" in response.json()["detail"]

def test_process_csv_invalid_file():
    """Teste com arquivo inválido (não CSV)"""
    # Criar arquivo de texto simples
    with open('test_invalid.txt', 'w') as f:
        f.write("Este não é um arquivo CSV")
    
    with open('test_invalid.txt', 'rb') as f:
        response = client.post(
            "/processar-csv/",
            files={"file": ("test_invalid.txt", f, "text/plain")}
        )
    
    # Deve retornar erro 400
    assert response.status_code == 400
    assert "O arquivo deve ser um CSV" in response.json()["detail"]

def test_process_csv_with_commas():
    """Teste com números contendo vírgulas como separador decimal"""
    # Dados com vírgulas como separador decimal
    data = {
        'Empresa': ['Empresa A', 'Empresa B', 'Empresa C'],
        'nota_1': ['7,5', '8,0', '6,5'],
        'nota_2': ['8,5', '7,0', '9,0']
    }
    
    test_file = create_test_csv('test_commas.csv', data)
    
    with open(test_file, 'rb') as f:
        response = client.post(
            "/processar-csv/",
            files={"file": ("test_commas.csv", f, "text/csv")}
        )
    
    assert response.status_code == 200
    content = response.content
    df = pd.read_csv(io.BytesIO(content))
    
    # Verificar se converteu corretamente
    assert df.iloc[0]["nota_pesquisa"] == 8.0  # (7.5 + 8.5) / 2
    assert df.iloc[1]["nota_pesquisa"] == 7.5  # (8.0 + 7.0) / 2
    assert df.iloc[2]["nota_pesquisa"] == 7.75  # (6.5 + 9.0) / 2

# Executar os testes se o script for chamado diretamente
if __name__ == "__main__":
    # Configuração para teste manual
    print("Iniciando testes da API de processamento CSV...")
    
    # Executar os testes
    test_root_endpoint()
    print("✅ Teste do endpoint raiz passou!")
    
    test_process_csv_valid_file()
    print("✅ Teste com arquivo CSV válido passou!")
    
    test_process_csv_different_column_names()
    print("✅ Teste com nomes de colunas diferentes passou!")
    
    try:
        test_process_csv_missing_columns()
        print("✅ Teste com colunas faltantes passou!")
    except Exception as e:
        print(f"❌ Teste com colunas faltantes falhou: {e}")
    
    try:
        test_process_csv_invalid_file()
        print("✅ Teste com arquivo inválido passou!")
    except Exception as e:
        print(f"❌ Teste com arquivo inválido falhou: {e}")
    
    test_process_csv_with_commas()
    print("✅ Teste com números usando vírgulas passou!")
    
    # Limpeza
    teardown_module()
    print("🧹 Limpeza concluída!")
    
    print("Testes finalizados!")