from flask import Flask, Response, request, render_template, redirect, url_for
from datetime import date
from fpdf import FPDF
import db, log

app = Flask(__name__)

osubmitted = None
oeditted = False

isubmitted = None
ieditted = False

ord_list = []
form_val = []

@app.route('/')
def home():
    log.put_log(2, "home page!")
    return render_template('home.html')

#order_script starts

@app.route('/order', methods=['GET','POST'])
def order():
    global osubmitted, oeditted
    cur, con = db.get_db()
    product_data = cur.execute("select Product_Name from Mproduct").fetchall()
    products = [product[0] for product in product_data]

    category_data = cur.execute("select Category_Name from Mcategory").fetchall()
    categories = [category[0] for category in category_data]

    Ord_Id = cur.execute("select Ord_Id from MOrder").fetchval()
    Ord_Id = int(Ord_Id) + cur.execute("select count(*) from Morder").fetchval()
    
    table_values = []
    if request.method=='GET':
        osubmitted = False
        oeditted = False
        log.put_log(2, "Order page!")
        return render_template('order.html', oeditted=oeditted, osubmitted=osubmitted, products=products, categories=categories, Ord_Id=Ord_Id)
    
    else:
        
        tup_values=[]
        table_values = list(request.form.values())

        if len(table_values)!=0:
            osubmitted = True
        
        log.put_log(2, "submit: {} & edit: {}".format(osubmitted,oeditted))
        
        try:
            Ord_Date = date.today()

            Product_Name = request.form.get("Product_Name")
            ProductId = cur.execute("select ProductId from Mproduct where Product_Name=(?)",Product_Name).fetchval()
            
            Category_Name = request.form.get("Category_Name")
            Category_Id = cur.execute("select Category_Id from Mcategory where Category_Name=(?)",Category_Name).fetchval()
            
            ProductQty = request.form.get("ProductQty")
            ProductRate = request.form.get("ProductRate")
            Ord_Status = request.form.get("Ord_Status")

            log.put_log(2, "Got order from the user.")
            tup = (Ord_Id,Ord_Date,ProductId,Category_Id,ProductQty,ProductRate,Ord_Status)
            tup_values = [value for value in tup]

            if oeditted and osubmitted:
                Ord_Id = Ord_Id-1
                oeditted = False
                cur.execute("update Morder set Ord_Date=?,ProductId=?,Category_Id=?,ProductQty=?,ProductRate=?,Ord_Status=? where Ord_Id=? ",Ord_Date,ProductId,Category_Id,ProductQty,ProductRate,Ord_Status,Ord_Id)
                log.put_log(2, "database is updated!")

            else:
                cur.execute("insert into Morder values(?,?,?,?,?,?,?)",tup_values)
                log.put_log(2, "data is inserted!")
            
        
        except Exception as e:
            log.put_log(3, " There is some error in nested try block!!")
            return f"There is an ERROR - {e}"      
        
        db.save_db(con)
        log.put_log(2, "database is saved!")
        db.close_db(con)
        log.put_log(2, "database is closed!")
        
        return render_template('order.html',oeditted=oeditted, products=products, categories=categories, table_values=table_values, osubmitted=osubmitted, Ord_Id=Ord_Id)


@app.route('/order/edit/<table_values>', methods=['POST'])
def order_edit(table_values):
    log.put_log(2, "Edit section of order!")
    global osubmitted, oeditted
    osubmitted = False
    oeditted = True
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
        log.put_log(3, "There is some error in the method- {}!!".format(e))
        return f"There is an ERROR - {table_values}"

    
    return render_template('order.html', categories=categories, products=products, osubmitted=osubmitted, oeditted=oeditted, table_values=table_values)


@app.route('/order/delete/<string:record_id>', methods=['POST'])
def order_delete(record_id):
    log.put_log(2, "Delete section of order!")
    
    try:
        cur, con = db.get_db()
        cur.execute("delete from Morder where Ord_Id=(?)",record_id)
        log.put_log(2, f"{record_id} data is deleted!")
    except Exception as e:
        log.put_log(3, f"There is some error in the query - {e}!!")
        return f"There is an ERROR - {record_id}"

    db.save_db(con)
    log.put_log(2, "database is saved!")
    db.close_db(con)
    log.put_log(2, "database is closed!")
    return redirect('/')

#order_script ends


#invoice_script starts

