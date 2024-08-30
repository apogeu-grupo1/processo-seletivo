import os
import hashlib
import uuid
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)
DATABASE = 'Alexandria.db'

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


@app.route('/', methods=['GET'])
def homepage():
    login_token = session.get('login_token')
    if login_token:
        return render_template('/home')
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def loginPost():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute('''SELECT "UUID Cliente", "Hash Senha Cliente" 
                        FROM Clientes 
                        WHERE "Email Cliente" = ?''', (email,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'E-mail não encontrado!'}), 404

        uuid_cliente, hash_senha_armazenada = result

        if not bcrypt.check_password_hash(hash_senha_armazenada, password):
            return jsonify({'error': 'Senha incorreta!'}), 401

        login_token = str(uuid.uuid4())
        cursor.execute('''UPDATE Clientes SET "Login Token" = ? WHERE "UUID Cliente" = ?''', (login_token, uuid_cliente))
        conn.commit()

        session['login_token'] = login_token
        print(f"Login token stored in session: {login_token}")

        return redirect(url_for('home'))


@app.route('/register', methods=['GET'])
def index():
    return render_template('cadastro.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    insert_cliente(data)
    return jsonify({'message': 'Cadastro realizado com sucesso!'})

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

@app.route('/search')
def search():
    query = request.args.get('q')
    rows = search_books(query)
    data = [{"titulo": row[0], "autor": row[1], "isbn": row[2], "descricao": row[3], "foto": row[4]} for row in rows]
    return render_template('busca-livros.html', data=data)

def get_genero_data(cursor, nome_genero):
    cursor.execute('''
            SELECT Livros."UUID Livro", Livros."Nome Livro", Livros."Autor Livro", Livros."ISBN Livro", Livros."Descricao do Livro", Livros."Foto Capa"
            FROM Livros
            JOIN Generos ON Livros."UUID Genero" = Generos."UUID Genero"
            WHERE Generos."Nome Genero" = ?;
        ''', (nome_genero,))
    return cursor.fetchall()

@app.route('/home')
def home():
    login_token = session.get('login_token')
    if not login_token:
        return redirect(url_for('loginPost'))
    
    cliente_id = '2'  # UUID do cliente atual

    with connect_db() as conn:
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT "Generos Cliente" 
            FROM Clientes 
            WHERE "UUID Cliente" = ?
        ''', (cliente_id,))
        
        generos_cliente = cursor.fetchone()
        lista_generos = generos_cliente[0].split(", ") if generos_cliente else []

        # Obtenha livros para os gêneros preferidos do cliente
        data_genero = [get_genero_data(cursor, genero) for genero in lista_generos[:3]]

    # Preparar os dados para renderização
    data1 = [{"id": row[0], "nome": row[1], "autor": row[2], "ISBN": row[3], "descricao": row[4], "foto": row[5]} for row in data_genero[0]] if len(data_genero) > 0 else []
    data2 = [{"id": row[0], "nome": row[1], "autor": row[2], "ISBN": row[3], "descricao": row[4], "foto": row[5]} for row in data_genero[1]] if len(data_genero) > 1 else []
    data3 = [{"id": row[0], "nome": row[1], "autor": row[2], "ISBN": row[3], "descricao": row[4], "foto": row[5]} for row in data_genero[2]] if len(data_genero) > 2 else []

    return render_template('pagina-inicial.html', data1=data1, data2=data2, data3=data3)

if __name__ == '__main__':
    app.run(debug=True)