from google.cloud import firestore
import logging

def write_data(db, collection, document_id, data, override = False):
    """
    Adds new data to the firestore db
        Args: db (database obj): instascholar
              collection (str): 'papers'
              document_id (str): doi (primary key)
              data (dict)
              override (bool): If set to True, will override an existing entry
    """
    data.update({'timestamp': firestore.SERVER_TIMESTAMP})

    doc_ref = db.collection(collection).document(document_id)
    if doc_ref.get().exists and not override:
        logging.info(f"{document_id} from collection {collection} already exists")
    else:
        doc_ref.set(data)


def read_data(db, collection, document_id):
    """
    Return data dictionary from db
        Args:
            db (databse obj): 'instascholar'
            collection (str): 'papers'
            document_id (str): doi (primary key)
        Returns:
            Data dictionary (dict)
    """
    doc_ref = db.collection(collection).document(document_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
    

def remove_entry(db, collection, document_id):
    """
    Removes entry from db
        Args:
            db (databse obj): 'instascholar'
            collection (str): 'papers'
            document_id (str): doi (primary key)
        Returns:
            Data dictionary (dict)
    """
    try:
        # Create a reference to the document
        doc_ref = db.collection(collection).document(document_id)
        
        # Delete the document
        doc_ref.delete()
        
        logging.info(f"Successfully deleted document with ID: {document_id} from collection: {collection}")
        return True
    except Exception as e:
        logging.info(f"An error occurred while deleting the document: {e}")
        return False