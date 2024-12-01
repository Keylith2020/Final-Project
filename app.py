from flask import Flask, render_template

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/reservation')
def reservation():
    return render_template('reservation.html')

if __name__ == '__main__':
    app.run()
    