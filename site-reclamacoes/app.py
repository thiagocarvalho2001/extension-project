from flask import Response, Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DATABASE = {
    'dbname': os.getenv('dbname'),
    'user': os.getenv('user',),
    'password': os.getenv('password'),
    'host': os.getenv('host'),
    'port': os.getenv('port')
}


def get_db_connection():
    return psycopg2.connect(**DATABASE)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/reclamacoes', methods=['GET', 'POST'])
def listar_reclamacoes():
    conn = get_db_connection()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        email = request.form['email']
        imagem = request.files['imagem']

        cur = conn.cursor()
        cur.execute('INSERT INTO reclamacoes (titulo, descricao, email, imagem) VALUES (%s, %s, %s, %s)',
                    (titulo, descricao, email, imagem.read()))
        conn.commit()
        cur.close()

        return redirect(url_for('listar_reclamacoes'))

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM reclamacoes ORDER BY id DESC;')
    reclamacoes = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('reclamacoes.html', reclamacoes=reclamacoes)


@app.route('/imagem/<int:id>')
def exibir_imagem(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute('SELECT imagem FROM reclamacoes WHERE id = %s;', (id,))
    resultado = cur.fetchone()

    cur.close()
    conn.close()

    if resultado and resultado['imagem']:
        imagem_bytes = resultado['imagem']
        return Response(imagem_bytes, mimetype='image/jpeg')
    else:
        return "Imagem não encontrada", 404


if __name__ == '__main__':
    app.run(debug=True)
