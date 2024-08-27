from flask import Flask, render_template, request, jsonify
import sqlite3
import base64

app = Flask(__name__)

# Configurar o banco de dados
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

@app.route('/')
def index():
    return render_template('cadastro.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    telefone = data.get('telefone')
    username = data.get('username')
    pais = data.get('pais')
    estado = data.get('estado')
    cidade = data.get('cidade')
    generosPreferidos = data.get('generosPreferidos')
    fotoCliente = data.get('fotoCliente')


    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Clientes 
            ("Nome Cliente", "Email Cliente", "Telefone Cliente", "Username Cliente", "Pais Cliente", "Estado Cliente","Cidade Cliente",  "Generos Cliente", "Foto Cliente")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (nome, email, telefone, username, pais, estado, cidade, generosPreferidos, fotoCliente))
        conn.commit()

    return jsonify({'message': 'Cadastro realizado com sucesso!'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)