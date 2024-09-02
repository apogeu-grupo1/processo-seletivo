import sqlite3
import hashlib
import os
import uuid
from flask_bcrypt import Bcrypt
from flask import Flask, request, jsonify, redirect, url_for, render_template, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'Alexandria1.db'
bcrypt = Bcrypt(app)

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Clientes (
            "UUID Cliente" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Nome Cliente" TEXT,
            "Email Cliente" TEXT NOT NULL,
            "Username Cliente" TEXT,
            "Hash Senha Cliente" TEXT,
            "Cidade Cliente" TEXT,
            "Estado Cliente" TEXT,
            "Pais Cliente" TEXT,
            "Generos Cliente" TEXT,
            "Telefone Cliente" TEXT,
            "Foto Cliente" BLOB,
            "Login Token" TEXT
        )''')
        conn.commit()

@app.route('/login', methods=['GET'])
def loginGet():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def loginPost():
    dataLogin = request.json
    email = dataLogin.get('email')
    password = dataLogin.get('password')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Verifica se o email existe na base
        cursor.execute('''SELECT "UUID Cliente", "Hash Senha Cliente" FROM Clientes WHERE "Email Cliente" = ?''', (email,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'E-mail não encontrado!'}), 404

        uuid_cliente, hash_senha_armazenada = result  
        # Verifica se o hash da senha inserida é igual ao hash armazenado
        #hash_senha_inserida = bcrypt.generate_password_hash(password).decode('utf-8')
        hash_senha_inserida = '$2b$12$EjCFeWMMUtA0HHb5Z.Hi9OAIiMLli.SsjRMrACUkU2idA05Ba0lji'
        if hash_senha_armazenada != hash_senha_inserida:
            return jsonify({'error': 'Senha incorreta!'}), 401

        # Gera um cookie de login (token de login)
        login_token = str(uuid.uuid4())
        # Armazena o token no banco de dados
        cursor.execute('''UPDATE Clientes SET "Login Token" = ? WHERE "UUID Cliente" = ?''', (login_token, uuid_cliente))
        conn.commit()

        # Armazena o token na sessão
        session['login_token'] = login_token

        # Redireciona para a página inicial
        return redirect(url_for('homepage'))

@app.route('/', methods=['GET'])
def homepage():    
    if 'login_token' in session and session['login_token']:
        login_token = session['login_token']
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            # Buscar o cliente com o token armazenado
            cursor.execute('''SELECT "UUID Cliente" FROM Clientes WHERE "Login Token" = ?''', (login_token,))
            result = cursor.fetchone()
            if result:
                # Token é válido e encontrado no banco de dados
                return "Olá mundo!"
            else:
                # Token inválido, redirecionar para a página de login
                return redirect(url_for('loginPost'))
    else:
        # Sem token na sessão, redirecionar para a página de login
        return redirect(url_for('loginPost'))

@app.route('/perfil', methods=['GET'])
def perfilGet():
    if 'login_token' in session and session['login_token']:
        login_token = session['login_token']
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            # Buscar o cliente com o token armazenado
            cursor.execute('''SELECT "UUID Cliente" FROM Clientes WHERE "Login Token" = ?''', (login_token,))
            result = cursor.fetchone()
            if result:
                # Token é válido e encontrado no banco de dados
                return render_template('perfil.html')
            else:
                # Token inválido, redirecionar para a página de login
                return redirect(url_for('loginPost'))
    else:
        # Sem token na sessão, redirecionar para a página de login
        return redirect(url_for('loginPost'))

@app.route('/instancia', methods=['GET'])
def instanciaGet():
    if 'login_token' in session and session['login_token']:
        login_token = session['login_token']
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            # Buscar o cliente com o token armazenado
            cursor.execute('''SELECT "UUID Cliente" FROM Clientes WHERE "Login Token" = ?''', (login_token,))
            result = cursor.fetchone()
            if result:
                # Token é válido e encontrado no banco de dados
                return render_template('instancia.html')
            else:
                # Token inválido, redirecionar para a página de login
                return redirect(url_for('loginPost'))
    else:
        # Sem token na sessão, redirecionar para a página de login
        return redirect(url_for('loginPost'))

@app.route('/busca-livros', methods=['GET'])
def buscaGet():
    if 'login_token' in session and session['login_token']:
        login_token = session['login_token']
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            # Buscar o cliente com o token armazenado
            cursor.execute('''SELECT "UUID Cliente" FROM Clientes WHERE "Login Token" = ?''', (login_token,))
            result = cursor.fetchone()
            if result:
                # Token é válido e encontrado no banco de dados
                return render_template('busca-livros.html')
            else:
                # Token inválido, redirecionar para a página de login
                return redirect(url_for('loginPost'))
    else:
        # Sem token na sessão, redirecionar para a página de login
        return redirect(url_for('loginPost'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)