from google.cloud.firestore_v1.base_query import FieldFilter

from firebase import db, questions_ref, master_ref

statements_ref = db.collection('statements')


def get_all_statements():
    result = []
    for question in statements_ref.stream():
        question = question.to_dict() | {'id': question.id}
        result.append(question)

    return result


def get_statements_by_type(axes, statement_type):
    result = []
    for question in statements_ref.where(filter=FieldFilter('axes', '==', axes)).where(filter=FieldFilter('type', '==', statement_type)).stream():
        question = question.to_dict() | {'id': question.id}
        result.append(question)

    return result


def get_questions_by_type(axes):
    result = []
    for question in questions_ref.document(axes.lower()).collection("questions").stream():
        question = question.to_dict() | {'id': question.id}
        result.append(question)
    return result

def get_statement_by_user(uuid, axes, axes_type):
    result = []
    for statement in master_ref.document(uuid).collection("tasks").where(filter=FieldFilter('axes', '==', axes)).where(filter=FieldFilter('type', '==', axes_type)).stream():
        statement = statement.to_dict() | {'id': statement.id}
        result.append(statement)
    return result

