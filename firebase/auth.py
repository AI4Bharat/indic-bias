import streamlit as st
from firebase_admin import firestore
from collections import defaultdict
import pandas as pd

from db_init import db

def get_annotated_task_breakdown():
    user_data = {}
    
    # Get all users from master collection
    users_ref = db.collection('master')
    users = users_ref.stream()
    
    for user_doc in users:
        user_id = user_doc.id
        user_info = user_doc.to_dict()
        
        # Initialize user structure
        user_data[user_id] = {
            'username': user_info.get('display_name', 'Anonymous'),
            'total_annotated': 0,
            'breakdown': defaultdict(int)
        }
        
        # Get tasks subcollection
        try:
            tasks_ref = users_ref.document(user_id).collection('tasks')
            for task in tasks_ref.stream():
                task_data = task.to_dict()
                
                # Only process annotated tasks
                if task_data.get('is_annotated', False):
                    user_data[user_id]['total_annotated'] += 1
                    
                    # Process axes and types
                    axes = task_data.get('axes', 'N/A').split(', ')
                    types = task_data.get('type', 'N/A').split(', ')
                    
                    # Create category combinations
                    for axis in axes:
                        for task_type in types:
                            key = f"{axis.strip().capitalize()} {task_type.strip().capitalize()}"
                            user_data[user_id]['breakdown'][key] += 1
        
        except Exception as e:
            st.error(f"Error processing tasks for {user_id}: {str(e)}")
    
    # Convert counts to native Python types
    for user in user_data.values():
        user['total_annotated'] = int(user['total_annotated'])
        user['breakdown'] = {k: int(v) for k, v in user['breakdown'].items()}
    
    return user_data

# Streamlit Interface
st.title('Annotated Tasks Breakdown')

# Get data
user_stats = get_annotated_task_breakdown()

# Display nested table
if user_stats:
    for user_id, stats in user_stats.items():
        with st.expander(f"{stats['username']} - {stats['total_annotated']} annotated tasks"):
            if stats['total_annotated'] > 0:
                # Create sorted breakdown
                breakdown_df = pd.DataFrame(
                    sorted(stats['breakdown'].items(), 
                         key=lambda x: x[1], 
                         reverse=True),
                    columns=['Category', 'Count']
                )
                
                # Display with progress bars
                st.dataframe(
                    breakdown_df,
                    column_config={
                        "Category": "Task Type",
                        "Count": st.column_config.ProgressColumn(
                            "Count",
                            format="%d",
                            min_value=0,
                            max_value=int(breakdown_df['Count'].max()) if not breakdown_df.empty else 0
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.write("No annotated tasks found for this user")
else:
    st.warning("No user data found in the database")

# Add refresh button
if st.button('Refresh Data'):
    st.experimental_rerun()