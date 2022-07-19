from flask import Flask, request, render_template, redirect, url_for
from werkzeug.datastructures import MultiDict
from datetime import date
import db, log

app = Flask(__name__)
submitted = None
editted = False

@app.route('/', methods=['GET','POST'])
def home_page():
    global submitted, editted
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
        editted = False
        log.put_log(2, "Open Home page")
        return render_template('home.html', editted=editted, submitted=submitted, products=products, categories=categories, Ord_Id=Ord_Id)
    
    else:
        
        tup_values=[]
        table_values = list(request.form.values())

        if len(table_values)!=0:
            submitted = True
        
        log.put_log(2, "submit: {} & edit: {}".format(submitted,editted))
        
        try:
            Ord_Date = date.today()

            Product_Name = request.form.get("Product_Name")
            ProductId = cur.execute("select ProductId from Mproduct where Product_Name=(?)",Product_Name).fetchval()
            
            Category_Name = request.form.get("Category_Name")
            Category_Id = cur.execute("select Category_Id from Mcategory where Category_Name=(?)",Category_Name).fetchval()
            
            ProductQty = request.form.get("ProductQty")
            ProductRate = request.form.get("ProductRate")
            Ord_Status = request.form.get("Ord_Status")

            log.put_log(2, "Got values from user")
            tup = (Ord_Id,Ord_Date,ProductId,Category_Id,ProductQty,ProductRate,Ord_Status)
            tup_values = [value for value in tup]

            if editted:
                Ord_Id = Ord_Id-1
                cur.execute("update Morder set Ord_Date=?,ProductId=?,Category_Id=?,ProductQty=?,ProductRate=?,Ord_Status=? where Ord_Id=? ",Ord_Date,ProductId,Category_Id,ProductQty,ProductRate,Ord_Status,Ord_Id)
                log.put_log(2, "database is updated!")

            else:
                cur.execute("insert into Morder values(?,?,?,?,?,?,?)",tup_values)
                log.put_log(2, "data is inserted!")
            
        
        except:
            log.put_log(3, " There is some error in nested try block!!")
            return f"There is an ERROR - {tup_values}"      
        
        db.save_db(con)
        log.put_log(2, "database is saved!")
        db.close_db(con)
        log.put_log(2, "database is closed!")
        
        return render_template('home.html',editted=editted, products=products, categories=categories, table_values=table_values, submitted=submitted, Ord_Id=Ord_Id)


@app.route('/edit/<table_values>', methods=['POST'])
def edit(table_values):
    log.put_log(2, "edit section")
    global submitted, editted
    submitted = False
    editted = True
    try:
        cur, con = db.get_db()
        product_data = cur.execute("select Product_Name from Mproduct").fetchall()
        products = [product[0] for product in product_data]

        category_data = cur.execute("select Category_Name from Mcategory").fetchall()
        categories = [category[0] for category in category_data]
        
        table_values = table_values.replace("'", "")
        table_values = table_values.replace("[", "")
        table_values = table_values.replace("]", "")
        table_values = table_values.split(',')
        
        log.put_log(2, "values got successfully {}!!".format(table_values))
        
    except Exception as e:
        log.put_log(3, " There is some error in the method- {}!!".format(e))
        return f"There is an ERROR - {table_values}"

    
    return render_template('home.html', categories=categories, products=products, submitted=submitted, editted=editted, table_values=table_values)


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
