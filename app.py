from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
import json
import time
import urllib.parse
import urllib.request
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError(
        'DATABASE_URL must be set to a PostgreSQL URL, e.g. '
        'postgresql://user:password@host:port/dbname'
    )
if DATABASE_URL.startswith('sqlite'):
    raise RuntimeError('SQLite is not supported in this deployment. Please set DATABASE_URL to PostgreSQL.')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Livro(Base):
    __tablename__ = 'livros'
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(Text, nullable=False)
    autor = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    nota = Column(Integer)
    paginas = Column(Integer)
    isbn = Column(Text)
    ano = Column(Integer)
    capa_url = Column(Text)
    pdf_path = Column(Text)
    cor = Column(Text)


def init_db():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as error:
        raise RuntimeError(
            'Unable to initialize the PostgreSQL database. '
            'Confirm that PostgreSQL is running and DATABASE_URL is correct. '
            f'Original error: {error}'
        ) from error


@app.route('/')
def index():
    session = SessionLocal()
    try:
        livros = session.query(Livro).order_by(Livro.id.desc()).all()
        livros = [livro.__dict__ for livro in livros]
        for l in livros:
            l.pop('_sa_instance_state', None)
        return render_template('index.html', livros=livros)
    finally:
        session.close()


@app.route('/estante')
def estante():
    session = SessionLocal()
    try:
        livros = []
        for livro in session.query(Livro).order_by(Livro.id.desc()).all():
            livro_data = livro.__dict__.copy()
            livro_data.pop('_sa_instance_state', None)
            if livro.pdf_path:
                livro_data['pdfUrl'] = url_for('pdf_view', id=livro.id)
                livro_data['pdfName'] = os.path.basename(livro.pdf_path)
            else:
                livro_data['pdfUrl'] = ''
                livro_data['pdfName'] = ''
            livros.append(livro_data)
        return render_template('estante.html', livros=livros)
    finally:
        session.close()


@app.route('/estante/api/livros', methods=['POST'])
def estante_api_add():
    titulo = request.form.get('titulo', '').strip()
    autor = request.form.get('autor', '').strip()
    cor = request.form.get('color', '').strip()
    if not titulo or not autor:
        return jsonify({'success': False, 'error': 'Título e autor são obrigatórios.'}), 400

    arquivo = request.files.get('pdf')
    filename = None
    pdf_name = None
    if arquivo and arquivo.filename and allowed_file(arquivo.filename):
        pdf_name = arquivo.filename
        filename = secure_filename(f"{int(time.time())}_{arquivo.filename}")
        arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    session = SessionLocal()
    try:
        novo = Livro(
            titulo=titulo,
            autor=autor,
            status='Quero ler',
            nota=None,
            paginas=None,
            isbn=None,
            ano=None,
            capa_url=None,
            pdf_path=filename,
            cor=cor or None
        )
        session.add(novo)
        session.commit()
        session.refresh(novo)
        livro_data = {
            'id': novo.id,
            'title': novo.titulo,
            'author': novo.autor,
            'color': novo.cor or '',
            'pdfUrl': url_for('pdf_view', id=novo.id) if novo.pdf_path else '',
            'pdfName': pdf_name or ''
        }
        return jsonify({'success': True, 'book': livro_data})
    finally:
        session.close()


@app.route('/estante/api/deletar/<int:id>', methods=['POST'])
def estante_api_deletar(id):
    session = SessionLocal()
    try:
        livro = session.query(Livro).filter(Livro.id == id).first()
        if livro is None:
            return jsonify({'success': False, 'error': 'Livro não encontrado.'}), 404
        if livro.pdf_path:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], livro.pdf_path))
            except OSError:
                pass
        session.delete(livro)
        session.commit()
        return jsonify({'success': True})
    finally:
        session.close()


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

        session = SessionLocal()
        try:
            novo = Livro(
                titulo=titulo,
                autor=autor,
                status=status,
                nota=nota_val,
                paginas=paginas_val,
                isbn=isbn or None,
                ano=ano_val,
                capa_url=capa_url or None,
                pdf_path=None
            )
            session.add(novo)
            session.commit()
            return redirect(url_for('index'))
        finally:
            session.close()

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

    session = SessionLocal()
    try:
        novo = Livro(
            titulo=titulo,
            autor=autor,
            status=status,
            nota=nota_val,
            paginas=paginas_val,
            isbn=isbn or None,
            ano=ano_val,
            capa_url=capa_url or None,
            pdf_path=None
        )
        session.add(novo)
        session.commit()
        return redirect(url_for('index'))
    finally:
        session.close()


@app.route('/detalhes/<int:id>')
def detalhes(id):
    session = SessionLocal()
    try:
        livro = session.query(Livro).filter(Livro.id == id).first()
        if livro is None:
            return redirect(url_for('index'))
        return render_template('detalhes.html', livro=livro)
    finally:
        session.close()


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    session = SessionLocal()
    try:
        livro = session.query(Livro).filter(Livro.id == id).first()

        if livro is None:
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
                return render_template('editar.html', livro=livro, erro=erro)

            nota_val = int(nota) if nota.isdigit() else None
            paginas_val = int(paginas) if paginas.isdigit() else None
            ano_val = int(ano) if ano.isdigit() else None

            livro.titulo = titulo
            livro.autor = autor
            livro.status = status
            livro.nota = nota_val
            livro.paginas = paginas_val
            livro.isbn = isbn or None
            livro.ano = ano_val
            livro.capa_url = capa_url or None
            session.commit()
            return redirect(url_for('index'))

        return render_template('editar.html', livro=livro)
    finally:
        session.close()


@app.route('/upload_pdf/<int:id>', methods=['POST'])
def upload_pdf(id):
    session = SessionLocal()
    try:
        livro = session.query(Livro).filter(Livro.id == id).first()
        if livro is None:
            return redirect(url_for('index'))

        arquivo = request.files.get('pdf')
        if arquivo and allowed_file(arquivo.filename):
            filename = secure_filename(f'{id}_{arquivo.filename}')
            destino = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            arquivo.save(destino)
            livro.pdf_path = filename
            session.commit()
        return redirect(url_for('detalhes', id=id))
    finally:
        session.close()


@app.route('/pdf/<int:id>')
def pdf_view(id):
    session = SessionLocal()
    try:
        livro = session.query(Livro).filter(Livro.id == id).first()
        if livro is None or not livro.pdf_path:
            return redirect(url_for('detalhes', id=id))
        return send_from_directory(app.config['UPLOAD_FOLDER'], livro.pdf_path)
    finally:
        session.close()


@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    session = SessionLocal()
    try:
        livro = session.query(Livro).filter(Livro.id == id).first()
        if livro and livro.pdf_path:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], livro.pdf_path))
            except OSError:
                pass
        if livro:
            session.delete(livro)
            session.commit()
        return redirect(url_for('index'))
    finally:
        session.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
