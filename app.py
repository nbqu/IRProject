from flask import Flask
from flask import render_template
from flask import request
import IR_lib

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/query_in', methods=['GET'])
def query_in():
    query = request.args.get('query')
    tokenized = IR_lib.process_query(query)

    return render_template('index.html', result=IR_lib.consine_rank(tokenized))


@app.before_first_request
def dfr():
    return IR_lib.init()


if __name__ == '__main__':
    app.run(debug=True)