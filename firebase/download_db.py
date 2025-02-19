import json
import os
import zipfile
from firebase_admin import firestore
from db_init import db

def fetch_all_tasks():
    user_tasks = {}
    users_ref = db.collection('master')
    users = users_ref.stream()
    
    for user_doc in users:
        user_id = user_doc.id
        tasks_ref = users_ref.document(user_id).collection('tasks')
        
        user_tasks[user_id] = []
        try:
            for task in tasks_ref.stream():
                user_tasks[user_id].append(task.to_dict())
        except Exception as e:
            print(f"Error fetching tasks for {user_id}: {str(e)}")
    
    return user_tasks

def save_tasks_to_zip(zip_filename="user_tasks.zip"):
    task_data = fetch_all_tasks()
    os.makedirs("task_jsons", exist_ok=True)
    
    # Save each user's tasks as a separate JSON file
    json_files = []
    for user_id, tasks in task_data.items():
        user_filename = f"task_jsons/{user_id}.json"
        with open(user_filename, "w") as json_file:
            json.dump(tasks, json_file, indent=4)
        json_files.append(user_filename)
    
    # Create a ZIP archive
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for file in json_files:
            zipf.write(file, os.path.basename(file))
    
    print(f"Data saved to {zip_filename}")

if __name__ == "__main__":
    save_tasks_to_zip()
