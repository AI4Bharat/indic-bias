from google.cloud.firestore_v1.base_query import FieldFilter, And

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


def get_questions_by_type(axes, task_type):
    result = []
    # Fetch questions from Firestore collection
    for question in questions_ref.document('_'.join(axes.lower().split())).collection("questions").stream():
        question = question.to_dict() | {'id': question.id}
        # Filter by 'sub_axe'
        if question.get('sub_axe') == task_type:
            result.append(question)
    return result


def get_statement_by_user(uuid, axes, axes_type):
    result = []
    query = master_ref.document(uuid).collection("tasks").where(
        filter=And([
            FieldFilter('axes', '==', axes),
            FieldFilter('type', '==', axes_type),
            FieldFilter('is_annotated', '==', False)
        ])
    )

    for statement in query.stream():
        statement = statement.to_dict() | {'id': statement.id}
        result.append(statement)
    return result


def store_answers(uuid, answers, task_id):
    firestore_answers = list(answers.values()).copy()

    for question in firestore_answers:
        if question['type'] == 'msq':
            question['answer'] = ",".join(question['answer'])

    task_ref = master_ref.document(uuid).collection("tasks").document(task_id)
    task_ref.update({'is_annotated': True, 'answers': firestore_answers})
