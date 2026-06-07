"""
Simple migration script: copies rows from the local SQLite database to the target DATABASE_URL
Set environment variable DATABASE_URL to your Postgres URL before running.
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

SQLITE = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database.db')}"
PG = os.environ.get('DATABASE_URL')
if not PG:
    print('Please set DATABASE_URL environment variable (postgresql://user:pass@host:port/dbname)')
    exit(1)

engine_sqlite = create_engine(SQLITE)
engine_pg = create_engine(PG)

SessionSQLite = sessionmaker(bind=engine_sqlite)
SessionPG = sessionmaker(bind=engine_pg)

def rows_from_sqlite():
    s = SessionSQLite()
    try:
        result = s.execute(text('SELECT * FROM livros'))
        res = result.mappings().all()
        valid = {'id', 'titulo', 'autor', 'status', 'nota', 'paginas', 'isbn', 'ano', 'capa_url', 'pdf_path', 'cor'}
        cols = [c for c in result.keys() if c in valid]
        return res, cols
    finally:
        s.close()

def insert_into_pg(rows, cols):
    s = SessionPG()
    try:
        s.execute(text('TRUNCATE TABLE livros RESTART IDENTITY CASCADE'))
        for r in rows:
            data = {c: r[c] for c in cols}
            # use simple insert; if table doesn't exist, create with SQLAlchemy beforehand
            placeholders = ','.join(':' + c for c in cols)
            sql = text(f"INSERT INTO livros ({','.join(cols)}) VALUES ({placeholders})")
            s.execute(sql, data)
        s.commit()
    finally:
        s.close()

if __name__ == '__main__':
    rows, cols = rows_from_sqlite()
    if not rows:
        print('No rows found in SQLite database.')
    else:
        print(f'Migrating {len(rows)} rows...')
        insert_into_pg(rows, cols)
        print('Done.')
