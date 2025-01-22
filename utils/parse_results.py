import json

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
