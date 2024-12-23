import random

from firebase import master_ref, firestore
from firebase.question_helpers import get_statements_by_type


def create_task(uuid, axes, statement_type):
    user_tasks_ref = master_ref.document(uuid).collection('tasks')

    statements = get_statements_by_type(axes, statement_type)

    statement_chosen = random.choice(statements)

    task_doc = {
        'createdAt': firestore.SERVER_TIMESTAMP,
        **statement_chosen
    }

    doc = user_tasks_ref.add(task_doc)

    return {'id': doc.id, **task_doc}
