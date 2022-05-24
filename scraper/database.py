from google.cloud import firestore

db = firestore.Client()


def success(doc_id, filename):
    doc_ref = db.collection('feeds').document(doc_id)
    doc = doc_ref.get()
    if doc.exists:
        data = {
            'filename': filename,
            'status': 'SUCCESS',
            'updated_at': firestore.SERVER_TIMESTAMP,
        }
        doc_ref.update(data)
    else:
        raise RuntimeError(f'id: {doc_id} is not found')


def fail(doc_id):
    doc_ref = db.collection('feeds').document(doc_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({'status': 'FAIL'})
    else:
        raise RuntimeError(f'id: {doc_id} is not found')
