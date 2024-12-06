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

def get_db_connection():
    conn = sqlite3.connect('reservations.db')
    conn.row_factory = sqlite3.Row  # Allows access to columns by name (instead of index)
    return conn

# DEBUG for reserved_seats (row, seat) this should be empty for turn in.
reservations = []
reserved_seats = get_db_connection().execute("SELECT seatRow, seatColumn FROM reservations").fetchall()
for x,y in reserved_seats:
    reservations.append((x,y))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        option = request.form['option']
        
        if option == 'admin':
            return redirect(url_for('admin'))
        elif option == 'reservation':
            return redirect(url_for('reservation'))
        else:
            return render_template('index.html', error='Please select an option')
    
    return render_template('index.html')

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

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin'))  # If not logged in, redirect to the login page

    # Fetch the total sales data
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM reservations')  # Get total number of reservations (this can be used for total sales)
    total_sales = cursor.fetchone()[0]  # Example: Total reservations count as sales (modify as needed)

    conn.close()

    # Generate the seating chart as a 4x12 grid
    seating_chart = []
    for row in range(0, 4):
        row_seats = []
        for col in range(0, 12):
            if (row, col) in reservations:
                row_seats.append('X')
            else:
                row_seats.append('O')
        seating_chart.append(row_seats)

    return render_template('adminLoggedIn.html', seating_chart=seating_chart, total_sales=total_sales)

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)  # Remove the admin from the session
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin'))  # Redirect back to the login page

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
        return redirect(url_for('index'))
    
    return render_template('reservation.html', reserved_seats=reservations)

def generate_reservation_code(length=12):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix

if __name__ == '__main__':
    app.run()