@app.route('/invoice', methods=['GET','POST'])
def invoice():
    global isubmitted, ieditted, ord_list, form_val
    ieditted = False
        
    if request.method=='GET':
        form_val = []
        ord_list = []
        isubmitted = False
        
        log.put_log(2, 'Open invoice page!')
        return render_template('invoice.html', zip=zip, form_val=form_val, isubmitted=isubmitted, ieditted=ieditted, ord_list=ord_list)

    else:
        cur, con = db.get_db()

        Invoice_Date = request.form.get('Invoice_Date')
        Cust_Id = request.form.get('Cust_Id')
        Cust_Name = cur.execute("select Cust_name from Mcustomer where Cust_Id=(?)",Cust_Id).fetchval()
        Ord_Id = request.form.get('Ord_Id')
        Invoice_Qty = request.form.get('Invoice_Qty')
        
        form_val += [Invoice_Date, Cust_Id, Cust_Name]
        if Ord_Id!='' and Invoice_Qty!='':
            ord_list += [(Ord_Id, Invoice_Qty)]
        
        log.put_log(2, 'Got values from the user - {}'.format(ord_list))
        return render_template('invoice.html', zip=zip, form_val=form_val, isubmitted=isubmitted, ieditted=ieditted, ord_list=ord_list)


@app.route('/invoice/edit/<values>', methods=['POST'])
def invoice_edit(values):
    global ieditted, isubmitted, ord_list
    ieditted = True
    isubmitted = False
    log.put_log(2, f'Edit section of invoice! - {values}')
    
    values = values.strip('()')
    values = values.replace("'","")
    values = values.replace('"','')
    values = values.split(',')
    twos = (values[0].strip(), values[1].strip())
    
    ord_list.remove(twos)
    log.put_log(2, f'want to edit invoice - {twos}')
    
    return render_template('invoice.html', zip=zip, form_val=form_val, isubmitted=isubmitted, ieditted=ieditted, ord_list=ord_list, twos=twos)


@app.route('/invoice/delete/<values>', methods=['POST'])
def invoice_delete(values):
    global ord_list
    log.put_log(2, f'Delete section of invoice - {values}')
    
    values = values.strip('()')
    values = values.replace("'","")
    values = values.replace('"','')
    values = values.split(',')
    values = (values[0].strip(), values[1].strip())
    
    ord_list.remove(values)
    log.put_log(2, f'updated order list - {ord_list}')
    
    return render_template('invoice.html', zip=zip, form_val=form_val, isubmitted=isubmitted, ieditted=ieditted, ord_list=ord_list)
 

@app.route('/invoice/submit', methods=['POST'])
def submit():
    global ord_list, isubmitted, form_val
    isubmitted = True
    log.put_log(2, 'Submit section of invoice!')
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
        log.put_log(2, '........!')

        for values in ord_list:
            Tax_Amount += [cur.execute("select Tax_Amount from Tinvoice where Ord_Id=?",values[0]).fetchval()]
            Net_Amount += [cur.execute("select Net_Amount from Tinvoice where Ord_Id=?",values[0]).fetchval()]
        
        
        cur.execute("update Mnum set Serial = ? where Tname = 'Tinvoice'",int(Invoice_No)+1)
        db.save_db(con)
        log.put_log(2, "database is saved!")
        db.close_db(con)
        log.put_log(2, "database is closed!")
    
    except Exception as e:
        log.put_log(2, f'some error in the query exec - {e}')

    log.put_log(2, f'Amounts - {Tax_Amount} {Net_Amount}')
    return render_template('invoice.html', zip=zip, isubmitted=isubmitted, ieditted=ieditted, form_val=form_val, ord_list=ord_list, Tax_Amount=Tax_Amount, Net_Amount=Net_Amount, total=sum(Net_Amount))

#invoice_script ends


