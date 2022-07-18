from flask import Flask, request, render_template, redirect, url_for
from datetime import date
import db, log

app = Flask(__name__)
global submitted

@app.route('/', methods=['GET','POST'])
def home_page():
    cur, con = db.get_db()
    product_data = cur.execute("select Product_Name from Mproduct").fetchall()
    products = [product[0] for product in product_data]

    category_data = cur.execute("select Category_Name from Mcategory").fetchall()
    categories = [category[0] for category in category_data]

    Ord_Id = cur.execute("select Ord_Id from MOrder").fetchval()
    Ord_Id = int(Ord_Id) + cur.execute("select count(*) from Morder").fetchval()
    
    
    table_values = []
    if request.method=='GET':
        submitted = False
        log.put_log(2, "Open Home page")
        return render_template('home.html', submitted=submitted, products=products, categories=categories, Ord_Id=Ord_Id)
    
    else:
        submitted = True
        tup_values=[]
        table_values = list(request.form.values())
        log.put_log(2, request.method)
        
        try:
            Ord_Date = date.today()

            Product_Name = request.form.get("Product_Name")
            ProductId = cur.execute("select ProductId from Mproduct where Product_Name=(?)",Product_Name).fetchval()

            Categoryt_Name = request.form.get("Category_Name")
            Category_Id = cur.execute("select Category_Id from Mcategory where Category_Name=(?)",Category_Name).fetchval()
            
            ProductQty = request.form.get("ProductQty")
            ProductRate = request.form.get("ProductRate")
            Ord_Status = request.form.get("Ord_Status")
            Category_Id = request.form.get("Category_Id")

            log.put_log(2, "Got values from user")
            tup = (Ord_Id,Ord_Date,ProductId,ProductQty,ProductRate,Ord_Status,Category_Id)
            tup_values = [value for value in tup]

            cur.execute("insert into Morder values(?,?,?,?,?,?,?)",tup_values)
            log.put_log(2, "operation is performed!")
        
        except:
            log.put_log(3, " There is some error in nested try block!!")
            return f"There is an ERROR - {tup_values}"      
        
        db.save_db(con)
        log.put_log(2, "database is saved!")
        db.close_db(con)
        log.put_log(2, "database is closed!")
        
        return render_template('home.html', table_values=table_values, submitted=submitted, Ord_Id=Ord_Id)


@app.route('/edit/<string:record_id>', methods=['POST'])
def edit(record_id):
    log.put_log(2, "edit section")
    '''
    try:
        
    except:
        log.put_log(3, " There is some error in the query!!")
        return f"There is an ERROR - {record_id}"
'''
    return [request.form.get("Ord_Id"),
    request.form.get("ProductQty"),
    request.form.get("ProductRate"),
    request.form.get("Ord_Status"),
    request.form.get("Category_Id")]

    #return render_template('home.html')


@app.route('/delete/<string:record_id>', methods=['POST'])
def delete(record_id):
    log.put_log(2, "delete section")
    
    try:
        cur, con = db.get_db()
        cur.execute("delete from Morder where Ord_Id=(?)",record_id)
        log.put_log(2, f"{record_id} database is saved!")
    except:
        log.put_log(3, " There is some error in the query!!")
        return f"There is an ERROR - {record_id}"

    db.save_db(con)
    log.put_log(2, "database is saved!")
    db.close_db(con)
    log.put_log(2, "database is closed!")
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
