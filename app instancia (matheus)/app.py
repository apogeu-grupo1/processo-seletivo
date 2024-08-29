from flask import Flask, request, redirect, render_template, url_for
import sqlite3

app = Flask(__name__)


def create_tables(): # Conversando com o dudu vi que tinha que fazer a criação de uma tabela para as 'sessões' para resgatar o cookie de login.
                        # Esse script não precisa ficar aqui, mas deixei nesse app.py apenas para funcionar o teste.
                            # Além disso, ainda falta "integrar" essa rota de instância com a rota do Dudu, que é algo que estou com dificuldade.
    conn = sqlite3.connect('Alexandria1.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessoes (
        sessao_id TEXT PRIMARY KEY,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES clientes(id)
    )
    ''')

    conn.commit()
    conn.close()

create_tables()

def verifica_login(sessao_id): 
    if not sessao_id:
        return None

    conn = sqlite3.connect('Alexandria1.db')
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM sessoes WHERE sessao_id=?", (sessao_id,))
    sessao = cursor.fetchone()

    if sessao:
        user_id = sessao[0]

        cursor.execute("SELECT * FROM clientes WHERE id=?", (user_id,))
        usuario = cursor.fetchone()
    else:
        usuario = None

    conn.close()
    return usuario

def verifica_instancia(uuid_instancia):
    conn = sqlite3.connect('Alexandria1.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM livros WHERE uuid=?", (uuid_instancia,))
    instancia = cursor.fetchone()

    conn.close()
    return instancia

@app.route('/books/<uuid_instancia>')
def instancia_livro(uuid_instancia):
    sessao_id = request.cookies.get('sessao_id')

    usuario = verifica_login(sessao_id)
    if not usuario:
        return redirect(url_for('login'))

    instancia = verifica_instancia(uuid_instancia)
    if not instancia:
        return redirect(url_for('index'))

    return render_template('instancia.html', instancia=instancia, usuario=usuario)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
