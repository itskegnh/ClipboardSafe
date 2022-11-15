import flask, hashlib, pymongo, time, datetime

with open('mongo.secret', 'r') as f:
    mongo = f.read().strip().split(';')

client = pymongo.MongoClient(f'mongodb+srv://{mongo[0]}:{mongo[1]}@clipboardapps.ty4zpdd.mongodb.net/?retryWrites=true&w=majority')
db = client['safe']

app = flask.Flask(__name__)

@app.route('/')
def index():
    ...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)