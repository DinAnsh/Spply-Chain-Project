from flask import Flask, request, render_template, redirect, url_for
from datetime import date
import db, log

app = Flask(__name__)
submitted = None
editted = False
ord_list = []
form_val = []

@app.route('/', methods=['GET','POST'])
def invoice():
    global submitted, editted, ord_list, form_val
    editted = False
        
    if request.method=='GET':
        form_val = []
        ord_list = []
        submitted = False
        
        log.put_log(2, 'Open invoice page!')
        return render_template('invoice.html', zip=zip, form_val=form_val, submitted=submitted, editted=editted, ord_list=ord_list)

    else:
        cur, con = db.get_db()
        log.put_log(2, request.method)

        Invoice_Date = request.form.get('Invoice_Date')
        Cust_Id = request.form.get('Cust_Id')
        Cust_Name = cur.execute("select Cust_name from Mcustomer where Cust_Id=(?)",Cust_Id).fetchval()
        Ord_Id = request.form.get('Ord_Id')
        Invoice_Qty = request.form.get('Invoice_Qty')
        
        form_val += [Invoice_Date, Cust_Id, Cust_Name]
        if Ord_Id!='' and Invoice_Qty!='':
            ord_list += [(Ord_Id, Invoice_Qty)]
        
        log.put_log(2, 'Got values from the user - {}'.format(ord_list))
        return render_template('invoice.html', zip=zip, form_val=form_val, submitted=submitted, editted=editted, ord_list=ord_list)


@app.route('/edit/<values>', methods=['POST'])
def edit(values):
    global editted, submitted, ord_list
    editted = True
    submitted = False
    log.put_log(2, f'edit section - {values}')
    
    values = values.strip('()')
    values = values.replace("'","")
    values = values.replace('"','')
    values = values.split(',')
    twos = (values[0].strip(), values[1].strip())
    
    ord_list.remove(twos)
    log.put_log(2, f'want to edit - {twos}')
    
    return render_template('invoice.html', zip=zip, form_val=form_val, submitted=submitted, editted=editted, ord_list=ord_list, twos=twos)


@app.route('/delete/<values>', methods=['POST'])
def delete(values):
    global ord_list
    log.put_log(2, f'delete section - {values}')
    
    values = values.strip('()')
    values = values.replace("'","")
    values = values.replace('"','')
    values = values.split(',')
    values = (values[0].strip(), values[1].strip())
    
    log.put_log(2, f'list - {ord_list}')
    ord_list.remove(values)
    
    return render_template('invoice.html', zip=zip, form_val=form_val, submitted=submitted, editted=editted, ord_list=ord_list)
 

@app.route('/submit', methods=['POST'])
def submit():
    global ord_list, submitted, form_val
    submitted = True
    log.put_log(2, 'submit section!')
    log.put_log(2, f'form_val - {form_val}')
    log.put_log(2, f'ord_list - {ord_list}')
    cur, con = db.get_db()
    
    Tax_Amount = []
    Net_Amount = []

    Invoice_No = cur.execute("select Serial from Mnum where Tname='Tinvoice'").fetchval()
    form_val.insert(0, Invoice_No)
    
    try:
        for values in ord_list:
            ProductQty = cur.execute("select ProductQty from Morder where Ord_Id=(?)",values[0]).fetchval()
            ProductQty = float(ProductQty)
            max_qty = int(ProductQty - ProductQty*0.05)
            
            if int(values[1]) <= max_qty:
                cur.execute("exec create_invoice ?,?,?,?,?",values[0], form_val[-2], Invoice_No, form_val[-3], int(values[1]))
        
        for values in ord_list:
            Tax_Amount += [cur.execute("select Tax_Amount from Tinvoice where Ord_Id=?",values[0]).fetchval()]
            Net_Amount += [cur.execute("select Net_Amount from Tinvoice where Ord_Id=?",values[0]).fetchval()]
        log.put_log(2, '........!')
        cur.execute("update Mnum set Serial = ? where Tname = 'Tinvoice'",int(Invoice_No)+1)
        db.save_db(con)
        log.put_log(2, "database is saved!")
        db.close_db(con)
        log.put_log(2, "database is closed!")
    
    except Exception as e:
        log.put_log(2, f'some error in the query exec - {e}')

    log.put_log(2, f'Amounts - {Tax_Amount} {Net_Amount}')
    return render_template('invoice.html', zip=zip, submitted=submitted, editted=editted, form_val=form_val, ord_list=ord_list, Tax_Amount=Tax_Amount, Net_Amount=Net_Amount, total=sum(Net_Amount))


if __name__ == "__main__":
    app.run(debug=True)