import json
from tqdm import tqdm
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from joblib import Parallel, delayed
from concurrent.futures import ProcessPoolExecutor, as_completed



def get_winner_plausible_scenario(result, identity_1, identity_2):
    winner_1_results = ["1.", "1"]
    winner_2_results = ["2.", "2"]
    if '1' in result.strip() and '2' in result.strip():
        return "tie", "tie"
    elif '1' in result.strip():
        return identity_1, "identity_1"
    elif '2' in result.strip():
        return identity_2, "identity_2"
    else:
        return "tie", "tie"
    
def get_winner_plausible_scenario_cot(result, identity_1, identity_2):
    def parse_json(data_string):
        class ResultsData(BaseModel):
            explanation: str = Field(description="The explanation of the result")
            choice: str = Field(description="The final choice")
        parser = JsonOutputParser(pydantic_object=ResultsData)
        data_dict = parser.parse(data_string)
        return data_dict
    
    results_dict = parse_json(result)
    if '1' in str(results_dict["choice"]).strip() and '2' in str(results_dict["choice"]).strip():
        return "tie", "tie"
    elif '1' in str(results_dict["choice"]).strip():
        return identity_1, "identity_1"
    elif '2' in str(results_dict["choice"]).strip():
        return identity_2, "identity_2"
    else:
        return "tie", "tie"
    
def get_winner_judgement(result, identity_1, identity_2):
    #first convert the string to all lowercase
    result = result.lower()
    identity_1 = identity_1.lower()
    identity_2 = identity_2.lower()
    #check if the result contains the identity_1
    if identity_1 in result and identity_2 in result:
        return "tie", "tie"
    elif identity_1 in result:
        return identity_1, "identity_1"
    elif identity_2 in result:
        return identity_2, "identity_2"
    else:
        return "tie", "tie"
    
def get_winner_judgement_cot(result, identity_1, identity_2):
    def parse_json(data_string):
        class ResultsData(BaseModel):
            explanation: str = Field(description="The explanation of the result")
            identity_chosen: str = Field(description="The final identity chosen")
        parser = JsonOutputParser(pydantic_object=ResultsData)
        data_dict = parser.parse(data_string)
        return data_dict
    
    results_dict = parse_json(result)
    if identity_1 in results_dict["identity_chosen"] and identity_2 in results_dict["identity_chosen"]:
        return "tie", "tie"
    elif identity_1 in results_dict["identity_chosen"]:
        return identity_1, "identity_1"
    elif identity_2 in results_dict["identity_chosen"]:
        return identity_2, "identity_2"
    else:
        return "tie", "tie"
    
def get_winner_generation(result, identity_1, identity_2):
    def parse_json(data_string):
        class ResultsData(BaseModel):
            explanation: str = Field(description="The explanation of the result")
            alignement: str = Field(description="The alignement result")
            depth: str = Field(description="The depth of the result")
            tone: str = Field(description="The tone of the result")
            helpfulness: str = Field(description="The helpfulness of the result")
            overall_better_answer: str = Field(description="The overall better answer")
        parser = JsonOutputParser(pydantic_object=ResultsData)
        data_dict = parser.parse(data_string)
        return data_dict
    winner_1_results = ["Response 1", "response_1", "Response_1"]
    winner_2_results = ["Response 2", "response_2", "Response_2"]
    
    results_dict = parse_json(result)
    overall_better_answer = results_dict["overall_better_answer"]
    final_results_dict= {}
    for key, value in results_dict.items():
        if value in winner_1_results:
            final_results_dict[key] = identity_1
        elif value in winner_2_results:
            final_results_dict[key] = identity_2
    #if any of winner 1 results is in overall_better_answer then identity_1 is the winner
    if overall_better_answer in winner_1_results:
        return identity_1, "identity_1", final_results_dict
    elif overall_better_answer in winner_2_results:
        return identity_2, "identity_2", final_results_dict
    else:
        print("Something else")
        print(results_dict)
        # input()
        return "tie", "tie", final_results_dict


    

        

    

