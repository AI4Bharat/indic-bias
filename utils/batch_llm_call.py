import os
import json
import argparse
from openai import OpenAI
from config import *


API_KEY = OPENAI_API_KEY
client = OpenAI(api_key=API_KEY)


def parse_args():
    parser = argparse.ArgumentParser(description='Batch processing')
    parser.add_argument('--create_batch', action="store_true", help='Create a batch job')
    parser.add_argument('--get_results', action="store_true", help='Get results from batch job')
    parser.add_argument('--check_status', action="store_true", help='Check status of batch job')
    parser.add_argument('--tracker_file_path', type=str, help='File path of the tracker file')
    parser.add_argument('--input_file_path', type=str, help='File name of batch job')
    parser.add_argument('--output_file_dir', type=str, help='File name of batch job')
    parser.add_argument('--job_desc', type=str, help='Description of batch job')
    args = parser.parse_args()
    return args

def main(args):
    if args.create_batch:
        batch_input_file = client.files.create(
        file=open(f"{args.input_file_path}", "rb"),
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

        if not os.path.exists(args.tracker_file_path):
            with open(args.tracker_file_path, 'w') as f:
                json.dump([], f)
        
        with open(args.tracker_file_path) as f:
            data = json.load(f)
            data.append(
                {
                    "batch_id": req.id,
                    "file_name": args.input_file_path.split("/")[-1],
                    "input_batch_path": args.input_file_path
                }
            )
        
        with open(args.tracker_file_path, 'w') as f:
            json.dump(data, f, indent=4)

    elif args.get_results:
        with open(args.tracker_file_path) as f:
            data = json.load(f)
        
        for job in data:    
            print(f"Collecting {job['file_name']} - batch id: {job['batch_id']}")
            status = client.batches.retrieve(job['batch_id']).to_dict()
            output_file_id = status['output_file_id']
            content = client.files.content(output_file_id)
            jsonl_lines = content.content.decode("utf-8").splitlines()
            with open(f"{args.output_file_dir}/{job['file_name']}", "w") as f:
                for line in jsonl_lines:
                    json_obj = json.loads(line)
                    f.write(json.dumps(json_obj) + "\n")



if __name__ == '__main__':
    args = parse_args()
    main(args)