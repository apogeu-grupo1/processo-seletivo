from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)