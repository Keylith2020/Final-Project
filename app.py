import time
from flask import Flask, flash, redirect, render_template, request, url_for
import requests
import random
import string


app = Flask(__name__)
app.config['API_KEY'] = 'API_KEY_HERE'
app.config["DEBUG"] = True

#DEBUG for reserved_seats (row, seat) this should be empty for turn in. Could also be moved elsewhere?
reserved_seats = [(5,1), (3,3), (7,2)]


@app.route('/')
def index():
    return render_template('reservation.html', reserved_seats=reserved_seats) # reserved_seats=reserved_seats can be moved?

@app.route('/admin')
def admin():
    
    return render_template('admin.html')

@app.route('/reservation', methods=['POST'])
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
            flash(f'Reservation successful! Your reservation code is {reservation_code}.
            Row: {row}, Seat: {seat}')
        
            time.sleep(5)
            return redirect(url_for('index'))
    
    def generate_reservation_code(length=12):
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))



    return render_template('reservation.html')

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
    