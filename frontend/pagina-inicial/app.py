from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

DATABASE = 'Alexandria1.db'

def connect_db():
    return sqlite3.connect(DATABASE)

@app.route('/home')
def index():
    query = '2' #UUID_CLiente#

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
            SELECT "UUID CLiente", "Generos Cliente" 
            FROM Clientes 
            WHERE "UUID CLiente" = ?
        ''', ('%' + query + '%'))
    
    rows = cursor.fetchall()
    conn.close()

    data = [{"id": row[0], "generos": row[1]} for row in rows]

    print(data.id + "\n")
    print(data.generos)
    
    return render_template('pagina-inicial.html', data=data)

    
if __name__ == '__main__':
    app.run(debug=True)