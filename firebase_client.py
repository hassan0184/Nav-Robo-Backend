import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from random import randint
from rest_framework.exceptions import ValidationError
from google.cloud.firestore_v1 import ArrayRemove



class FirebaseClient:

    def __init__(self):
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(
                credentials.Certificate("nav-firebase-1de19-firebase-adminsdk-bwafc-0ffa5800a0.json")
            )

        self._db = firestore.client()
        self._collection = self._db.collection(u'robot_data')

    def create(self, data):
        """Create document/record in firestore database"""
        doc_ref = self._collection.document()
        doc_ref.set(data)

    def update(self, id, data):
        """Update document/record on firestore database using document id"""
        doc_ref = self._collection.document(id)
        doc_ref.update(data)

    def delete_by_id(self, id):
        """Delete document/record on firestore database using document id"""
        self._collection.document(id).delete()

    def get_by_id(self, id):
        """Get document/record on firestore database using document id"""
        try:
            doc_ref = self._collection.document(id)
            doc = doc_ref.get()
            return {**doc.to_dict(), "id": doc.id}
        except:
            raise ValidationError("Robot does not exist")

    def all(self):
        """Get all documents/records from firestore database"""
        docs = self._collection.stream()
        return [{**doc.to_dict(), "id": doc.id} for doc in docs]

    def filter(self, field, condition, value):
        """Filter documents/records using conditions on firestore database"""
        docs = self._collection.where(field, condition, value).stream()
        return [{**doc.to_dict(), "id": doc.id} for doc in docs]
    
    def filter_robot(self):
        """Filter documents/records using conditions on firestore database"""
        docs = self._collection.where('status', '==', 'online').where("is_available", '==', True).stream()
        return [{**doc.to_dict(), "id": doc.id} for doc in docs]

    def remove_value_from_array_in_all_docs(self,field_name,value):
        docs = self._collection.stream()
        for doc in docs:
            doc.reference.update({field_name: ArrayRemove([value])})


client = FirebaseClient()

# --------- Get and display all documents/records in the robot_data collection------------
# all_records = client.all()
# print("all records: ", all_records)
# ----------------------------------------------------------------------------------------


# ---------Create a new document/record in the robot_data table--------
# client.create(
#                 {"robot_id": randint(100, 999),
#                "updated_at": firestore.SERVER_TIMESTAMP,
#                "robot_status":False,
#                "location": firestore.GeoPoint(10,20),
#                 "is_available":False})
# ---------------------------------------------------------------------
class FirebaseRobot:

    def __init__(self):
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(
                credentials.Certificate("nav-firebase-1de19-firebase-adminsdk-bwafc-0ffa5800a0.json")
            )

        self._db = firestore.client()
        self._collection = self._db.collection(u'robot_data_from_software_side')

    def create(self, data):
        """Create document/record in firestore database"""
        doc_ref = self._collection.document(data.get('robot_id'))
        doc_ref.set(None)

    def update(self, id, data):
        """Update document/record on firestore database using document id"""
        doc_ref = self._collection.document(id)
        doc_ref.update(data)

    def delete_by_id(self, id):
        """Delete document/record on firestore database using document id"""
        self._collection.document(id).delete()
    
    def delete_all_fields_by_id(self, id):
        """Delete all fields in a document/record on Firebase using the document ID."""
        doc_ref = self._collection.document(id)
        doc = doc_ref.get()
        if doc.exists:
            for field in doc.to_dict().keys():
                doc_ref.update({field: firestore.DELETE_FIELD})

    def get_by_id(self, id):
        """Get document/record on firestore database using document id"""
        doc_ref = self._collection.document(id)
        doc = doc_ref.get()

        if doc.exists:
            return {**doc.to_dict(), "id": doc.id}
        return

    def all(self):
        """Get all documents/records from firestore database"""
        docs = self._collection.stream()
        return [{**doc.to_dict(), "id": doc.id} for doc in docs]

    def filter(self, field, condition, value):
        """Filter documents/records using conditions on firestore database"""
        docs = self._collection.where(field, condition, value).stream()
        return [{**doc.to_dict(), "id": doc.id} for doc in docs]

robot_firebase = FirebaseRobot()
