import sqlite3
import hashlib
import os
import uuid
from flask import Flask, request, jsonify, redirect, url_for, render_template

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'Alexandria1.db'

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
            "Foto Cliente" BLOB
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
        cursor.execute('''SELECT "Hash Senha Cliente" FROM Clientes WHERE "Email Cliente" = ?''', (email,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'E-mail não encontrado!'}), 404

        hash_senha_armazenada = result

        # Verifica se o hash da senha inserida é igual ao hash armazenado
        #hash_senha_inserida = hashlib.sha256(password.encode()).hexdigest()
        hash_senha_inserida = "$2b$12$EjCFeWMMUtA0HHb5Z.Hi9OAIiMLli.SsjRMrACUkU2idA05Ba0lji"
        """if hash_senha_inserida != hash_senha_armazenada:
            return jsonify({'error': 'Senha incorreta!'}), 401"""

        # Redireciona para a página inicial
        return redirect("http://www.google.com", code=307)
    


@app.route('/', methods=['GET'])
def homepage():
    return "Bem-vindo à página inicial!"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
