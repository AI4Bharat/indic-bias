from firebase import db

questions_ref = db.collection('questions')


def get_questions():
    result = []
    for question in questions_ref.stream():
        question = question.to_dict() | {'id': question.id}
        result.append(question)

    return result
