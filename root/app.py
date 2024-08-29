from flask import Flask, redirect, render_template, request, jsonify
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

DATABASE = 'Alexandria.db'

def connect_db():
    return sqlite3.connect(DATABASE)


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
    senha = data.get('senha')
    hash_senha = bcrypt.generate_password_hash(senha).decode('utf-8')

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Clientes 
            ("Nome Cliente", "Email Cliente", "Telefone Cliente", "Username Cliente", "Pais Cliente", "Estado Cliente","Cidade Cliente",  "Generos Cliente", "Foto Cliente", "Hash Senha Cliente")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (nome, email, telefone, username, pais, estado, cidade, generosPreferidos, fotoCliente, hash_senha))
        conn.commit()

    return jsonify({'message': 'Cadastro realizado com sucesso!'})


@app.route('/search')
def search():
    query = request.args.get('q')

    conn = connect_db()
    cursor = conn.cursor()

    if query:
        cursor.execute('''
            SELECT "Nome Livro", "Autor Livro", "ISBN Livro", "Descricao do Livro", "Foto Capa" 
            FROM Livros 
            WHERE "Nome Livro" LIKE ? OR "Autor Livro" LIKE ?
        ''', ('%' + query + '%', '%' + query + '%'))
    else:
        cursor.execute('SELECT "Nome Livro", "Autor Livro", "ISBN Livro", "Descricao do Livro", "Foto Capa" FROM Livros')
        
    rows = cursor.fetchall()
    conn.close()

    data = [{"titulo": row[0], "autor": row[1], "isbn": row[2], "descricao": row[3], "foto": row[4]} for row in rows]

    return render_template('busca-livros.html', data=data)
    

@app.route('/home')
def home():
    query = '2'  # UUID_CLiente#

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
            SELECT "Generos Cliente" 
            FROM Clientes 
            WHERE "UUID Cliente" = ?
        ''', (query,))
    
    rows = cursor.fetchall()
    if not rows:
        conn.close()
        return render_template('pagina-inicial.html', data1=[], data2=[], data3=[], genero1=[], genero2=[], genero3=[])

    generos_cliente = rows[0][0]
    lista_generos = generos_cliente.split(", ") if generos_cliente else []

    def get_genero_data(nome_genero):
        cursor.execute('''
                SELECT "UUID Genero", "Nome Genero"
                FROM Generos
                WHERE "Nome Genero" = ?
            ''', (nome_genero,))
    
        rows = cursor.fetchall()
        print(rows)
        return [{"id_genero": row[0], "nome": row[1]} for row in rows]

    data_genero1 = get_genero_data(lista_generos[0]) if len(lista_generos) > 0 else []
    data_genero2 = get_genero_data(lista_generos[1]) if len(lista_generos) > 1 else []
    data_genero3 = get_genero_data(lista_generos[2]) if len(lista_generos) > 2 else []

    uuid_genero1 = data_genero1[0]["id_genero"] if data_genero1 else None
    uuid_genero2 = data_genero2[0]["id_genero"] if data_genero2 else None
    uuid_genero3 = data_genero3[0]["id_genero"] if data_genero3 else None

    def get_livros_data(uuid_genero):
        if uuid_genero:
            cursor.execute('''
                    SELECT "UUID Livro", "Nome Livro", "Autor Livro", "ISBN Livro", "UUID Genero", "Descricao do Livro", "Foto Capa"
                    FROM Livros
                    WHERE "UUID Genero" = ?
                ''', (uuid_genero,))
    
            rows = cursor.fetchall()
            print(rows)
            return [{"id": row[0], "nome": row[1], "autor": row[2], "ISBN": row[3], "id-genero": row[4], "descricao": row[5], "foto": row[6]} for row in rows]
        return []

    data_genero_livros1 = get_livros_data(uuid_genero1)
    data_genero_livros2 = get_livros_data(uuid_genero2)
    data_genero_livros3 = get_livros_data(uuid_genero3)
    
    conn.close()

    return render_template('pagina-inicial.html', genero1=data_genero1, genero2=data_genero2, genero3=data_genero3, data1=data_genero_livros1, data2=data_genero_livros2, data3=data_genero_livros3)

if __name__ == '__main__':
    app.run(debug=True)