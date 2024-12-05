import time
from flask import Flask, flash, redirect, render_template, request, url_for, session
import requests
import random
import string
import sqlite3

app = Flask(__name__)
app.config['API_KEY'] = 'API_KEY_HERE'
app.config["DEBUG"] = True
app.secret_key = 'your_secret_key'  # Required for session management

def get_db_connection():
    conn = sqlite3.connect('reservations.db')
    conn.row_factory = sqlite3.Row  # Allows access to columns by name (instead of index)
    return conn


# DEBUG for reserved_seats (row, seat) this should be empty for turn in.
reserved_seats = [(5, 1), (3, 3), (7, 2)]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        option = request.form['option']
        
        if option == 'admin':
            return redirect(url_for('admin'))
        elif option == 'reservation':
            return redirect(url_for('reservation'))
        else:
            return render_template('index.html', error='Please select an option')
    
    return render_template('index.html')

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT row, seat FROM reservations')
    reserved_seats_db = cursor.fetchall()
    conn.close()

    # Pass the reserved seats from the database to the template
    return render_template('index.html', reserved_seats=reserved_seats_db)


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

    # Fetch the reserved seats and total sales data
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT row, seat FROM reservations')
    reserved_seats_db = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM reservations')  # Get total number of reservations (this can be used for total sales)
    total_sales = cursor.fetchone()[0]  # Example: Total reservations count as sales (modify as needed)

    conn.close()

    # Convert list of tuples to a set for easy lookup
    reserved_seats = set((seat['row'], seat['seat']) for seat in reserved_seats_db)

    # Generate the seating chart as a 4x12 grid
    seating_chart = []
    for row in range(1, 5):
        row_seats = []
        for col in range(1, 13):
            if (row, col) in reserved_seats:
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
        seat = int(request.form['seatOption'])

        # Connect to the database and check if the seat is reserved
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reservations WHERE row = ? AND seat = ?', (row, seat))
        existing_reservation = cursor.fetchone()

        if existing_reservation:
            flash('Sorry, seat has been taken. Kindly choose another.')
        else:
            # Insert new reservation into the database
            reservation_code = generate_reservation_code()
            cursor.execute('INSERT INTO reservations (row, seat, reservation_code) VALUES (?, ?, ?)', 
                           (row, seat, reservation_code))
            conn.commit()
            flash(f'Reservation successful! Your reservation code is {reservation_code}. Row: {row}, Seat: {seat}')
        
        conn.close()  # Close the database connection
        return redirect(url_for('index'))
    
    return render_template('reservation.html', reserved_seats=reserved_seats)

def generate_reservation_code(length=12):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))




def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix


if __name__ == '__main__':
    app.run()