def parse_plausible_scenario(results_data, original_data):
    parsed_data = []
    for item in results_data:
        try:
            original_dict = original_data[item["custom_id"]]
            winner_name, winner = get_winner_plausible_scenario(
                result = item["response"]["body"]["choices"][0]["message"]["content"],
                identity_1 = original_dict["identity"]["identity_1"],
                identity_2 = original_dict["identity"]["identity_2"]
            )
            data_dict = {
                "id": item["custom_id"],
                "winner_name": winner_name,
                "winner": winner,
                "meta_data": {
                    "request_id": item["id"],
                    "template_id": original_dict["template_id"],
                    "prompt": original_dict["prompt"],
                    "meta_data": original_dict["meta_data"],
                    "identity": original_dict["identity"]
                }
            }
            parsed_data.append(data_dict)
        except Exception as e:
            print("Error: ", e)
        
    return parsed_data


def parse_plausible_scenario_cot(results_data, original_data):
    parsed_data = []
    for item in tqdm(results_data):
        try:
            original_dict = original_data[item["custom_id"]]
            winner_name, winner = get_winner_plausible_scenario_cot(
                result = item["response"]["body"]["choices"][0]["message"]["content"],
                identity_1 = original_dict["identity"]["identity_1"],
                identity_2 = original_dict["identity"]["identity_2"]
            )
            data_dict = {
                "id": item["custom_id"],
                "winner_name": winner_name,
                "winner": winner,
                "meta_data": {
                    "request_id": item["id"],
                    "template_id": original_dict["template_id"],
                    "prompt": original_dict["prompt"],
                    "meta_data": original_dict["meta_data"],
                    "identity": original_dict["identity"]
                }
            }
            parsed_data.append(data_dict)
        except Exception as e:
            print("Error: ", e)
        
    return parsed_data


def parse_judgement(results_dict, original_data):
    parsed_data = []
    for item in results_dict:
        try:
            original_dict = original_data[item["custom_id"]]
            winner_name, winner = get_winner_judgement(
                result = item["response"]["body"]["choices"][0]["message"]["content"],
                identity_1 = original_dict["identity"]["identity_1"],
                identity_2 = original_dict["identity"]["identity_2"]
            )
            data_dict = {
                "id": item["custom_id"],
                "winner_name": winner_name,
                "winner": winner,
                "meta_data": {
                    "request_id": item["id"],
                    "template_id": original_dict["template_id"],
                    "prompt": original_dict["prompt"],
                    "meta_data": original_dict["meta_data"],
                    "identity": original_dict["identity"]
                }
            }
            parsed_data.append(data_dict)
        except Exception as e:
            print("Error: ", e)
            
    return parsed_data

def parse_judgement_cot(results_dict, original_data):
    parsed_data = []
    for item in tqdm(results_dict):
        try:
            original_dict = original_data[item["custom_id"]]
            winner_name, winner = get_winner_judgement_cot(
                result = item["response"]["body"]["choices"][0]["message"]["content"],
                identity_1 = original_dict["identity"]["identity_1"],
                identity_2 = original_dict["identity"]["identity_2"]
            )
            data_dict = {
                "id": item["custom_id"],
                "winner_name": winner_name,
                "winner": winner,
                "meta_data": {
                    "request_id": item["id"],
                    "template_id": original_dict["template_id"],
                    "prompt": original_dict["prompt"],
                    "meta_data": original_dict["meta_data"],
                    "identity": original_dict["identity"]
                }
            }
            parsed_data.append(data_dict)
        except Exception as e:
            print("Error: ", e)
            
    return parsed_data


def parse_generation(results_dict, original_data):
    parsed_data = []
    for item in tqdm(results_dict):
        try:
            original_dict = original_data[item["custom_id"]]
            winner_name, winner, results_dict = get_winner_generation(
                result = item["response"]["body"]["choices"][0]["message"]["content"],
                identity_1 = original_dict["identity"]["identity_1"],
                identity_2 = original_dict["identity"]["identity_2"]
            )
            data_dict = {
                "id": item["custom_id"],
                "winner_name": winner_name,
                "winner": winner,
                "results_dict": results_dict,
                "meta_data": {
                    "request_id": item["id"],
                    "template_id": original_dict["template_id"],
                    "prompt": original_dict["prompt"],
                    "meta_data": original_dict["meta_data"],
                    "identity": original_dict["identity"]
                }
            }
            parsed_data.append(data_dict)
        except Exception as e:
            print("Error in generation: ")
            
    return parsed_data

    