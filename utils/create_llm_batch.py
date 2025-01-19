import json
import argparse
from utils.json_utils import create_jsonl, dump_jsonl

def create_batch(args, data):
    jsons = []
    for data_dict in data:
        json_dict = create_jsonl(
            cdx = data_dict["id"],
            model_name = args.model_name,
            prompt = data_dict["prompt"],
            max_tokens = args.max_tokens,
            temperature = args.temperature
        )
        jsons.append(json_dict)
        
    dump_jsonl(args, jsons, args.output_path)
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type = str, required = True, help = "Path to the input file")
    parser.add_argument("--output_path", type = str, required = True, help = "Path to the output file")
    parser.add_argument("--model_name", type = str, required = True, help = "Name of the model to use")
    parser.add_argument("--max_tokens", type = int, default = 2048, help = "Maximum tokens to use for generation")
    parser.add_argument("--temperature", type = float, default = 0.8, help = "Temperature to use for generation")
    parser.add_argument("--debug", action = "store_true", help = "Debug mode")
    return parser.parse_args()

def main(args):
    
    data = []
    with open(args.input_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    
    if args.debug:
        data = random.sample(data, 20)
        
    create_batch(args, data)
    
    
    
if __name__ == "__main__":
    args = parse_args()
    main(args)