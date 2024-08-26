import sqlite3

conn = sqlite3.connect('Alexandria1.db')
cursor = conn.cursor()


def criar_tabela():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teste (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        idade INTEGER NOT NULL
    )
    ''')
    conn.commit()

def inserir_dados():
    cursor.execute('''
    INSERT INTO teste (nome, idade)
    VALUES ('João', 25),
           ('Maria', 30),
           ('Pedro', 22)
    ''')
    conn.commit()

def consultar_dados():
    cursor.execute('SELECT * FROM teste')
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def deletar_dados():
    cursor.execute('DELETE FROM teste WHERE nome = "Maria"')
    conn.commit()

def deletar_tabela():
    cursor.execute('DROP table teste')
    conn.commit()



criar_tabela()     
inserir_dados()     
print("Dados inseridos:")
consultar_dados()   

deletar_dados()   
print("\nDados após deleção:")
consultar_dados()
deletar_tabela()


conn.close()
