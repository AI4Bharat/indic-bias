import os
import json
import argparse
import time
from openai import OpenAI
from config import *


API_KEY = OPENAI_API_KEY
client = OpenAI(api_key=API_KEY)

def merge_files(file_list):
    all_data = []
    for file in file_list:
        with open(file) as f:
            for line in f:
                all_data.append(json.loads(line))
                
    return all_data

def parse_args():
    parser = argparse.ArgumentParser(description='Batch processing')
    parser.add_argument('--create_batch', action="store_true", help='Create a batch job')
    parser.add_argument('--get_results', action="store_true", help='Get results from batch job')
    parser.add_argument('--check_status', action="store_true", help='Check status of batch job')
    parser.add_argument('--tracker_file_path', type=str, help='File path of the tracker file')
    parser.add_argument('--input_file_path', type=str, help='File name of batch job')
    parser.add_argument('--output_file_dir', type=str, help='File name of batch job')
    parser.add_argument('--max_size', type=int, default=40000, help='Max size of the batch job')
    parser.add_argument('--job_desc', type=str, help='Description of batch job')
    args = parser.parse_args()
    return args

def main(args):
    if args.create_batch:
        
        os.makedirs("data/tmp/input_batches", exist_ok=True)
        os.makedirs("data/tmp/output_batches", exist_ok=True)
        
        total_data = []
        with open(args.input_file_path) as f:
            for line in f:
                total_data.append(line)
                
        final_file_paths = []
        if len(total_data) > args.max_size:
            print(f"Splitting the input file into {len(total_data)//args.max_size} batches")
            file_name = args.input_file_path.split("/")[-1].split(".")[0]
            for i in range(0, len(total_data), args.max_size):
                with open(f"data/tmp/input_batches/{file_name}_{i//args.max_size}.jsonl", "w") as f:
                    for line in total_data[i:i+args.max_size]:
                        f.write(line)
                final_file_paths.append(f"data/tmp/input_batches/{file_name}_{i//args.max_size}.jsonl")
        else:
            final_file_paths.append(args.input_file_path)
        
        batch_data = []
        tracker_file_name = args.tracker_file_path
        for file_path in final_file_paths:
            print(f"Creating batch job for {file_path}")
            batch_input_file = client.files.create(
            file=open(f"{file_path}", "rb"),
            purpose="batch"
            )
            batch_input_file_id = batch_input_file.id

            req = client.batches.create(
                input_file_id=batch_input_file_id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={
                "description": args.job_desc
                }
            )

            
            batch_data.append(
                {
                    "batch_id": req.id,
                    "file_name": file_path.split("/")[-1],
                    "input_batch_path": file_path,
                    "main_input_file_path": args.input_file_path
                }
            )
            
        with open(args.tracker_file_path, 'w') as f:
            json.dump(batch_data, f, indent=4)

    elif args.get_results:
        with open(args.tracker_file_path) as f:
            data = json.load(f)
        
        merge_file_list = []
        main_file_name = data[0]["main_input_file_path"].split("/")[-1].split(".")[0]
        while True:
            for job in data:    
                #first check status
                status = client.batches.retrieve(job['batch_id']).to_dict()
                # print(status)
                sleep_flag = True
                if status['status'] == "completed" or status['status'] == "expired":
                    sleep_flag = False
                    print(f"Collecting {job['file_name']} - batch id: {job['batch_id']}")
                    output_file_id = status['output_file_id']
                    content = client.files.content(output_file_id)
                    jsonl_lines = content.content.decode("utf-8").splitlines()
                    with open(f"data/tmp/output_batches/{job['file_name']}", "w") as f:
                        for line in jsonl_lines:
                            json_obj = json.loads(line)
                            f.write(json.dumps(json_obj) + "\n")
                    merge_file_list.append(f"data/tmp/output_batches/{job['file_name']}")
                    data.remove(job)
                elif status['status'] == 'cancelled':
                    sleep_flag = False
                    data.remove(job)
                    continue
                else:
                    print(f"Batch job {job['batch_id']} is still in progress")
                    continue
                
            if len(data) == 0:
                break
            if sleep_flag:
                time.sleep(60)
                
            
        all_data = merge_files(merge_file_list)
        with open(f"{args.output_file_dir}/{main_file_name}.jsonl", "w") as f:
            for line in all_data:
                f.write(json.dumps(line) + "\n")



if __name__ == '__main__':
    args = parse_args()
    main(args)