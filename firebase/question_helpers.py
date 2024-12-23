from google.cloud.firestore_v1.base_query import FieldFilter

from firebase import db

statements_ref = db.collection('statements')


def get_all_statements():
    result = []
    for question in statements_ref.stream():
        question = question.to_dict() | {'id': question.id}
        result.append(question)

    return result


def get_statements_by_type(axes, type):
    result = []
    for question in statements_ref.where(filter=FieldFilter('axes', '==', axes)).where('type', '==', type).stream():
        question = question.to_dict() | {'id': question.id}
        result.append(question)

    return result
