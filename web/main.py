from flask import Flask, request
from google.cloud import firestore, pubsub_v1
import os
import json
from concurrent import futures

app = Flask(__name__)

db = firestore.Client()
feeds = db.collection('feeds')


@app.route('/feeds', methods=['POST'])
def create_feed():
    envelope = request.get_json()
    if not envelope:
        pass

    url = envelope['url'].lower()
    feeds_ref = db.collection('feeds')
    results = list(
        feeds_ref.where('url', '==', url).order_by('created_at').limit(1).stream()
    )

    if len(results) == 0:
        data = {
            'url': url,
            'filename': None,
            'status': 'PENDING',
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
        }
        new_feed_ref = feeds_ref.document()
        new_feed_ref.set(data)

        # publish message {id, url}
        msg = {'id': new_feed_ref.id, 'url': url}
        _publish_msg(msg)

        # get scraper status by visiting backpod.podcastdrill.com/ID
        return {'id': new_feed_ref.id}
    else:
        feed = results[0]
        return {'id': feed.id}


def _validate_url(url):


def _publish_msg(data):
    def callback(future):
        try:
            print(future.result(timeout=30))
        except futures.TimeoutError:
            print(f"Publishing {data} timed out.")

    publisher = pubsub_v1.PublisherClient()
    project_id = os.getenv('PROJECT_ID')
    topic_id = os.getenv('TOPIC_ID')
    topic_path = publisher.topic_path(project_id, topic_id)
    print(f'publish message {data} to {project_id}/{topic_id}')
    future = publisher.publish(topic_path, json.dumps(data).encode("utf-8"))
    # Non-blocking. Publish failures are handled in the callback function.
    future.add_done_callback(callback)


@app.route('/feeds/<feed_id>', methods=['GET'])
def get_feed(feed_id):
    # https://github.com/googleapis/python-firestore/blob/3ec13dac8e/google/cloud/firestore_v1/base_collection.py#L479
    # id is length of 20 based on doc
    if len(feed_id) != 20:
        return 'invalid feed', 400

    doc_ref = db.collection('feeds').document(feed_id)
    doc = doc_ref.get()
    if doc.exists:
        if doc.get('status') == 'PENDING':
            return 'still working on it', 202
        if doc.get('filename'):
            return {'file': doc.get('filename'), 'url': doc.get('url')}
        return 'failed to get feed', 422
    else:
        return '', 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
