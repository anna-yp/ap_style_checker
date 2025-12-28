from flask import Flask, render_template, request, jsonify, redirect
from services.checker import grammar

app = Flask(__name__)

@app.route('/')
def landing_page():
    return render_template('home.html')

@app.route('/checker', methods=["POST"])
def check_for_grammar():
    # text_content = str(request.form['text-content'])
    text_content = request.json
    # text_content = str(request.form['editor'])
    output = grammar.check_quote_and_pos(text_content)
    return 'testing!'

if __name__ == "__main__":
    port = 5000
    app.run(host="0.0.0.0", port=port, debug=True)
