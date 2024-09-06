import datetime
from flask import Flask, flash, render_template, request, jsonify, redirect, session, url_for
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
    uuid_cliente = str(uuid.uuid4())

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Clientes 
            ("UUID Cliente", "Nome Cliente", "Email Cliente", "Telefone Cliente", "Username Cliente", "Pais Cliente", "Estado Cliente",
            "Cidade Cliente", "Generos Cliente", "Foto Cliente", "Hash Senha Cliente")
            VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (uuid_cliente, nome, email, telefone, username, pais, estado, cidade, generosPreferidos, fotoCliente, hash_senha))
        conn.commit()

def search_books(query=None):
    with connect_db() as conn:
        cursor = conn.cursor()
        if query:
            cursor.execute('''
                SELECT Livros."Nome Livro", Livros."Autor Livro", Livros."ISBN Livro", Livros."Descricao do Livro", Livros."Foto Capa", Instancias."UUID Instancia" 
                FROM Instancias
                JOIN Livros ON Instancias."UUID Livro" = Livros."UUID Livro" 
                Join Generos ON Livros."UUID Genero" = Generos."UUID Genero"
                WHERE "Nome Genero" = ? OR "Nome Livro" LIKE ? OR "Autor Livro" LIKE ? AND Instancias."Status Instancia" = 'Disponível';
            ''', (query, '%' + query + '%', '%' + query + '%'))
        else:
            cursor.execute('SELECT Livros."Nome Livro", Livros."Autor Livro", Livros."ISBN Livro", Livros."Descricao do Livro", Livros."Foto Capa", Instancias."UUID Instancia" FROM Instancias JOIN Livros ON Instancias."UUID Livro" = Livros."UUID Livro" ')
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
    return [row[0] for row in cursor.fetchall()]

