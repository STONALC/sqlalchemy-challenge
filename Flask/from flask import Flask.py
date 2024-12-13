from flask import Flask

app = Flask(__name__)

@app.route('/api/v1.0/precipitation')
def hawaii.sqlite():
    return "Climate App"

if __name__ == "__main__":
    app.run(debug=True)