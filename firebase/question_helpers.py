from google.cloud.firestore_v1.base_query import FieldFilter, And

from firebase import db, questions_ref, master_ref

statements_ref = db.collection('statements')


def get_all_types(uuid):
    result = {'axes': set(),'types': set()}

    tasks_ref = master_ref.document(uuid).collection('tasks')

    for task in tasks_ref.stream():
        result['axes'].add(task.to_dict()['axes'])
        result['types'].add(task.to_dict()['type'])

    result['axes'] = list(result['axes'])
    result['types'] = list(result['types'])
 
    return result


def get_statements_by_type(axes, statement_type,uuid):

    result = []

    tasks_ref = master_ref.document(uuid).collection('tasks')

    query = tasks_ref.where(filter=And([
        FieldFilter('type','==' ,statement_type),
        FieldFilter('axes','==' ,axes),
    ]))

    print(axes,statement_type)


    for statement in query.stream():
        statement = statement.to_dict() | {'id': statement.id}
        result.append(statement)

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


def store_answers(uuid, answer, task_id):

    task_ref = master_ref.document(uuid).collection('tasks').document(task_id)

    task_ref.update({'answers': answer,'is_annotated': True})

    return True