def get_data_instancia(cursor, uuid_instancia):
    cursor.execute('''
            SELECT Livros."Nome Livro", Livros."Autor Livro", Livros."Descricao do Livro", Livros."Foto Capa", Generos."Nome Genero", Instancias."UUID Instancia", Clientes."Foto CLiente", Clientes."UUID CLiente", Clientes."Username Cliente", Clientes."Telefone Cliente"
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

def get_minhas_instancias(cursor, uuid_cliente):
    cursor.execute('''
            SELECT Livros."Nome Livro", Instancias."UUID Instancia", Livros."Foto Capa"
            FROM Instancias
            JOIN Livros ON Instancias."UUID Livro" = Livros."UUID Livro"
            WHERE Instancias."UUID CLiente" = ?
        ''', (uuid_cliente,))
    return cursor.fetchall()

def get_transacoes_data(cursor, uuid_cliente):
    cursor.execute('''
            SELECT Transações."UUID Transacao", inst1."UUID Instancia", inst2."UUID Instancia", livros1."Foto Capa", livros2."Foto Capa"
            FROM Transações
            JOIN Instancias AS inst1 ON Transações."UUID Instancia livro1" = inst1."UUID Instancia"
			JOIN Instancias AS inst2 ON Transações."UUID Instancia livro2" = inst2."UUID Instancia"
			JOIN Livros AS livros1 ON inst1."UUID Livro" = livros1."UUID Livro"
			JOIN Livros AS livros2 ON inst2."UUID Livro" = livros2."UUID Livro"
			WHERE inst1."UUID Cliente" = ? AND Transações."Status Transacao" = 'Pendente'
        ''', (uuid_cliente,))
    
    rows = cursor.fetchall()
    data = [{"uuid_transacao": row[0], "uuid_instancia_1": row[1], "uuid_instancia_2": row[2], "foto_capa_livro_1": row[3], "foto_capa_livro_2": row[4]} for row in rows]
    return data

# Rotas da aplicação
@app.route('/', methods=['GET'])
def homepage():
    if 'login_token' in session:
        login_token = session['login_token']
    else:
        login_token = None
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
    if request.method == 'POST':
            login_token = session['login_token']
            cliente_id = session['cliente_id']  # Recupera o UUID do cliente da sessão
            if not login_token:
                # Remove os dados da sessão corretamente
                session.pop('login_token', None)  # Remove o login_token da sessão
                session.pop('cliente_id', None)   # Remove o cliente_id da sessão

                # Cria a resposta de redirecionamento para a homepage
                resp = redirect(url_for('homepage'))

                # Opcional: Apaga cookies específicos, caso eles tenham sido criados
                resp.delete_cookie('login_token')  # Apaga o cookie de login_token
                resp.delete_cookie('cliente_id')   # Apaga o cookie de cliente_id
                
                return resp  # Retorna a resposta com os cookies apagados 
    
    cliente_id = session['cliente_id']

    with connect_db() as conn:
        cursor = conn.cursor()
        foto_cliente = get_foto_cliente(cursor,cliente_id)[0]
        lista_generos = get_all_generos(cursor)

    query = request.args.get('q')
    rows = search_books(query)
    data = [{"titulo": row[0], "autor": row[1], "isbn": row[2], "descricao": row[3], "foto": row[4], "uuid_instancia": row[5]} for row in rows]
    
    return render_template('busca-livros.html', data=data, foto_cliente=foto_cliente,lista_generos=lista_generos)

@app.route('/home')
def home():
    login_token = session['login_token']
    cliente_id = session['cliente_id']  # Recupera o UUID do cliente da sessão
    
    if not login_token:
        # Remove os dados da sessão corretamente
        session.pop('login_token', None)  # Remove o login_token da sessão
        session.pop('cliente_id', None)   # Remove o cliente_id da sessão

        # Cria a resposta de redirecionamento para a homepage
        resp = redirect(url_for('homepage'))

        # Opcional: Apaga cookies específicos, caso eles tenham sido criados
        resp.delete_cookie('login_token')  # Apaga o cookie de login_token
        resp.delete_cookie('cliente_id')   # Apaga o cookie de cliente_id
        
        return resp  # Retorna a resposta com os cookies apagados

    
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

@app.route('/books/<UUID_Instancia>', methods=['GET', 'POST'])
def books(UUID_Instancia):
    cliente_id = session['cliente_id']
    
    with connect_db() as conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            login_token = session['login_token']
            cliente_id = session['cliente_id']  # Recupera o UUID do cliente da sessão
            if not login_token:
                # Remove os dados da sessão corretamente
                session.pop('login_token', None)  # Remove o login_token da sessão
                session.pop('cliente_id', None)   # Remove o cliente_id da sessão

                # Cria a resposta de redirecionamento para a homepage
                resp = redirect(url_for('homepage'))

                # Opcional: Apaga cookies específicos, caso eles tenham sido criados
                resp.delete_cookie('login_token')  # Apaga o cookie de login_token
                resp.delete_cookie('cliente_id')   # Apaga o cookie de cliente_id
                
                return resp  # Retorna a resposta com os cookies apagados


            uuid_instancia_livro_2 = request.form['livro_nome']
            uuid_instancia_livro_1 = request.form['uuid_instancia_livro_1']
            data_atual = datetime.datetime.now()
            data_cadastro_troca = data_atual.strftime("%d/%m/%Y")
            uuid_transacao = str(uuid.uuid4())
            try:
            
                cursor.execute('''
                    INSERT INTO Transações ("UUID Transacao", "UUID Instancia livro1", "UUID Instancia livro2", "Data Transaçao","Status Transacao")
                    VALUES (?, ?, ?, ?,?)
                ''', (uuid_transacao, uuid_instancia_livro_1, uuid_instancia_livro_2, data_cadastro_troca, 'Pendente'))
            
                conn.commit()

                flash('Proposta de troca enviada com sucesso!', 'success')
            except Exception as e:
                # Define uma mensagem de erro
                flash('Erro ao enviar a proposta de troca. Tente novamente.', 'danger')
                print(e)

            
            return redirect(url_for('books', UUID_Instancia=UUID_Instancia))

        
        data = get_data_instancia(cursor, UUID_Instancia)
        foto_cliente = get_foto_cliente(cursor, cliente_id)[0]
        all_generos = get_all_generos(cursor)
        client_books = get_minhas_instancias(cursor, cliente_id)
        data_Instancia = [{"nome_livro": row[0], "autor_livro": row[1], "descricao_livro": row[2], "foto_livro": row[3], "genero_livro": row[4], "uuid_instancia": row[5], "foto_cliente": row[6], "uuid_cliente": row[7], "username_cliente": row[8], "telefone_cliente": row[9]} for row in data]
    
    return render_template('instancia.html', data_Instancia=data_Instancia, foto_cliente=foto_cliente, all_generos=all_generos, client_books=client_books)

@app.route('/cadastro_instancia', methods=['GET'])
def cadastro_instanciaGet():
    login_token = session['login_token']
    
    if not login_token:
        return redirect(url_for('loginPost'))
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        livros = getBooks(cursor)
    print(livros)
    return render_template('cadastro_instancia.html', livros= livros)

@app.route('/cadastro_instancia', methods=['POST'])
def cadastro_instanciaPost():
    cliente_id = session['cliente_id']
    uuid_instancia = str(uuid.uuid4())
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
        cursor.execute('''INSERT INTO Instancias ("UUID Instancia", "UUID Livro", "UUID Cliente", "Data Cadastro Instancia", "Status instancia")
                            VALUES (?, ?, ?, ?, ?)''', (uuid_instancia,uuid_livro[0], uuid_cliente, data_cadastro_instancia, status_instancia))
        conn.commit()
        livros = getBooks(cursor)
       
        

    return redirect(url_for('books', UUID_Instancia=uuid_instancia))

@app.route('/perfil', methods=['GET'])
def perfilGet():
    cliente_id = session['cliente_id']

    with connect_db() as conn:
        cursor = conn.cursor()

    foto_cliente = get_foto_cliente(cursor, cliente_id)[0]
    data = get_minhas_instancias(cursor,cliente_id)
    all_generos = get_all_generos(cursor)
    transacao = get_transacoes_data(cursor, cliente_id)
    print(transacao)
    
    return render_template('perfil.html', foto_cliente=foto_cliente, data=data, all_generos=all_generos, transacao=transacao)

@app.route('/perfil', methods=['POST'])
def perfilPost():
    # Remove os dados da sessão corretamente
    session.pop('login_token', None)  # Remove o login_token da sessão
    session.pop('cliente_id', None)   # Remove o cliente_id da sessão
    
    # Cria a resposta de redirecionamento
    resp = redirect(url_for('homepage'))  # Redireciona para a homepage

    # Opcional: Apagar cookies específicos, caso você tenha cookies personalizados
    resp.delete_cookie('login_token')  # Apaga o cookie de login_token se ele existir
    resp.delete_cookie('cliente_id')   # Apaga o cookie de cliente_id se ele existir
    
    return resp


@app.route('/aceitar_proposta', methods=['POST'])
def aceitar_proposta():
    uuid_transacao = request.form['uuid_transacao']
    uuid_instancia_1 = request.form['uuid_instancia_1']
    uuid_instancia_2 = request.form['uuid_instancia_2']

    
    with connect_db() as conn:
        cursor = conn.cursor()

    
    cursor.execute('UPDATE Transações SET "Status Transacao" = "Aceita" WHERE "UUID Transacao" = ?', (uuid_transacao,))
    
    
    cursor.execute('''
            UPDATE Transações SET "Status Transacao" = "Cancelada" 
            WHERE "UUID Instancia livro1" = ? OR "UUID Instancia livro2" = ? OR "UUID Instancia livro2" = ? OR "UUID Instancia livro1" = ? AND "Status Transacao" = 'Pendente'
        ''', (uuid_instancia_1, uuid_instancia_2, uuid_instancia_2, uuid_instancia_1))
    conn.commit()

    return redirect(url_for('perfilGet'))


@app.route('/recusar_proposta', methods=['POST'])
def recusar_proposta():
    uuid_transacao = request.form['uuid_transacao']

    with connect_db() as conn:
        cursor = conn.cursor()

    
    cursor.execute('UPDATE Transações SET "Status Transacao" = "Recusada" WHERE "UUID Transacao" = ?', (uuid_transacao,))
    conn.commit()

    return redirect(url_for('perfilGet'))

# Execução da aplicação
if __name__ == '__main__':
    app.run(debug=True)