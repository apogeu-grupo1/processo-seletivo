import datetime
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from flask_bcrypt import Bcrypt
import sqlite3
import os
import uuid

# Configuração da aplicação Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)

# Conexão com o banco de dados
DATABASE = 'Alexandria.db'

def connect_db():
    return sqlite3.connect(DATABASE)

# Funções de manipulação do banco de dados
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
            SELECT Livros."UUID Livro", Livros."Nome Livro", Livros."Autor Livro", Livros."ISBN Livro", Livros."Descricao do Livro", Livros."Foto Capa",Instancias."UUID Instancia"
            FROM Instancias
            JOIN Livros ON Instancias."UUID Livro" = Livros."UUID Livro"
            JOIN Generos ON Livros."UUID Genero" = Generos."UUID Genero"
            WHERE Generos."Nome Genero" = ? AND Instancias."Status Instancia" = 'Disponível';
        ''', (nome_genero,))
    return cursor.fetchall()

def get_foto_cliente(cursor, uuid_cliente):
    cursor.execute('''
            SELECT "Foto Cliente"
            FROM Clientes
            WHERE "UUID Cliente" = ?
        ''', (uuid_cliente,))
    return cursor.fetchone()

def get_generos_cliente(cursor, cliente_id):
        cursor.execute('''
            SELECT "Generos Cliente" 
            FROM Clientes 
            WHERE "UUID Cliente" = ?
        ''', (cliente_id,))

        generos_cliente = cursor.fetchone()
        
        return generos_cliente[0].split(", ") if generos_cliente else []

def get_all_generos(cursor):
    cursor.execute('SELECT "Nome Genero" FROM Generos')
    return cursor.fetchall()

def get_data_instancia(cursor, uuid_instancia):
    cursor.execute('''
            SELECT Livros."Nome Livro", Livros."Autor Livro", Livros."Descricao do Livro", Livros."Foto Capa", Generos."Nome Genero", Instancias."UUID Instancia", Clientes."Foto CLiente"
            FROM Instancias
            JOIN Livros ON Instancias."UUID Livro" = Livros."UUID Livro"
            JOIN Generos ON Livros."UUID Genero" = Generos."UUID Genero"
            JOIN Clientes ON Instancias."UUID Cliente" = Clientes."UUID Cliente"
            WHERE Instancias."UUID Instancia" = ?;
        ''', (uuid_instancia,))
    
    return cursor.fetchall()

def getBooks(cursor):
    cursor.execute('SELECT "Nome Livro" FROM Livros')
    return cursor.fetchall()

def getUuidBook(cursor,livro):
    cursor.execute('SELECT "UUID Livro" FROM Livros WHERE "Nome Livro"=?', (livro,))
    return cursor.fetchone()


# Rotas da aplicação
@app.route('/', methods=['GET'])
def homepage():
    login_token = session.get('login_token')
    if login_token:
        return redirect(url_for('home'))
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def loginPost():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    with connect_db() as conn:
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

        # Gera o login token e armazena na sessão
        login_token = str(uuid.uuid4())
        cursor.execute('''UPDATE Clientes SET "Login Token" = ? WHERE "UUID Cliente" = ?''', (login_token, uuid_cliente))
        conn.commit()

        session['login_token'] = login_token
        session['cliente_id'] = uuid_cliente  # Armazena o UUID do cliente na sessão
        print(f"Login token stored in session: {login_token}")
        print(f"Cliente ID stored in session: {uuid_cliente}")

        return redirect(url_for('home'))

@app.route('/register', methods=['GET'])
def index():
    return render_template('cadastro.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    insert_cliente(data)
    return jsonify({'message': 'Cadastro realizado com sucesso!'})

@app.route('/search')
def search():
    cliente_id = session.get('cliente_id')

    with connect_db() as conn:
        cursor = conn.cursor()
        foto_cliente = get_foto_cliente(cursor,cliente_id)[0]
        lista_generos = get_all_generos(cursor)

    query = request.args.get('q')
    rows = search_books(query)
    data = [{"titulo": row[0], "autor": row[1], "isbn": row[2], "descricao": row[3], "foto": row[4]} for row in rows]
    
    return render_template('busca-livros.html', data=data, foto_cliente=foto_cliente,lista_generos=lista_generos)

@app.route('/home')
def home():
    login_token = session.get('login_token')
    cliente_id = session.get('cliente_id')  # Recupera o UUID do cliente da sessão
    
    if not login_token:
        return redirect(url_for('loginPost'))

    #FUNCAO GET_GENEROS_CLIENTE ***********************************
    with connect_db() as conn:
        cursor = conn.cursor()
        
        lista_generos = get_generos_cliente(cursor, cliente_id)
        foto_cliente = get_foto_cliente(cursor, cliente_id)[0]
        # Obtenha livros para os gêneros preferidos do cliente
        data_genero = [get_genero_data(cursor, genero) for genero in lista_generos[:3]]
        all_generos = get_all_generos(cursor)

    # Preparar os dados para renderização
    data1 = [{"id": row[0], "nome": row[1], "autor": row[2], "ISBN": row[3], "descricao": row[4], "foto": row[5], "uuid_instancia": row[6]} for row in data_genero[0]] if len(data_genero) > 0 else []
    data2 = [{"id": row[0], "nome": row[1], "autor": row[2], "ISBN": row[3], "descricao": row[4], "foto": row[5], "uuid_instancia": row[6]} for row in data_genero[1]] if len(data_genero) > 1 else []
    data3 = [{"id": row[0], "nome": row[1], "autor": row[2], "ISBN": row[3], "descricao": row[4], "foto": row[5], "uuid_instancia": row[6]} for row in data_genero[2]] if len(data_genero) > 2 else []

    return render_template('pagina-inicial.html', data1=data1, data2=data2, data3=data3, foto_cliente=foto_cliente, lista_generos=lista_generos, all_generos=all_generos)

@app.route('/books/<UUID_Instancia>')
def books(UUID_Instancia):
    cliente_id = session.get('cliente_id')
    
    with connect_db() as conn:
        cursor = conn.cursor()
        
        data = get_data_instancia(cursor, UUID_Instancia)
        foto_cliente = get_foto_cliente(cursor,cliente_id)[0]
        all_generos = get_all_generos(cursor)
        data_Instancia = [{"nome_livro": row[0], "autor_livro": row[1], "descricao_livro": row[2], "foto_livro": row[3], "genero_livro": row[4], "uuid_instancia": row[5], "foto_cliente": row[6]} for row in data]
    
    
    return render_template('instancia.html', data_Instancia=data_Instancia, foto_cliente=foto_cliente, all_generos=all_generos)

@app.route('/cadastro_instancia', methods=['GET'])
def cadastro_instanciaGet():
    login_token = session.get('login_token')
    
    if not login_token:
        return redirect(url_for('loginPost'))
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        livros = getBooks(cursor)
    print(livros)
    return render_template('cadastro_instancia.html', livros= livros)

@app.route('/cadastro_instancia', methods=['POST'])
def cadastro_instanciaPost():
    cliente_id = session.get('cliente_id')
    
    dataCadastro = request.json
    nome_livro = dataCadastro['livro_nome']
    data_atual = datetime.datetime.now()
    uuid_cliente = cliente_id
    data_cadastro_instancia = data_atual.strftime("%d/%m/%Y")
    status_instancia = dataCadastro['status']
    #imagem_instancia = request.files['imagem'].read() if 'imagem' in request.files else None
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        uuid_livro = getUuidBook(cursor,nome_livro)
        cursor.execute('''INSERT INTO Instancias ("UUID Livro", "UUID Cliente", "Data Cadastro Instancia", "Status instancia")
                            VALUES (?, ?, ?, ?)''', (uuid_livro[0], uuid_cliente, data_cadastro_instancia, status_instancia))
        conn.commit()
        livros = getBooks(cursor)
        uuid_instancia = cursor.lastrowid
        

    return redirect(url_for('books', UUID_Instancia=uuid_instancia))

# Execução da aplicação
if __name__ == '__main__':
    app.run(debug=True)