'''
import db
cur, con = db.get_db()

data = cur.execute("select ProductId from Mproduct where Product_Name='Wheels'").fetchval()
print(data)'''

l = [1,2,32,4]
print(l[1:])