#download_script starts

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/download_invoice', methods=['POST'])
def download_invoice():
    cur, con = db.get_db()
    try:        
        Invoice_No = request.form.get('Invoice_No')
        log.put_log(2, f"Download invoice {Invoice_No} section!!!")
        
        cur.execute("select * from Tinvoice where Invoice_No = (?)",Invoice_No)
        invoice = cur.fetchall()
        #amount calculation
        total, tax, net_amt = 0.0, 0.0, 0.0
        products = []
        for row in invoice:
            cur.execute("select Product_Name from Mproduct where ProductId = ?",row[1])
            products += [cur.fetchval()]
            total += float(row[7])
            tax += float(row[8])
            net_amt += float(row[9])
        total, tax, net_amt = round(total,4), round(tax,4), round(net_amt,4)

        #billing details
        cust_id = cur.execute("select Cust_Id from Tinvoice where Invoice_No = (?)", Invoice_No).fetchval()
        cust_name = cur.execute("select Cust_Name from Mcustomer where Cust_Id = (?)", cust_id).fetchval()
        address = cur.execute("select Cust_Add from Mcustomer where Cust_Id = (?)", cust_id).fetchval()
        invoice_date = cur.execute("select Invoice_Date from Tinvoice where Invoice_No = (?)", Invoice_No).fetchval()
        invoice_date = str(invoice_date).split()[0]
        mobno = '9588914507'
        log.put_log(2, f"Query executed successfully! - {cust_name}")

        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        page_width = pdf.w - 2 * pdf.l_margin
		
        pdf.set_font('Times','B',16.0)
        pdf.cell(page_width/2, 0.0, 'ABC PVT LTD', align='R')
        pdf.set_font('Times','B',8.0)
        pdf.cell(page_width/2, 0.0, '(an Illusion Group Company)', align='L')
        pdf.ln(5)

        pdf.set_font('Times','B',10.0) 
        pdf.cell(page_width, 0.0, 'Ganesh Nagar, Pahada, Udaipur-313001, Rajasthan', align='C')
        pdf.ln(5)
        pdf.cell(page_width, 0.0, 'Telephone: 123-456-7890', align='C')
        pdf.ln(10)

        pdf.set_font('Times','B',14.0) 
        pdf.cell(page_width, 0.0, 'INVOICE', align='C')
        pdf.ln(10)
        
        log.put_log(2, "header printed!")

        col_width = page_width/7
        pdf.set_font('Times','',10.0)
        pdf.cell(col_width, 0, 'Bill To:', align='L')
        pdf.ln(5)
                
        pdf.cell(col_width, 0, 'Custome Name', align='L')
        pdf.cell(col_width*3, 0, cust_name, align='L')
        pdf.cell(col_width, 0, '')
        pdf.cell(col_width, 0, 'Invoice No', align='L')
        pdf.cell(col_width, 0, Invoice_No, align='L')
        pdf.ln(5)

        pdf.cell(col_width, 0, 'Address', align='L')
        pdf.cell(col_width*3, 0, address, align='L')
        pdf.cell(col_width, 0,'', align='C')
        pdf.cell(col_width, 0, 'Invoice Date', align='L')
        pdf.cell(col_width, 0, invoice_date, align='L')
        pdf.ln(5)

        pdf.cell(col_width, 0, 'Mob.No.', align='L')
        pdf.cell(col_width*3, 0, mobno, align='L')
        pdf.cell(col_width, 0, '', align='C')
        pdf.cell(col_width, 0, 'Customer ID', align='L')
        pdf.cell(col_width, 0, cust_id, align='L')

        log.put_log(2, "body printed!")

        pdf.ln(10)
        pdf.cell(col_width, 0, '')
        pdf.cell(col_width*2, 5, 'Description', border=1, align='C')
        pdf.cell(col_width, 5, 'Rate', border=1, align='C')
        pdf.cell(col_width, 5, 'Quatity', border=1, align='C')
        pdf.cell(col_width, 5, 'Invoice Amount', border=1, align='C')
        pdf.cell(col_width, 0, '')
        pdf.ln(7)

        pdf.set_font('Courier', '', 8)
        td = pdf.font_size
        for pname, row in zip(products, invoice):
            pdf.cell(col_width, 5, '')
            pdf.cell(col_width*2, 5, pname, align='C', border='LR')
            pdf.cell(col_width, 5, str(row[6]), align='C', border='R')
            pdf.cell(col_width, 5, str(row[5]), align='C', border='R')
            pdf.cell(col_width, 5, str(row[7]), align='C', border='R')
            pdf.ln(5)

        pdf.cell(col_width, 0, '')
        pdf.cell(col_width*5, 0, '', border='T')

        pdf.ln(7)
        pdf.cell(col_width*5, 0, 'Total', align='R')
        pdf.cell(col_width, 0, str(total), align='C')
        pdf.ln(4)

        pdf.cell(col_width*5, 0, 'Tax', align='R')
        pdf.cell(col_width, 0, str(tax), align='C')
        pdf.ln(4)

        
        pdf.cell(col_width*5, 0, 'Net Amount', align='R')
        pdf.cell(col_width, 0, str(net_amt), align='C')
        pdf.ln(4)

        pdf.cell(col_width, 5, 'Signature', align='L', border='T')
        pdf.ln(10)

        pdf.set_font('Arial', '', 10.0)
        pdf.cell(page_width, 0.0, '--- end of invoice ---', align='C')
        
        db.close_db(con)
        log.put_log(2, "database is closed!")
        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=Invoice.pdf'})

    except Exception as e:
        log.put_log(2, f"Got exception - {e}")

#download_script ends


if __name__ == "__main__":
    app.run(debug=True)
