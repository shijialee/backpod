from google.cloud import pubsub_v1
from flask import Flask, request

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def feed_url():
    #error = None
    if request.method == 'POST':
        _publish_msg(request.form['url'])
        return "<p>Hello, World!</p>"
    else:
        #return render_template('login.html', error=error)
        return "<p>Hello, World!</p>"


def _publish_msg(url):
    project_id = "backpod"
    topic_id = "rss-feed"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    future = publisher.publish(topic_path, b'', url=url)
    try:
        msg_id = future.result()
        print(f'msg id: {msg_id}')
    except Exception as e:
        print("Error publishing: " + str(e))

    print(f"Published messages to {topic_path}.")
