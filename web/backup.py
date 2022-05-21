import functions_framework
import requests
from flask import Flask, make_response, request
from google.cloud import firestore, pubsub_v1

app = Flask(__name__)

db = firestore.Client()
feeds = db.collection('feeds')

publisher = pubsub_v1.PublisherClient()



@app.route('/feed', methods=['POST'])
def feed():
    # is feed exist
    # if not
    #   verify feed url
    # if verified
    #   publish msg
    return 'in feed'


@functions_framework.http
@app.route('/status', methods=['GET'])
def status():
    # verify id
    # return status
    return 'in status'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
