'''
import db

cur, con = db.get_db()
data = cur.execute("select * from Morder where Ord_Id=2253").fetchall()[0]
'''

from werkzeug.datastructures import MultiDict
data = MultiDict([('a', 'b'), ('a', 'c')])

print(data.setdefault('a'))
print()