# Version 1.0

from db_data import *
from os import environ

from flask import Flask, render_template, redirect, url_for, request, flash, session, g
from forms import vraagForm, RegistratieForm, LoginForm
from markupsafe import Markup

app = Flask(__name__)
app.config['SECRET_KEY'] = environ.get("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


@app.route("/datakwaliteit/<table>")
def table(table):
    db_connection = connect_to_database('testcorrect_vragen.db')
    data = get_db_data(db_connection, f"SELECT * FROM {table}").fetchall()
    db_connection.close()

    return render_template('table.html', title="table", data=data)

@app.route("/home")
def home():
    if g.gebruikersnaam:
        return render_template('homepage.html', gebruiker=session['gebruikersnaam'])
    return redirect(url_for('login'))

@app.before_request
def before_request():
    g.gebruikersnaam = None

    if 'gebruikersnaam' in session:
        g.gebruikersnaam = session['gebruikersnaam']

@app.route("/registreer", methods=['GET', 'POST'])
def registreer():
    form = RegistratieForm()
    con = sqlite3.connect('testcorrect_vragen.db')
    c = con.cursor()
    if request.method == 'POST':
        if (request.form['gebruikersnaam'] != "" and request.form["wachtwoord"] != ""):
            gebruikersnaam = request.form["gebruikersnaam"]
            wachtwoord = request.form["wachtwoord"]
            statement = f"INSERT INTO Gebruiker (gebruikersnaam, wachtwoord) VALUES ('{gebruikersnaam}', '{wachtwoord}')"
            c.execute(statement)
            con.commit()
        return render_template('registreer.html', title="Registreer", form=form)
    elif request.method == 'GET':
        return render_template('registreer.html', title="Registreer", form=form)

@app.route("/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    con = sqlite3.connect('testcorrect_vragen.db')
    con.row_factory=sqlite3.Row
    cur = con.cursor()
    if request.method == 'POST':
            session.pop('gebruikersnaam', None)
            gebruikersnaam = request.form['gebruikersnaam']
            wachtwoord = request.form['wachtwoord']
            cur = con.cursor()
            cur.execute("SELECT gebruikersnaam, wachtwoord FROM Gebruiker WHERE gebruikersnaam=? and wachtwoord=?",(gebruikersnaam, wachtwoord))
            data = cur.fetchone()

            if data:

                session["gebruikersnaam"] = data[0]
                session["wachtwoord"] = data[1]
                return redirect("home")

            else:
                
                flash("gebruikersnaam of wachtwoord is onjuist")

    return render_template('login1.1.html', title='Log in', form=form)

@app.route('/getsession')
def getsession():
    if 'gebruikersnaam' in session:
        gebruikersnaam = session['gebruikersnaam']
        return f"Welcome {gebruikersnaam}"
    else:
        return "Welcome Anonymous"

@app.route('/logout')
def logout():
    session.pop('gebruikersnaam', None)
    return redirect(url_for('login'))

@app.route("/vragen")
def vragen():
    if g.gebruikersnaam:
        db_connection = connect_to_database("testcorrect_vragen.db")
        vragen = get_db_data(db_connection, f"SELECT * FROM vragen WHERE NOT gemarkeerd=1").fetchall()
        leerdoelen = get_db_data(db_connection, f"SELECT * FROM leerdoelen").fetchall()
        db_connection.close()

        data = tag_data(vragen, leerdoelen)

        return render_template('vragen.html', title="Vragen", data=data)
    return redirect(url_for('login'))


@app.route("/vraag/<int:vraag_id>", methods=["GET", "POST"])
def vraag(vraag_id):
    if g.gebruikersnaam:
        db_connection = connect_to_database("testcorrect_vragen.db")
        vraag = get_db_data(
            db_connection, f"SELECT * FROM vragen WHERE id={vraag_id}").fetchone()
        leerdoelen = get_db_data(
            db_connection, f"SELECT * FROM leerdoelen").fetchall()
        form = vraagForm()

        if request.method == "POST":
            print(f"Gemarkeerd ja of nee?: {request.form.get('gemarkeerd')}")
            set_db_data(
                db_connection, f"UPDATE vragen SET vraag = '{form.vraag.data}' WHERE id={vraag_id}")
            set_db_data(db_connection, f"UPDATE vragen SET leerdoel = {form.leerdoel.data} WHERE id={vraag_id}")
            set_db_data(db_connection, f"UPDATE vragen SET gemarkeerd = {request.form.get('gemarkeerd')} WHERE id={vraag_id}")
            flash('Vraag is aangepast!')

            return redirect(url_for('vraag', vraag_id=vraag["id"]))


        marked_vraag = Markup(vraag["vraag"].replace("&nbsp;", "<mark>&amp;nbsp;</mark>").replace("<br>", "<mark>&lt;br&gt;</mark>"))

        form.vraag.default = vraag['vraag']
        form.process()

        db_connection.close()
        return render_template('vraag.html', title=f"Vraag items - Vraag {vraag['id']}", marked_vraag=marked_vraag, vraag=vraag, leerdoelen=leerdoelen,
                               form=form)
    return redirect(url_for('login'))

@app.route("/datakwaliteit")
def datakwaliteit():
    if g.gebruikersnaam:
        db_connection = connect_to_database("testcorrect_vragen.db")
        tables = get_db_data(db_connection, f"SELECT name FROM sqlite_master WHERE type='table'")

        return render_template("datakwaliteit.html", title="Data kwaliteit", tables=tables)
    return redirect(url_for('login'))

@app.route("/tables/<table>")
def tables(table):
    if g.gebruikersnaam:
        db_connection = connect_to_database("testcorrect_vragen.db")
        table_info = get_db_data(db_connection, f"SELECT name, type FROM pragma_table_info('{table}')").fetchall()
        tables = get_db_data(db_connection, f"SELECT name FROM sqlite_master WHERE type='table'")
        datatypes = ["INTEGER", "VARCHAR", "BOOLEAN"]
        return render_template("table.html", title="Data kwaliteit", table_info=table_info, datatypes=datatypes, tables=tables)
    return redirect(url_for('login'))

@app.route("/tabellen/<tabel>")
def tabellen(tabel):
    if g.gebruikersnaam:
        db_connection = connect_to_database("testcorrect_vragen.db")
        table_columns_info = get_db_data(db_connection, f"SELECT name, type FROM pragma_table_info('{tabel}')").fetchall()
        table_data = get_db_data(db_connection, f"SELECT * FROM '{tabel}'").fetchall()
        return render_template("tabel.html", title="Data kwaliteit", table_columns_info=table_columns_info, table_data=table_data, tabel=tabel)
    return redirect(url_for('login'))

@app.route("/kolom/<tabel>/<kolom>", methods=["GET", "POST"])
def kolom(tabel, kolom):
    if g.gebruikersnaam:
        db_connection = connect_to_database("testcorrect_vragen.db")
        column_info = get_db_data(db_connection, f"SELECT * FROM pragma_table_info('{tabel}') WHERE name='{kolom}'").fetchall()
        column_data = get_db_data(db_connection, f'SELECT id, "{kolom}" FROM "{tabel}"').fetchall()
        datatypes = ["INTEGER", "VARCHAR", "TEXT", "BOOLEAN"]

        db_connection.close()

        if request.method == "POST":
            if request.form.get('datatype-select') == "VARCHAR":
                change_data_type(tabel, kolom, f"{request.form.get('datatype-select')}({request.form.get('datatype-amount-of-varchar')})")

            else:
                change_data_type(tabel, kolom, request.form.get('datatype-select'))

            return redirect(url_for('kolom', tabel=tabel, kolom=kolom))


        return render_template("kolom.html", title="Data kwaliteit", column_info=column_info, column_data=column_data, datatypes=datatypes, tabel=tabel)
    return redirect(url_for('login'))

@app.route("/<tabel>/rij/<rij_id>", methods=["GET", "POST"])
def rij(tabel, rij_id):
    if g.gebruikersnaam:
        db_connection = connect_to_database("testcorrect_vragen.db")
        column_info = get_db_data(db_connection,
                                  f"SELECT type FROM pragma_table_info('{tabel}')").fetchall()
        column_data = get_db_data(db_connection, f'SELECT * FROM "{tabel}" WHERE id="{rij_id}"').fetchone()

        data = []
        for i, d in enumerate(column_data):
            new_dic = {
                str(d): column_data[d],
                "datatype": column_info[i]["type"]
            }
            data.append(new_dic)

        if request.method == "POST":
            for col in column_data:
                if col != "id":
                    this_col_info = get_db_data(db_connection,
                                              f'SELECT type FROM pragma_table_info("{tabel}") WHERE name="{col}"').fetchone()
                    if this_col_info['type'] == "BOOLEAN":
                        if request.form.get(col) == "0" or request.form.get(col) == None or request.form.get(col) == 0:
                            set_db_data(db_connection, f'UPDATE {tabel} SET "{col}" = 0 WHERE id = {rij_id}')
                        else:
                            set_db_data(db_connection,
                                        f'UPDATE {tabel} SET "{col}" = 1 WHERE id = {rij_id}')

                    else:
                        set_db_data(db_connection,
                                    f'UPDATE {tabel} SET "{col}" = "{request.form.get(col)}" WHERE id = {rij_id}')

            flash('Rij is aangepast!')
            return redirect(url_for('rij', rij_id=rij_id, title="Rij", data=data, tabel=tabel))


        return render_template("rij.html", title="Rij", data=data, tabel=tabel)
    return redirect(url_for('login'))

@app.route("/tussenwaardes", methods=["GET", "POST"])
def tussenwaardes():
    if g.gebruikersnaam:
        db_connection = connect_to_database("testcorrect_vragen.db")
        tabellen = get_db_data(db_connection, f"SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_with_info = []

        for tabel in tabellen:
            print(f"Tabel: {tabel['name']}")
            new_dict = {
                'tabel': tabel['name'],
                'columns': []
            }
            tabel = tabel['name']
            columns = get_db_data(db_connection, f'SELECT name FROM pragma_table_info("{tabel}")').fetchall()
            for column in columns:
                print(f"Column: {column['name']}")
                new_dict['columns'].append(column['name'])
            table_with_info.append(new_dict)

        if request.method == "POST":
            selected_table = request.form.get('tableSelect')
            selected_column = request.form.get('columnSelect')
            value_a = int(request.form.get('value-a'))
            value_b = int(request.form.get('value-b'))

            data = get_db_data(db_connection, f"SELECT * FROM {selected_table} WHERE {selected_column} BETWEEN {value_a} and {value_b}").fetchall()

            return render_template("tussenwaardes.html", title="Tussenwaardes", table_with_info=table_with_info, data=data)

        return render_template("tussenwaardes.html", title="Tussenwaardes", table_with_info=table_with_info)
    return redirect(url_for('login'))