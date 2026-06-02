from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
import json
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    conn = get_db_connection()
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            status TEXT NOT NULL,
            nota INTEGER,
            paginas INTEGER,
            isbn TEXT,
            ano INTEGER,
            capa_url TEXT,
            pdf_path TEXT
        )
        '''
    )
    conn.commit()
    conn.close()


@app.route('/')
def index():
    conn = get_db_connection()
    livros = conn.execute('SELECT * FROM livros ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', livros=livros)


@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        autor = request.form.get('autor', '').strip()
        status = request.form.get('status', '').strip()
        nota = request.form.get('nota', '').strip()
        paginas = request.form.get('paginas', '').strip()
        isbn = request.form.get('isbn', '').strip()
        ano = request.form.get('ano', '').strip()
        capa_url = request.form.get('capa_url', '').strip()

        if not titulo or not autor or not status:
            erro = 'Preencha título, autor e status.'
            return render_template('adicionar.html', erro=erro, titulo=titulo, autor=autor, status=status, nota=nota, paginas=paginas, isbn=isbn, ano=ano, capa_url=capa_url)

        nota_val = int(nota) if nota.isdigit() else None
        paginas_val = int(paginas) if paginas.isdigit() else None
        ano_val = int(ano) if ano.isdigit() else None

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO livros (titulo, autor, status, nota, paginas, isbn, ano, capa_url, pdf_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (titulo, autor, status, nota_val, paginas_val, isbn or None, ano_val, capa_url or None, None)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('adicionar.html')


@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultados = []
    query = ''
    erro = None

    if request.method == 'POST':
        query = request.form.get('titulo', '').strip()
        if not query:
            erro = 'Digite um título para pesquisar.'
        else:
            url = f'https://openlibrary.org/search.json?{urllib.parse.urlencode({'title': query})}'
            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    dados = json.loads(response.read())
                for item in dados.get('docs', [])[:20]:
                    resultados.append({
                        'titulo': item.get('title'),
                        'autor': ', '.join(item.get('author_name', [])) if item.get('author_name') else 'Desconhecido',
                        'paginas': item.get('number_of_pages_median'),
                        'ano': item.get('first_publish_year'),
                        'isbn': item.get('isbn', [None])[0],
                        'capa_url': f"https://covers.openlibrary.org/b/id/{item['cover_i']}-M.jpg" if item.get('cover_i') else None,
                    })
            except Exception:
                erro = 'Não foi possível buscar resultados. Tente novamente.'

    return render_template('buscar.html', resultados=resultados, query=query, erro=erro)


@app.route('/importar', methods=['POST'])
def importar():
    titulo = request.form.get('titulo', '').strip()
    autor = request.form.get('autor', '').strip()
    status = request.form.get('status', 'Quero ler').strip()
    nota = request.form.get('nota', '').strip()
    paginas = request.form.get('paginas', '').strip()
    isbn = request.form.get('isbn', '').strip()
    ano = request.form.get('ano', '').strip()
    capa_url = request.form.get('capa_url', '').strip()

    if not titulo or not autor:
        return redirect(url_for('buscar'))

    nota_val = int(nota) if nota.isdigit() else None
    paginas_val = int(paginas) if paginas.isdigit() else None
    ano_val = int(ano) if ano.isdigit() else None

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO livros (titulo, autor, status, nota, paginas, isbn, ano, capa_url, pdf_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (titulo, autor, status, nota_val, paginas_val, isbn or None, ano_val, capa_url or None, None)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/detalhes/<int:id>')
def detalhes(id):
    conn = get_db_connection()
    livro = conn.execute('SELECT * FROM livros WHERE id = ?', (id,)).fetchone()
    conn.close()
    if livro is None:
        return redirect(url_for('index'))
    return render_template('detalhes.html', livro=livro)


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
        paginas = request.form.get('paginas', '').strip()
        isbn = request.form.get('isbn', '').strip()
        ano = request.form.get('ano', '').strip()
        capa_url = request.form.get('capa_url', '').strip()

        if not titulo or not autor or not status:
            erro = 'Preencha título, autor e status.'
            conn.close()
            return render_template('editar.html', livro=livro, erro=erro)

        nota_val = int(nota) if nota.isdigit() else None
        paginas_val = int(paginas) if paginas.isdigit() else None
        ano_val = int(ano) if ano.isdigit() else None

        conn.execute(
            'UPDATE livros SET titulo = ?, autor = ?, status = ?, nota = ?, paginas = ?, isbn = ?, ano = ?, capa_url = ? WHERE id = ?',
            (titulo, autor, status, nota_val, paginas_val, isbn or None, ano_val, capa_url or None, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('editar.html', livro=livro)


@app.route('/upload_pdf/<int:id>', methods=['POST'])
def upload_pdf(id):
    conn = get_db_connection()
    livro = conn.execute('SELECT * FROM livros WHERE id = ?', (id,)).fetchone()
    if livro is None:
        conn.close()
        return redirect(url_for('index'))

    arquivo = request.files.get('pdf')
    if arquivo and allowed_file(arquivo.filename):
        filename = secure_filename(f'{id}_{arquivo.filename}')
        destino = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        arquivo.save(destino)
        conn.execute('UPDATE livros SET pdf_path = ? WHERE id = ?', (filename, id))
        conn.commit()
    conn.close()
    return redirect(url_for('detalhes', id=id))


@app.route('/pdf/<int:id>')
def pdf_view(id):
    conn = get_db_connection()
    livro = conn.execute('SELECT * FROM livros WHERE id = ?', (id,)).fetchone()
    conn.close()
    if livro is None or not livro['pdf_path']:
        return redirect(url_for('detalhes', id=id))
    return send_from_directory(app.config['UPLOAD_FOLDER'], livro['pdf_path'])


@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    conn = get_db_connection()
    livro = conn.execute('SELECT * FROM livros WHERE id = ?', (id,)).fetchone()
    if livro and livro['pdf_path']:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], livro['pdf_path']))
        except OSError:
            pass
    conn.execute('DELETE FROM livros WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
