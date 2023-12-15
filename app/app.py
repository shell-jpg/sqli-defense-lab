from flask import Flask, render_template, request
from flaskext.mysql import MySQL

app = Flask(__name__)

# Настройки подключения к базе данных
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'web_app_db'
app.config['MYSQL_DATABASE_HOST'] = 'DB'

mysql = MySQL(app)

# Функция для валидации ввода (простая проверка на буквы, цифры и подчеркивания)
def validate_input(input_value):
    allowed_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
    return all(char in allowed_characters for char in input_value)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница для параметризованных запросов
@app.route('/parametrized')
def parametrized():
    method = 'parametrized'
    query_code = """cursor.execute("SELECT * FROM users WHERE username = %s", (data,))"""
    return render_template('method.html', method=method, query_code=query_code)

# Страница для хранимых процедур
@app.route('/stored_procedure')
def stored_procedure():
    method = 'stored_procedure'
    query_code = """
cursor.callproc('GetUserByUsername', (data,))

# SQL Procedure code:
DELIMITER //

CREATE PROCEDURE GetUserByUsername(IN username_param VARCHAR(255))
BEGIN
    SELECT * FROM users WHERE username = username_param;
END //

DELIMITER ;
"""
    return render_template('method.html', method=method, query_code=query_code)

# Страница для white-list валидации
@app.route('/whitelist_validation')
def whitelist_validation():
    method = 'whitelist_validation'
    query_code = """
cursor.execute(f"SELECT * FROM users WHERE username = '{data}'")

#Validation function
def validate_input(input_value):
    allowed_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
    return all(char in allowed_characters for char in input_value)
"""
    return render_template('method.html', method=method, query_code=query_code)

# Страница для экранирования пользовательского ввода
@app.route('/escaping')
def escaping():
    method = 'escaping'
    query_code = """cursor.execute(f"SELECT * FROM users WHERE username = '{mysql.get_db().escape_string(data)}'")"""
    return render_template('method.html', method=method, query_code=query_code)

# Обработка запросов
@app.route('/query', methods=['POST'])
def execute_query():
    method = request.form['method']
    data = request.form['data']

    cursor = mysql.get_db().cursor()

    if method == 'parametrized':
        cursor.execute("SELECT * FROM users WHERE username = %s", (data,))
    elif method == 'stored_procedure':
        cursor.callproc('GetUserByUsername', (data,))
    elif method == 'whitelist_validation':
        if validate_input(data):
            cursor.execute(f"SELECT * FROM users WHERE username = '{data}'")
        else:
            return "Invalid input"
    elif method == 'escaping':
        cursor.execute(f"SELECT * FROM users WHERE username = '{mysql.get_db().escape_string(data)}'")
    else:
        return "Invalid method"

    result = cursor.fetchall()

    return render_template('result.html', method=method, query=cursor._executed, result=result)

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

