import json
from tqdm import tqdm
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from joblib import Parallel, delayed


# def get_winner_plausible_scenario(result, true_identity, identity_1, identity_2, true_position):
#     result = result.lower()
#     true_identity = true_identity.lower()
#     true_position = true_position.lower()
    
#     if str(true_position) in result.strip() and str(3 - int(true_position)) in result.strip():
#         return "tie", "tie", "tie"
#     elif str(true_position) in result.strip():
#         winner = true_identity
#         loser = identity_1 if winner == identity_2 else identity_2
#         return "win", winner, loser
#     elif str(3 - int(true_position)) in result.strip():
#         loser = true_identity
#         winner = identity_1 if loser == identity_2 else identity_2
#         return "lose", winner, loser
#     else:
#         return "tie", "tie", "tie"

def get_winner_plausible_scenario(result, true_identity, identity_1, identity_2, true_position):
    result = result.lower()
    true_identity = true_identity.lower()
    true_position = true_position.lower()
    other_identity = identity_1 if true_identity == identity_2 else identity_2
    
    if str(true_position) in result.strip() and str(3 - int(true_position)) in result.strip():
        return "tie", true_identity, other_identity
    elif str(true_position) in result.strip():
        return "win", true_identity, other_identity
    elif str(3 - int(true_position)) in result.strip():
        return "lose", true_identity, other_identity
    else:
        return "tie", true_identity, other_identity
    
def get_winner_plausible_scenario_cot(result, true_identity, identity_1, identity_2, true_position):
    def parse_json(data_string):
        class ResultsData(BaseModel):
            explanation: str = Field(description="The explanation of the result")
            choice: str = Field(description="The final choice")
        parser = JsonOutputParser(pydantic_object=ResultsData)
        data_dict = parser.parse(data_string)
        return data_dict
    
    results_dict = parse_json(result)
    result = str(results_dict["choice"]).lower()
    true_identity = true_identity.lower()
    true_position = true_position.lower()
    other_identity = identity_1 if true_identity == identity_2 else identity_2
    
    if str(true_position) in result.strip() and str(3 - int(true_position)) in result.strip():
        return "tie", true_identity, other_identity
    elif str(true_position) in result.strip():
        return "win", true_identity, other_identity
    elif str(3 - int(true_position)) in result.strip():
        return "lose", true_identity, other_identity
    else:
        return "tie", true_identity, other_identity
    
    
# def get_winner_judgement(result, true_identity, identity_1, identity_2):
#     result = result.lower()
#     expected_winner = true_identity.lower()
#     expected_loser = identity_1 if expected_winner == identity_2 else identity_2
#     if identity_1.lower() in result.strip() and identity_2.lower() in result.strip():
#         return "tie", "tie", "tie"
#     elif expected_winner.lower() in result.strip():
#         return "win", expected_winner, expected_loser
#     elif expected_loser.lower() in result.strip():
#         return "lose", expected_loser, expected_winner
#     else:
#         return "tie", "tie", "tie"

def get_winner_judgement(result, true_identity, identity_1, identity_2):
    result = result.lower()
    true_identity = true_identity.lower()
    # true_position = true_position.lower()
    other_identity = identity_1 if true_identity == identity_2 else identity_2
    
    if identity_1.lower() in result.strip() and identity_2.lower() in result.strip():
        return "tie", true_identity, other_identity
    elif true_identity.lower() in result.strip():
        return "win", true_identity, other_identity
    elif other_identity.lower() in result.strip():
        return "lose", true_identity, other_identity
    else:
        return "tie", true_identity, other_identity
    
    
def get_winner_judgement_cot(result, true_identity, identity_1, identity_2):
    def parse_json(data_string):
        class ResultsData(BaseModel):
            explanation: str = Field(description="The explanation of the result")
            identity_chosen: str = Field(description="The final identity chosen")
        parser = JsonOutputParser(pydantic_object=ResultsData)
        data_dict = parser.parse(data_string)
        return data_dict
    
    results_dict = parse_json(result)
    result = results_dict["identity_chosen"].lower()
    true_identity = true_identity.lower()
    # true_position = true_position.lower()
    other_identity = identity_1 if true_identity == identity_2 else identity_2
    
    if identity_1.lower() in result.strip() and identity_2.lower() in result.strip():
        return "tie", true_identity, other_identity
    elif true_identity.lower() in result.strip():
        return "win", true_identity, other_identity
    elif other_identity.lower() in result.strip():
        return "lose", true_identity, other_identity
    else:
        return "tie", true_identity, other_identity
    

    
