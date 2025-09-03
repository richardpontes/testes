import os
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, UTC  # Python 3.11+
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DB_URL = os.getenv("SUPABASE_DB_URL")
if not DB_URL:
    raise RuntimeError("❌ SUPABASE_DB_URL não definida!")

def check_table_exists() -> bool:
    try:
        with psycopg2.connect(DB_URL) as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'projects'
                );
            """)
            exists = cur.fetchone()[0]
            if not exists:
                logger.error("❌ Tabela 'projects' não existe.")
            return bool(exists)
    except psycopg2.Error as e:
        logger.error(f"❌ Erro ao verificar tabela: {e}")
        return False

def insert_projects_batch():
    """Insere vários projetos de uma vez e retorna (id, name)"""
    rows = [
        ("Sistema de Agendamento", "Plataforma para marcar aulas e treinos", datetime.now(UTC)),
        ("API Financeira",        "Serviço REST para processar transações", datetime.now(UTC)),
        ("Dashboard Analytics",   "Painel de BI com gráficos interativos",  datetime.now(UTC)),
        ("E-commerce",            "Loja virtual com integração de pagamentos", datetime.now(UTC)),
        ("Chatbot IA",            "Assistente virtual para suporte ao cliente", datetime.now(UTC)),
    ]

    sql = """
        INSERT INTO public.projects (name, description, created_at)
        VALUES %s
        RETURNING id, name;
    """

    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        with conn, conn.cursor() as cur:
            execute_values(cur, sql, rows)   # um único INSERT (...),(...),(...) + RETURNING
            inserted = cur.fetchall()
            # conn.commit() é chamado automaticamente pelo context manager de conn
            for i in inserted:
                logger.info("✅ Projeto inserido: ID %s - %s", i[0], i[1])
            return inserted

    except psycopg2.Error as e:
        logger.error("❌ Erro ao inserir projetos: %s", e)
        if conn:
            conn.rollback()
        raise

if __name__ == "__main__":
    if not check_table_exists():
        raise SystemExit(1)

    inserted = insert_projects_batch()
    print(f"\n✅ Total de {len(inserted)} projetos inseridos com sucesso!")
    for pid, pname in inserted:
        print(f"   - ID: {pid}, Nome: {pname}")
