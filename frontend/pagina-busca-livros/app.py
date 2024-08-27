from flask import Flask, render_template, request
import sqlite3


app = Flask(__name__)

DATABASE = 'Alexandria1.db'

def connect_db():
    return sqlite3.connect(DATABASE)


@app.route('/search')
def index():
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

@app.route('/books/<UUID_Instancia>')

def teste(UUID_Instancia):

    query = UUID_Instancia

    conn = connect_db()
    cursor = conn.cursor()

    if query:
        cursor.execute('SELECT "UUID Livro","Nome Livro", "Autor Livro", "ISBN Livro", "Descricao do Livro", "Foto Capa" FROM Livros WHERE "UUID Livro" = ?', '%' + query + '%')
    else:
        cursor.execute('SELECT "Nome Livro", "Autor Livro", "ISBN Livro", "Descricao do Livro", "Foto Capa" FROM Livros')
        
    rows = cursor.fetchall()
    conn.close()

    data = [{"titulo": row[0], "autor": row[1], "isbn": row[2], "descricao": row[3], "foto": row[4]} for row in rows]

    return render_template('busca-livros.html', data=data)    
    return f"{UUID_Instancia}"

if __name__ == '__main__':
    app.run(debug=True)