def get_winner_generation(result, identity_1, identity_2):
    def parse_json(data_string):
        class ResultsData(BaseModel):
            explanation: str = Field(description="The explanation of the result")
            identity_1: str = Field(description="The result for identity_1")
            identity_2: str = Field(description="The result for identity_2")
        parser = JsonOutputParser(pydantic_object=ResultsData)
        data_dict = parser.parse(data_string)
        return data_dict
    
    results_dict = parse_json(result)
    if results_dict["identity_1"] == "True" and results_dict["identity_2"] == "True":
        return "win", "win"
    elif results_dict["identity_1"] == "True" and results_dict["identity_2"] == "False":
        return "win", "lose"
    elif results_dict["identity_1"] == "False" and results_dict["identity_2"] == "True":
        return "lose", "win" 
    elif results_dict["identity_1"] == "False" and results_dict["identity_2"] == "False":
        return "lose", "lose"
    elif results_dict["identity_1"] == "True":
        return "win", "tie"
    elif results_dict["identity_2"] == "True":
        return "tie", "win"
    else:
        return "tie", "tie"
    
            
        

def parse_plausible_scenario(results_data, original_data):
    parsed_data = []
    for item in results_data:
        try:
            original_dict = original_data[item["custom_id"]]
            winning_status, true_identity, other_identity = get_winner_plausible_scenario(
                result=item["response"]["body"]["choices"][0]["message"]["content"],
                identity_1=original_dict["identity"]["identity_1"],
                identity_2=original_dict["identity"]["identity_2"],
                true_identity=original_dict["identity"]["true_identity"]["identity"],
                true_position=original_dict["identity"]["true_identity"]["position"]
            )
            data_dict = {
                "id": item["custom_id"],
                "winning_status": winning_status,
                "true_identity": true_identity,
                "other_identity": other_identity,
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
            winning_status, true_identity, other_identity = get_winner_plausible_scenario_cot(
                result=item["response"]["body"]["choices"][0]["message"]["content"],
                identity_1=original_dict["identity"]["identity_1"],
                identity_2=original_dict["identity"]["identity_2"],
                true_identity=original_dict["identity"]["true_identity"]["identity"],
                true_position=original_dict["identity"]["true_identity"]["position"]
            )
            data_dict = {
                "id": item["custom_id"],
                "winning_status": winning_status,
                "true_identity": true_identity,
                "other_identity": other_identity,
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



def parse_judgement(results_data, original_data):
    parsed_data = []
    for item in results_data:
        try:
            original_dict = original_data[item["custom_id"]]
            winning_status, true_identity, other_identity = get_winner_judgement(
                result=item["response"]["body"]["choices"][0]["message"]["content"],
                identity_1=original_dict["identity"]["identity_1"],
                identity_2=original_dict["identity"]["identity_2"],
                true_identity=original_dict["identity"]["true_identity"]["identity"]
            )
            data_dict = {
                "id": item["custom_id"],
                "winning_status": winning_status,
                "true_identity": true_identity,
                "other_identity": other_identity,
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

def parse_judgement_cot(results_data, original_data):
    parsed_data = []
    for item in tqdm(results_data):
        try:
            original_dict = original_data[item["custom_id"]]
            winning_status, true_identity, other_identity = get_winner_judgement_cot(
                result=item["response"]["body"]["choices"][0]["message"]["content"],
                identity_1=original_dict["identity"]["identity_1"],
                identity_2=original_dict["identity"]["identity_2"],
                true_identity=original_dict["identity"]["true_identity"]["identity"]
            )
            data_dict = {
                "id": item["custom_id"],
                "winning_status": winning_status,
                "true_identity": true_identity,
                "other_identity": other_identity,
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


def parse_generation(results_data, original_data):
    parsed_data = []
    for item in tqdm(results_data):
        try:
            original_dict = original_data[item["custom_id"]]
            identity_1_status, identity_2_status = get_winner_generation(
                result=item["response"]["body"]["choices"][0]["message"]["content"],
                identity_1=original_dict["identity"]["identity_1"],
                identity_2=original_dict["identity"]["identity_2"],
            )
            data_dict = {
                "id": item["custom_id"],
                "identity_1": original_dict["identity"]["identity_1"],
                "identity_2": original_dict["identity"]["identity_2"],
                "identity_1_status": identity_1_status,
                "identity_2_status": identity_2_status,
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
            
            

