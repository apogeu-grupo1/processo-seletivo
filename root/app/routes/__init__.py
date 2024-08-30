import uuid
from flask import render_template, request, jsonify, redirect, session, url_for
from app import app, bcrypt
from app.models import get_foto_cliente, insert_cliente, search_books, get_genero_data, connect_db

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
    query = request.args.get('q')
    rows = search_books(query)
    data = [{"titulo": row[0], "autor": row[1], "isbn": row[2], "descricao": row[3], "foto": row[4]} for row in rows]
    return render_template('busca-livros.html', data=data)

@app.route('/home')
def home():
    login_token = session.get('login_token')
    cliente_id = session.get('cliente_id')  # Recupera o UUID do cliente da sessão
    
    
    if not login_token:
        return redirect(url_for('loginPost'))

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT "Generos Cliente" 
            FROM Clientes 
            WHERE "UUID Cliente" = ?
        ''', (cliente_id,))

        generos_cliente = cursor.fetchone()
        lista_generos = generos_cliente[0].split(", ") if generos_cliente else []
        foto_cliente = get_foto_cliente(cursor, cliente_id)
        # Obtenha livros para os gêneros preferidos do cliente
        data_genero = [get_genero_data(cursor, genero) for genero in lista_generos[:3]]
        print(foto_cliente)
    # Preparar os dados para renderização
    data1 = [{"id": row[0], "nome": row[1], "autor": row[2], "ISBN": row[3], "descricao": row[4], "foto": row[5]} for row in data_genero[0]] if len(data_genero) > 0 else []
    data2 = [{"id": row[0], "nome": row[1], "autor": row[2], "ISBN": row[3], "descricao": row[4], "foto": row[5]} for row in data_genero[1]] if len(data_genero) > 1 else []
    data3 = [{"id": row[0], "nome": row[1], "autor": row[2], "ISBN": row[3], "descricao": row[4], "foto": row[5]} for row in data_genero[2]] if len(data_genero) > 2 else []

    return render_template('pagina-inicial.html', data1=data1, data2=data2, data3=data3, foto_cliente=foto_cliente)