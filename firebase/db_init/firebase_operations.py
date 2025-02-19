import firebase_admin
from firebase_admin import firestore, auth
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from tqdm import tqdm

db = firestore.client(database_id="indic-bias")

# Distribute statements among users
def distribute_to_users(statements_dict):
    user_emails = [f"user{i}@gmail.com" for i in range(1, 13)]
    rem_elements = []
    count = 0

    for category, sub_list in statements_dict.items():
        total_elements = len(sub_list)
        total_elements_go = total_elements - (total_elements % 12)
        rem_elements.extend(sub_list[total_elements_go:])

        for i, element in enumerate(sub_list[:total_elements_go]):
            user_email = user_emails[i % 12]
            user = auth.get_user_by_email(user_email)
            ref = db.collection("master").document(user.uid)
            sub_ref = ref.collection("tasks")
            sub_ref.document().set(element)
            count += 1

    for i, element in enumerate(rem_elements):
        user_email = user_emails[i % 12]
        user = auth.get_user_by_email(user_email)
        ref = db.collection("master").document(user.uid)
        sub_ref = ref.collection("tasks")
        sub_ref.document().set(element)
        count += 1

    return count

# Filter collection by type
def filter_collection_by_type(type_of_axes):
    col = db.collection("master")
    results = []
    count = 0
    for user in col.stream():
        user_ref = user.reference
        tasks = user_ref.collection("tasks")

        filtered = tasks.where("axes", "==", type_of_axes)
        for task in filtered.stream():
            results.append((task.id, user.id))
            count += 1
    return results

# Delete a collection
def delete_collection(coll_ref, batch_size):
    if batch_size == 0:
        return

    deleted = 0
    for doc in coll_ref.stream():
        print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
        doc.delete()
        deleted += 1

# Delete filtered collections
filtered = filter_collection_by_type("stereotype")

with ProcessPoolExecutor(max_workers=4) as pool:
    futures = [pool.submit(delete_collection, filtered[i], 100) for i in range(len(filtered))]

for _ in tqdm(as_completed(futures), total=len(futures), desc="Deleting Collections"):
    pass  # Wait for completion

# Delete tasks
def delete_task(task_user_pair):
    task_id, user_id = task_user_pair
    ref = db.collection("master").document(user_id).collection("tasks").document(task_id)
    ref.delete()

with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(delete_task, filtered), total=len(filtered), desc="Deleting tasks"))
