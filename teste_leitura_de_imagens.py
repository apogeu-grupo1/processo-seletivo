import sqlite3
import requests

conn = sqlite3.connect('Alexandria1.db')
cursor = conn.cursor()

def criar_tabela():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teste (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        idade INTEGER NOT NULL,
        foto BLOB
    )
    ''')
    conn.commit()

def baixar_imagem_da_internet(url):
    response = requests.get(url)
    response.raise_for_status() 
    return response.content

def converter_imagem_binario(caminho_imagem):
    with open(caminho_imagem, 'rb') as arquivo:
        return arquivo.read()

def limpar_tabela():                        # as imagens estavam duplicando então criei essa função pra evitar isso
    cursor.execute('DELETE FROM teste')
    conn.commit()

def inserir_imagem_internet(nome, idade, url_imagem): # fiz outra função apenas para os testes ficarem explicitamente divididos (um teste para ler imagem já no diretório e outro para pegar imagem da internet)
    imagem_binaria = baixar_imagem_da_internet(url_imagem)
    cursor.execute('''
    INSERT INTO teste (nome, idade, foto)
    VALUES (?, ?, ?)
    ''', (nome, idade, imagem_binaria))
    conn.commit()

def inserir_dados(nome, idade, caminho_imagem):
    imagem_binaria = converter_imagem_binario(caminho_imagem)
    cursor.execute('''
    INSERT INTO teste (nome, idade, foto)
    VALUES (?, ?, ?)
    ''', (nome, idade, imagem_binaria))
    conn.commit()

def consultar_dados():
    cursor.execute('SELECT id, nome, idade, foto FROM teste')
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Nome: {row[1]}, Idade: {row[2]}")
        if row[3]:
            with open(f"imagem_{row[0]}.png", 'wb') as file:
                file.write(row[3])
            print(f"Imagem do ID {row[0]} salva como imagem_{row[0]}.png")


criar_tabela()
limpar_tabela()  
inserir_dados('Matheus', 25, 'perfil.png')
inserir_imagem_internet('Botsa', 15, 'https://static.vecteezy.com/ti/vetor-gratis/p3/11186876-simbolo-de-foto-de-perfil-masculino-vetor.jpg')

print("Dados inseridos:")
consultar_dados()

conn.close()
