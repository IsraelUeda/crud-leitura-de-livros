from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            status TEXT NOT NULL,
            nota INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


@app.route('/')
def index():
    conn = get_db_connection()
    livros = conn.execute('SELECT * FROM livros ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', livros=livros)


@app.route('/criar', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        autor = request.form.get('autor', '').strip()
        status = request.form.get('status', '').strip()
        nota = request.form.get('nota', '').strip()

        if not titulo or not autor or not status:
            erro = 'Preencha todos os campos obrigatórios.'
            return render_template('criar.html', erro=erro, titulo=titulo, autor=autor, status=status, nota=nota)

        try:
            nota_val = int(nota) if nota else None
        except ValueError:
            erro = 'Nota deve ser um número inteiro entre 0 e 10.'
            return render_template('criar.html', erro=erro, titulo=titulo, autor=autor, status=status, nota=nota)

        conn = get_db_connection()
        conn.execute('INSERT INTO livros (titulo, autor, status, nota) VALUES (?, ?, ?, ?)',
                     (titulo, autor, status, nota_val))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('criar.html')


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    livro = conn.execute('SELECT * FROM livros WHERE id = ?', (id,)).fetchone()

    if livro is None:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        autor = request.form.get('autor', '').strip()
        status = request.form.get('status', '').strip()
        nota = request.form.get('nota', '').strip()

        if not titulo or not autor or not status:
            erro = 'Preencha todos os campos obrigatórios.'
            conn.close()
            return render_template('editar.html', livro=livro, erro=erro)

        try:
            nota_val = int(nota) if nota else None
        except ValueError:
            erro = 'Nota deve ser um número inteiro entre 0 e 10.'
            conn.close()
            return render_template('editar.html', livro=livro, erro=erro)

        conn.execute('UPDATE livros SET titulo = ?, autor = ?, status = ?, nota = ? WHERE id = ?',
                     (titulo, autor, status, nota_val, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('editar.html', livro=livro)


@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM livros WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
