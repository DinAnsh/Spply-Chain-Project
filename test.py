
import db

cur, con = db.get_db()
data = cur.execute("select Serial from Mnum where Tname='Tinvoice'").fetchval()
print(data)
