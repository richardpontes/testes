import psycopg2

DB_URL = "postgresql://postgres.nhecrtlsrirnbkaynvmb:pronuncIA2025@aws-1-sa-east-1.pooler.supabase.com:5432/postgres?sslmode=require"

todo_id = 8  # 👈 ajuste o id que deseja deletar

with psycopg2.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM public.todos WHERE id = %s RETURNING id, task;",
            (todo_id,)
        )
        deleted = cur.fetchone()
        conn.commit()
        print("🗑️ DELETE:", deleted)
