from flask import Flask, render_template, request, session, redirect
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mysecretkey'

# Se define la ruta principal de la aplicación
@app.route('/')
def index():
    # Si el usuario ya está autenticado, se redirige a la página principal
    if 'username' in session:
        return redirect('/main')

    # Si no, se muestra el formulario de inicio de sesión/registro
    return render_template('index.html')

# Ruta para manejar el inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    # Se obtienen las credenciales ingresadas por el usuario
    username = request.form['username']
    password = request.form['password']

    # Se realiza la validación de las credenciales en la base de datos
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()

    # Si las credenciales son correctas, se guarda el usuario en la sesión y se redirige a la página principal
    if user:
        session['username'] = user[0]
        return redirect('/main')

    # Si las credenciales son incorrectas, se muestra un mensaje de error en la página de inicio de sesión/registro
    return render_template('index.html', error='Invalid username or password')

# Ruta para manejar el registro de usuarios
@app.route('/signup', methods=['POST'])
def signup():
    # Se obtienen los datos ingresados por el usuario
    username = request.form['username']
    password = request.form['password']

    # Se verifica que el usuario no exista ya en la base de datos
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()

    # Si el usuario no existe, se crea en la base de datos
    if not user:
        cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
        cursor.execute('INSERT INTO users VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()

        # Se guarda el usuario en la sesión y se redirige a la página principal
        session['username'] = username
        return redirect('/main')

    # Si el usuario ya existe, se muestra un mensaje de error en la página de inicio de sesión/registro
    conn.close()
    return render_template('index.html', error='Username already taken')

# Ruta para la página principal, después de que el usuario se ha autenticado correctamente
@app.route('/main')
def main():
    # Si el usuario no está autenticado, se redirige a la página de inicio de sesión/registro
    if 'username' not in session:
        return redirect('/')

    # Se obtienen los mensajes enviados por el usuario
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, created_at)')
    cursor.execute('SELECT * FROM messages ORDER BY created_at DESC')
    '''cursor.execute('SELECT * FROM messages WHERE sender=?', (session['username'],))'''
    messages = cursor.fetchall()
    conn.close()

    # Se muestran los mensajes en la página principal
    return render_template('main.html', username=session['username'], messages=messages)

# Ruta para manejar el envío de mensajes por parte del usuario
@app.route('/send', methods=['POST'])
def send():
    # Se obtiene el mensaje enviado por el usuario
    message = request.form['message']

    # Se inserta el mensaje en la base de datos
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, created_at)')
    cursor.execute('INSERT INTO messages (sender, message, created_at) VALUES (?, ?, ?)', (session['username'], message, datetime.now()))
    conn.commit()
    conn.close()

    # Se redirige a la página principal
    return redirect('/main')

@app.route('/update_messages')
def update_messages():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages ORDER BY created_at DESC')
    messages = cursor.fetchall()
    conn.close()

    return json.dumps(messages)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    # Se elimina el usuario de la sesión y se redirige a la página de inicio de sesión/registro
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)