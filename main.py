import base64
import json
from flask import Flask, request
from backpod import cli
from upload import upload

app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    # Decode the Pub/Sub message.
    pubsub_message = envelope["message"]

    print(f"===debug {pubsub_message}")
    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        try:
            data = json.loads(base64.b64decode(pubsub_message["data"]).decode())
        except Exception as e:
            msg = (
                "Invalid Pub/Sub message: "
                "data property is not valid base64 encoded JSON"
            )
            print(f"error: {e}")
            return f"Bad Request: {msg}", 400

        # Validate the message
        if not data["url"] or not data["id"]:
            msg = (
                "Invalid Cloud Storage notification: "
                "expected url and id"
            )
            print(f"error: {msg}")
            return f"Bad Request: {msg}", 400

        try:
            status, filename, filepath = cli.process(data['url'])
            if status:
                # upload file
                print(f'status {status} filename {filename} filepath {filepath}')
                # upload(filepath, filename)
                # update status
                # update(record)
                return ("", 204)
            else:
                return ("got nothing", 204)

        except Exception as e:
            print(f"error: {e}")
            return ("fetch failed", 500)

    return ("bad request", 500)
