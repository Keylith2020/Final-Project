import time
from flask import Flask, flash, redirect, render_template, request, url_for, session
import requests
import random
import string
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'your_secret_key'  # Required for session management

# connect to the database
def get_db_connection():
    conn = sqlite3.connect('reservations.db')
    conn.row_factory = sqlite3.Row  # Allows access to columns by name (instead of index)
    return conn

# generate list of reserved seats from the database
reservations = []
reserved_seats = get_db_connection().execute("SELECT seatRow, seatColumn FROM reservations").fetchall()
for x,y in reserved_seats:
    reservations.append((x,y))

# home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        option = request.form['option']
        
        if option == 'admin':
            return redirect(url_for('admin'))
        elif option == 'reservation':
            return redirect(url_for('reservation'))
        else:
            flash('Please select an option', 'error')
            return render_template('index.html')
    
    return render_template('index.html')

# admin log in
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['userName']
        password = request.form['passWord']
        
        # Check the admin credentials (this is just an example, you can use hashed passwords)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE username = ?', (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and admin['password'] == password:  # Check password (in a real app, use hashed passwords)
            session['admin'] = admin['username']  # Store the logged-in admin in the session
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin.html')

# admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin'))  # If not logged in, redirect to the login page

    #Calculate total sales
    cost_matrix= get_cost_matrix()
    total_sales = 0
    for row, seat in reservations:
        total_sales += cost_matrix[row -1][seat -1]

    return render_template('adminLoggedIn.html', total_sales=total_sales, reserved_seats=reservations)

# admin log out
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)  # Remove the admin from the session
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin'))  # Redirect back to the login page

# reservations page
@app.route('/reservation', methods=['GET', 'POST'])
def reservation():
    if request.method == 'POST':
        row = int(request.form['rowOption'])
        column = int(request.form['seatOption'])
        name = request.form['firstName'] + " " + request.form['lastName']
        time = datetime.now()

        # Connect to the database and check if the seat is reserved
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reservations WHERE seatRow = ? AND seatColumn = ?', (row, column))
        existing_reservation = cursor.fetchone()

        if existing_reservation:
            flash('Sorry, seat has been taken. Kindly choose another.')
        else:
            # Insert new reservation into the database
            reservation_code = generate_reservation_code()
            cursor.execute('INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber, created) VALUES (?, ?, ?, ?, ?)', 
               (name, row, column, reservation_code, time))
            conn.commit()
            flash(f'Reservation successful! Your reservation code is {reservation_code}. Row: {row}, Seat: {column}')
        
        conn.close()  # Close the database connection
    
    return render_template('reservation.html', reserved_seats=reservations)

def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix

def generate_reservation_code(length=12):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

if __name__ == "__main__":
    # http://localhost:5001/
    app.run(host="0.0.0.0", port=5000)

