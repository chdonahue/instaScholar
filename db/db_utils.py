from google.cloud import firestore


def write_data(db, collection, document_id, data, override = False):
    """
    Adds new data to the firestore db
        Args: db (database obj): instascholar
              collection (str): 'papers'
              document_id (str): ISSN (primary key)
              data (dict)
              override (bool): If set to True, will override an existing entry
    """
    doc_ref = db.collection(collection).document(document_id)
    if doc_ref.get().exists and not override:
        print('Entry already exists')
    else:
        doc_ref.set(data)


def read_data(db, collection, document_id):
    """
    Return data dictionary from db
        Args:
            db (databse obj): 'instascholar'
            collection (str): 'papers'
            document_id (str): ISSN (primary key)
        Returns:
            Data dictionary (dict)
    """
    doc_ref = db.collection(collection).document(document_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None