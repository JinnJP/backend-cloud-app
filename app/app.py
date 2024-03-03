from flask import Flask, jsonify, request
from controller import * 
import mysql.connector

app = Flask(__name__)

def connector():
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        # 'database': 'src', 'dest'
    }
    return config

def get_column_types(src_table):
    connection = mysql.connector.connect(**connector())
    cursor = connection.cursor()
    query = f"DESCRIBE src.{src_table};"
    cursor.execute(query)
    column_types = {column[0]: column[1] for column in cursor.fetchall()}
    cursor.close()
    return column_types

@app.route('/create_table', methods=['GET'])
def create_table():
    src_table = request.args.get("src_table")
    src_column = request.args.getlist("src_column")
    dest_table = request.args.get("dest_table")
    dest_column = request.args.getlist("dest_column")
    connection = mysql.connector.connect(**connector())
    cursor = connection.cursor()
    # print("route create_table")
    column_types = get_column_types(src_table)
    sql_statements = manage_create_query(src_table, src_column, dest_table, dest_column, column_types)
    # created = create_table(create_query)
    # print("sql_statements = ",sql_statements)
    try:
        for sql in sql_statements:
            cursor.execute(sql)
            # print(f"Executed SQL: {sql};")
        # Commit the changes (if necessary)
        connection.commit()
        return jsonify({'status': 'Table created!', 'query': sql_statements})
    except mysql.connector.Error as err:
        # Handle the error and return a JSON response
        error_message = str(err)
        return jsonify({'error': error_message})
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()  

def get_column_names(table_name):
    connection = mysql.connector.connect(**connector())
    cursor = connection.cursor()
    query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = 'src';"
    cursor.execute(query)
    # column_types = {column[0]: column[1] for column in cursor.fetchall()}
    column_names = cursor.fetchall()
    # print("column_names= ",column_names)
    # ['car_brand_id','car_brand_name']
    cursor.close()
    return column_names

@app.route('/select_table', methods=['GET'])
def select_table():
    table_name = request.args.get("table_name")
    column_names = get_column_names(table_name)
    connection = mysql.connector.connect(**connector())
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT * FROM src.{table_name} LIMIT 5;")
        data = cursor.fetchall()
        formatted_data = [dict(zip([col[0] for col in column_names], row)) for row in data]
        if len(formatted_data) != 0:
            return formatted_data
        else:
            return 'Query returned no results.'
    except mysql.connector.Error as err:
        # Handle the error and return a JSON response
        error_message = str(err)
        return jsonify({'error': error_message})
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()  
    
#Route for testing
@app.route('/car_brand')
def index():
    # config_db = connector_sql()
    connection = mysql.connector.connect(**connector())
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM src.car_brand')
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

@app.route('/select_dest')
def select_dest():
    # connection_config = connector()
    connection = mysql.connector.connect(**connector())
    cursor = connection.cursor()
    try:
        # Create a cursor object to execute queries
        # Your SELECT query
        query = "SELECT * FROM dest.car_brand;"
        # Execute the query
        cursor.execute(query)
        # Fetch all rows
        result = cursor.fetchall()
        print(result)
        return result
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

@app.route('/desc_dest')
def desc_dest():
    dest_table = request.args.get("dest_table")
    connection = mysql.connector.connect(**connector())
    cursor = connection.cursor()
    query = f"DESCRIBE dest.{dest_table};"
    cursor.execute(query)
    column_types = {column[0]: column[1] for column in cursor.fetchall()}
    # result = cursor.fetchall()
    cursor.close()
    return column_types

@app.route('/desc_src', methods=['GET'])
def desc_src():
    src_table = request.args.get("src_table")
    connection = mysql.connector.connect(**connector())
    cursor = connection.cursor()
    query = f"DESCRIBE src.{src_table};"
    cursor.execute(query)
    # column_types = {column[0]: column[1] for column in cursor.fetchall()}
    results = cursor.fetchall()
    cursor.close()
    # return jsonify({'result': result,'column_types': column_types})
    return results

@app.route('/allTable_allColumn', methods=['GET'])
def allTable_allColumn():
    host = "db"
    user = "root"
    password = "root"
    port = "3306"
    database_src = "src"
    database_dest = "dest"

    data = {"source": [], "dest": []}

    # -- src ---
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=database_src)
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()

        table_data = {"name": table_name, "columns": [column[0] for column in columns]}
        data["source"].append(table_data)
    cursor.close()
    connection.close()

    # -- dest ---
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=database_dest)
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()

        table_data = {"name": table_name, "columns": [column[0] for column in columns]}
        data["dest"].append(table_data)
    cursor.close()
    connection.close()

    return data

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4999, debug=True)

