import sqlite3
from app import bcrypt

DATABASE = 'instance/Alexandria.db'

def connect_db():
    return sqlite3.connect(DATABASE)

def insert_cliente(data):
    nome = data.get('nome')
    email = data.get('email')
    telefone = data.get('telefone')
    username = data.get('username')
    pais = data.get('pais')
    estado = data.get('estado')
    cidade = data.get('cidade')
    generosPreferidos = data.get('generosPreferidos')
    fotoCliente = data.get('fotoCliente')
    senha = data.get('senha')
    hash_senha = bcrypt.generate_password_hash(senha).decode('utf-8')

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Clientes 
            ("Nome Cliente", "Email Cliente", "Telefone Cliente", "Username Cliente", "Pais Cliente", "Estado Cliente",
            "Cidade Cliente", "Generos Cliente", "Foto Cliente", "Hash Senha Cliente")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (nome, email, telefone, username, pais, estado, cidade, generosPreferidos, fotoCliente, hash_senha))
        conn.commit()

def search_books(query=None):
    with connect_db() as conn:
        cursor = conn.cursor()
        if query:
            cursor.execute('''
                SELECT "Nome Livro", "Autor Livro", "ISBN Livro", "Descricao do Livro", "Foto Capa" 
                FROM Livros 
                WHERE "Nome Livro" LIKE ? OR "Autor Livro" LIKE ?
            ''', ('%' + query + '%', '%' + query + '%'))
        else:
            cursor.execute('SELECT "Nome Livro", "Autor Livro", "ISBN Livro", "Descricao do Livro", "Foto Capa" FROM Livros')
        return cursor.fetchall()

def get_genero_data(cursor, nome_genero):
    cursor.execute('''
            SELECT Livros."UUID Livro", Livros."Nome Livro", Livros."Autor Livro", Livros."ISBN Livro", Livros."Descricao do Livro", Livros."Foto Capa"
            FROM Livros
            JOIN Generos ON Livros."UUID Genero" = Generos."UUID Genero"
            WHERE Generos."Nome Genero" = ?;
        ''', (nome_genero,))
    return cursor.fetchall()

def get_foto_cliente(cursor, uuid_cliente):
    cursor.execute('''
            SELECT "Foto Cliente"
            FROM Clientes
            WHERE "UUID CLiente" = ?
        ''', (uuid_cliente,))
    return cursor.fetchall()