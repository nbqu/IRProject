from flask import Flask
from flask import render_template
from flask import request
import requests

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/query_in', methods=['GET'])
def query_in():
    query = int(request.args.get('query'))
    return render_template('index.html', query=query)

@app.route('/user/<user_name>/<int:user_id>')
def user(user_name, user_id):
    return f'Hello, {user_name}({user_id})!'

if __name__ == '__main__':
    app.run(debug=True)