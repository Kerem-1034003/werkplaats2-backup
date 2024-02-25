import sqlite3


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def connect_to_database(db_file_path):
    conn = None
    try:
        conn = sqlite3.connect(db_file_path)
        conn.row_factory = dict_factory
    except:
        pass
    return conn


def get_db_data(db_connection, command):
    cursor = db_connection.cursor()
    try:
        result = cursor.execute(f'{command}')
        return result
    except:
        return False


def set_db_data(db_connection, command):
    cursor = db_connection.cursor()
    cursor.execute(f'{command}')
    db_connection.commit()


def scan_data(vragen, leerdoelen):
    br_vragen = []
    nbsp_vragen = []
    leerdoelen_vragen = []

    for vraag in vragen:
        if "<br>" in vraag['vraag']:
            br_vragen.append(vraag)
        elif "&nbsp" in vraag['vraag']:
            nbsp_vragen.append(vraag)
        elif vraag['leerdoel'] == None or vraag['leerdoel'] > leerdoelen[-1]['id']:
            leerdoelen_vragen.append(vraag)

    return {'br_vragen': br_vragen, 'nbsp_vragen': nbsp_vragen, 'leerdoelen_vragen': leerdoelen_vragen}

def tag_data(vragen, leerdoelen):
    for vraag in vragen:
        tags = []
        if "<br>" in vraag['vraag']:
            tags.append("br")
        if "&nbsp" in vraag['vraag']:
            tags.append("nbsp")
        if vraag['leerdoel'] == None or vraag['leerdoel'] > leerdoelen[-1]['id']:
            tags.append("leerdoel")
        vraag["tags"] = tags

    return vragen

def change_data_type(tablename, to_be_updated_column, new_datatype):
    db_connection = connect_to_database("testcorrect_vragen.db")
    columns_info = get_db_data(db_connection, f"SELECT name, type FROM pragma_table_info('{tablename}')")
    newDbName = f"{tablename}Copy"

    command = ""
    for i in columns_info:
        if i["name"] == to_be_updated_column:
            #command = f"{command}{to_be_updated_column} {new_datatype}, "
            command = command + "\"" + to_be_updated_column + "\" " + new_datatype + ", "
        else:
            #command = f"{command}{i['name']} {i['type']}, "
            command = command + "\"" + i['name'] + "\" " + i['type'] + ", "

    command = f"CREATE TABLE {newDbName}({command[:-2]})"
    set_db_data(db_connection, command)
    set_db_data(db_connection, f"INSERT INTO {newDbName} SELECT * FROM {tablename}")
    set_db_data(db_connection, f"DROP TABLE {tablename}")
    set_db_data(db_connection, f"ALTER TABLE {newDbName} RENAME TO {tablename}")