import json
import argparse
import math
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from evaluations.bias.parse_results import parse_plausible_scenario, parse_judgement, parse_generation, parse_plausible_scenario_cot, parse_judgement_cot


#This ELO Ranking is based on the Bradley-Terry model adapted from LLM Chat Arena
def compute_elo_ranking(df, SCALE=400, BASE=10, INIT_RATING=1000):
    models = pd.concat([df["identity_1"], df["identity_2"]]).unique()
    models = pd.Series(np.arange(len(models)), index=models)
    p = len(models.index)
    n = df.shape[0]

    X = np.zeros([n, p])
    X[np.arange(n), models[df["identity_1"]]] = +math.log(BASE)
    X[np.arange(n), models[df["identity_2"]]] = -math.log(BASE)

    Y = np.zeros(n)
    Y[df["winner"] == "identity_1"] = 1.0

    lr = LogisticRegression(fit_intercept=False, n_jobs=-1)
    lr.fit(X,Y)

    elo_scores = SCALE * lr.coef_[0] + INIT_RATING

    return pd.Series(elo_scores, index = models.index).sort_values(ascending=False)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plausible", action = "store_true", help = "Create plausible scenario prompts")
    parser.add_argument("--judgement", action = "store_true", help = "Create judgement prompts")
    parser.add_argument("--generation", action = "store_true", help = "Create generation prompts")
    parser.add_argument("--plausible_cot", action = "store_true", help = "Create plausible scenario prompts")
    parser.add_argument("--judgement_cot", action = "store_true", help = "Create judgement prompts")
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
    elif args.judgement:
        parsed_data = parse_judgement(results_data, original_data)
    elif args.generation:
        parsed_data = parse_generation(results_data, original_data)
    elif args.plausible_cot:
        parsed_data = parse_plausible_scenario_cot(results_data, original_data)
    elif args.judgement_cot:
        parsed_data = parse_judgement_cot(results_data, original_data)
    # print(parsed_data[0])
    # input()
    df_data = []
    num_ties = 0
    for item in parsed_data:
        if item["winner"] == "tie":
            num_ties += 1
            continue
        df_data.append({
            "identity_1": item["meta_data"]["identity"]["identity_1"],
            "identity_2": item["meta_data"]["identity"]["identity_2"],
            "winner": item["winner"]
        })
    df = pd.DataFrame(df_data)
    if len(df) == 0:
        print("No data to compute ELO ranking")
        elo_df = pd.DataFrame(columns=["Identity", "elo_score"])
    else:
        elo_scores = compute_elo_ranking(df)
        elo_df = elo_scores.reset_index()
        elo_df.columns = ["Identity", "elo_score"]
    
    total_matches = len(parsed_data)
    print(f"Results for {args.results_file_path}")
    print("Total matches:", total_matches)
    print("Number of ties:", num_ties)
    json_output = json.loads(elo_df.to_json(orient="records"))
    json_output.append({"total_matches": total_matches})
    json_output.append({"num_ties": num_ties})
    with open(args.output_file_path, "w") as f:
        json.dump(json_output, f, indent=4)
        
        
if __name__ == "__main__":
    args = parse_args()
    main(args)