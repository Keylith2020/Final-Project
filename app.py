import time
from flask import Flask, flash, g, redirect, render_template, request, url_for
import requests
import random
import string
import sqlite3

app = Flask(__name__)
app.config['API_KEY'] = 'API_KEY_HERE'
app.config["DEBUG"] = True
DATABASE = 'reservations.db'

def get_db_connection():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect(DATABASE)

    return conn

#DEBUG for reserved_seats (row, seat) this should be empty for turn in.
reserved_seats = [(5,1), (3,3), (7,2)]

@app.route('/', methods=('GET', 'POST'))
def index():
<<<<<<< HEAD
    if request.method == 'POST':
        option = request.form['option']
        if option == 'admin':
            return redirect(url_for('admin'))
        elif option == 'reservation':
            return redirect(url_for('reservation'))
        else:
            flash("Please select a menu option.")
    return render_template('index.html') 
=======
    return render_template('index.html', reserved_seats=reserved_seats) # reserved_seats=reserved_seats can be moved?
>>>>>>> dcf6f972b9dcc2f835289d5d6d9224dd617938c1

@app.route('/admin', methods=('GET', 'POST'))
def admin():
    if request.method == 'POST':
        # see if username and password matches record in admin table
        pass
    
    return render_template('admin.html')

@app.route('/reservation', methods=('GET', 'POST'))
def reservation():
    if request.method == 'POST':
        row = int(request.form['rowOption'])
        seat = int(request.form['seatOption'])
        
        if(row, seat) in reserved_seats:
            flash('Sorry, seat has been taken. Kindly choose another.')
        elif(row, seat) not in reserved_seats:
            reserved_seats.append((row, seat))
            # What generates the reservation code
            reservation_code = generate_reservation_code()
            # TODO maybe the def that stores it in reservations goes here?
            #Displaying info to user (Debug)
<<<<<<< HEAD
            flash(f'Reservation successful! Your reservation code is {reservation_code}.\nRow: {row}, Seat: {seat}')
=======
            flash(f'Reservation successful! Your reservation code is {reservation_code}.Row: {row}, Seat: {seat}')
>>>>>>> dcf6f972b9dcc2f835289d5d6d9224dd617938c1
        
            time.sleep(5)
            return redirect(url_for('index'))

    return render_template('reservation.html', reserved_seats=reserved_seats)

def generate_reservation_code(length=12):
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

if __name__ == '__main__':
    app.run()

'''
Function to generate cost matrix for flights
Input: none
Output: Returns a 12 x 4 matrix of prices
Will likely need to change location of code to better fit logic
'''
def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix
    