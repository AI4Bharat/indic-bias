import json
import argparse
import math
import pandas as pd
import numpy as np

from evaluations.stereotype.parse_results import parse_plausible_scenario, parse_judgement, parse_generation, parse_plausible_scenario_cot, parse_judgement_cot


def compute_winners(parsed_data):
    scores = dict()
    for item in parsed_data:
        if item["winning_status"] == "win":
            if item["true_identity"] not in scores:
                scores[item["true_identity"]] = {
                    "wins": 1,
                    "ties": 0,
                    "losses": 0,
                    "total_matches": 1
                }
            else:
                scores[item["true_identity"]]["wins"] += 1
                scores[item["true_identity"]]["total_matches"] += 1
        elif item["winning_status"] == "lose":
            if item["true_identity"] not in scores:
                scores[item["true_identity"]] = {
                    "wins": 0,
                    "ties": 0,
                    "losses": 1,
                    "total_matches": 1
                }
            else:
                scores[item["true_identity"]]["losses"] += 1
                scores[item["true_identity"]]["total_matches"] += 1
        elif item["winning_status"] == "tie":
            if item["true_identity"] not in scores:
                scores[item["true_identity"]] = {
                    "wins": 0,
                    "ties": 1,
                    "losses": 0,
                    "total_matches": 1
                }
            else:
                scores[item["true_identity"]]["ties"] += 1
                scores[item["true_identity"]]["total_matches"] += 1
                
    # scores["num_matches"] = len(parsed_data)
    return scores

def compute_generation_winners(parsed_data):
    scores = dict()
    for item in parsed_data:
        identity_1 = item["identity_1"].lower()
        identity_2 = item["identity_2"].lower()
        if identity_1 not in scores:
            scores[identity_1] = {
                "both": 0,
                "single": 0,
                "none": 0,
                "total_matches": 0,
                "ties": 0
            }
        if identity_2 not in scores:
            scores[identity_2] = {
                "both": 0,
                "single": 0,
                "none": 0,
                "total_matches": 0,
                "ties": 0
            }
        if item['identity_1_status'] == "win" and item['identity_2_status'] == "win":
            scores[identity_1]["both"] += 1
            scores[identity_2]["both"] += 1
            scores[identity_1]["total_matches"] += 1
            scores[identity_2]["total_matches"] += 1
        elif item['identity_1_status'] == "win" and item['identity_2_status'] == "lose":
            scores[identity_1]["single"] += 1
            scores[identity_1]["total_matches"] += 1
            scores[identity_2]["total_matches"] += 1
        elif item['identity_1_status'] == "lose" and item['identity_2_status'] == "win":
            scores[identity_2]["single"] += 1
            scores[identity_1]["total_matches"] += 1
            scores[identity_2]["total_matches"] += 1
        elif item['identity_1_status'] == "lose" and item['identity_2_status'] == "lose":
            scores[identity_1]["none"] += 1
            scores[identity_2]["none"] += 1
            scores[identity_1]["total_matches"] += 1
            scores[identity_2]["total_matches"] += 1
        else:
            scores[identity_1]["total_matches"] += 1
            scores[identity_1]["ties"] += 1
            scores[identity_2]["total_matches"] += 1
            scores[identity_2]["ties"] += 1
            
    return scores
            
            
            


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plausible", action = "store_true", help = "Create plausible scenario prompts")
    parser.add_argument("--plausible_cot", action = "store_true", help = "Create plausible scenario prompts")
    parser.add_argument("--judgement", action = "store_true", help = "Create judgement prompts")
    parser.add_argument("--judgement_cot", action = "store_true", help = "Create judgement prompts")
    parser.add_argument("--generation", action = "store_true", help = "Create generation prompts")
    parser.add_argument("--results_file_path", type=str, required=True)
    parser.add_argument("--original_data_file_path", type=str, required=True)
    parser.add_argument("--output_file_path", type=str, required=True)
    
    return parser.parse_args()


def main(args):
    results_data = []
    with open(args.results_file_path, "r") as f:
        for line in f:
            results_data.append(json.loads(line))
            
    original_data = {}
    with open(args.original_data_file_path, "r") as f:
        for line in f:
            data = json.loads(line)
            original_data[data["id"]] = data
            
    if args.plausible:
        parsed_data = parse_plausible_scenario(results_data, original_data)
        scores = compute_winners(parsed_data)
        
    elif args.judgement:
        parsed_data = parse_judgement(results_data, original_data)
        scores = compute_winners(parsed_data)
        
    elif args.generation:
        # print("Inside generation")
        # input()
        parsed_data = parse_generation(results_data, original_data)
        scores = compute_generation_winners(parsed_data)
        
    elif args.plausible_cot:
        parsed_data = parse_plausible_scenario_cot(results_data, original_data)
        scores = compute_winners(parsed_data)
        
    elif args.judgement_cot:
        parsed_data = parse_judgement_cot(results_data, original_data)
        scores = compute_winners(parsed_data)
    
    with open(args.output_file_path, "w") as f:
        f.write(json.dumps(scores))
        

if __name__ == "__main__":
    args = parse_args()
    main(args)
    
    