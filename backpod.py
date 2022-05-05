import base64
import json
from flask import Flask, request
from backpod import cli

app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    class Args:
        pass

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

        # Validate the message is a Cloud Storage event.
        if not data["url"] or not data["id"]:
            msg = (
                "Invalid Cloud Storage notification: "
                "expected url and id"
            )
            print(f"error: {msg}")
            return f"Bad Request: {msg}", 400

        args = Args()
        args.url = data['url']
        args.id = data['id']
        try:
            cli.process(args)
            return ("", 204)

        except Exception as e:
            print(f"error: {e}")
            return ("", 500)

    return ("", 500)
