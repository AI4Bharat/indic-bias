import json
import os
import itertools
import random
import logging
from synth_data_gen.agents.agent import Agent
from tqdm import tqdm
from synth_data_gen.prompts.stereotype.generations import generation_agent_prompt
from rich.logging import RichHandler
from joblib import Parallel, delayed
from config import *

stereotypes_file = "synth_data_gen/taxonomy/reverse_stereotype_map.json"
stereotype_identity_map_file = "synth_data_gen/taxonomy/stereotype_map.json"
identity_file = "synth_data_gen/taxonomy/identites.json"

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True, show_level=True, show_time=True),
        logging.FileHandler("TEMP.log")
    ]
)

def initialize():
    #function to create required empty directories to store the logs and data outputs
    pass

def get_stereotypes():
    with open(stereotypes_file, 'r') as f:
        stereotypes = json.load(f)
        
    return stereotypes

def get_identities():
    with open(identity_file, 'r') as f:
        identities = json.load(f)
        
    return identities

def get_stereotype_identity_map():
    with open(stereotype_identity_map_file, 'r') as f:
        stereotype_identity_map = json.load(f)
        
    return stereotype_identity_map


def sample_scenarios(scenarios, num_scenarios_required, strategy="random"):
    if strategy == "random":
        return random.sample(scenarios, num_scenarios_required)
    elif strategy == "sequential":
        return scenarios[:num_scenarios_required]
    elif strategy == "all":
        return scenarios
    else:
        raise ValueError("Invalid strategy")
    
    
def get_scenario_pairs(stereotypes, identities, stereotype_identity_map, sample_stereotypes_per_identity=2):
    all_scenarios = []
    identity_counts = {identity: 0 for identity_type in identities for identity in identities[identity_type]}
    
    for identity_type in stereotypes:
        for stereotype in stereotypes[identity_type]:
            temp_scenarios = []
            
            for identity_1 in stereotypes[identity_type][stereotype]:
                
                # Identities not already covered under the same stereotype
                other_identities = [identity_x for identity_x in identities[identity_type] 
                                    if identity_x not in stereotypes[identity_type][stereotype] and identity_x != identity_1]
                
                for identity_2 in other_identities:
                    
                    # Sample only 2 stereotypes for identity_2 instead of considering all
                    all_stereotype_2 = [strs for cats in stereotype_identity_map[identity_type][identity_2].keys()
                                        for strs in stereotype_identity_map[identity_type][identity_2][cats]]
                    
                    sampled_stereotypes_2 = random.sample(all_stereotype_2, min(len(all_stereotype_2), sample_stereotypes_per_identity))
                    
                    for stereotype_2 in sampled_stereotypes_2:
                        true_pairs = {
                            "identity_1": identity_1,
                            "identity_2": identity_2,
                            "stereotype_1": stereotype,
                            "stereotype_2": stereotype_2
                        }
                        
                        selected_identities = [identity_1, identity_2]
                        selected_stereotypes = [stereotype, stereotype_2]
                        
                        random.shuffle(selected_identities)
                        random.shuffle(selected_stereotypes)
                        
                        temp_scenarios.append({
                            'identity_1': selected_identities[0],
                            'identity_2': selected_identities[1],
                            'stereotype_1': selected_stereotypes[0],
                            'stereotype_2': selected_stereotypes[1],
                            'true_pairs': true_pairs
                        })
            
            all_scenarios.extend(temp_scenarios)
            
    return all_scenarios
                
                
                

def get_templates(prompt, prompt_template):
    try:
        single_prompt_template = prompt_template.format(**prompt)
            
        agent_config = {
            "model_name": "meta-llama/Llama-3.3-70B-Instruct",
            # "model_type": "azure",
            "model_type": "openai",
            "logger": logging.getLogger("rich"),
            # "api_url": AZURE_OPENAI_BASE_URL,
            # "api_key": AZURE_OPENAI_API_KEY,
            # "api_version": AZURE_OPENAI_API_VERSION,
            'api_url': LLAMA3_BASE_URL,
            'api_key': LLAMA3_API_KEY,
            "agent_name": "template_agent",
            "max_tokens": 4096,
            "temperature": 0.8,
            "json_output": True,
            "parser_type": "regular",
            "output_path": "template_outputs.jsonl",
            "single_run_prompt": single_prompt_template,
            "recursive_run_prompt": "",
        }
        
        agent = Agent(config = agent_config, parser = None)
        
        gen_template = agent.run_single()
        gen_template.update(prompt)
        
        return gen_template
    
    except Exception as e:
        logging.error(f"Error generating prompt: {e}")
        return {"status": "error", "error": str(e), "dialect": prompt}
    
    
def filter_templates(results):
    proper_jsons = []
    for result in results:
        proper_jsons.append(result)
        
    final_data = []
    errors = 0
    for template_output in tqdm(proper_jsons):
        try:
            for template_pair in template_output["model_output"]:
                try:
                    final_data.append({
                        "scenario": template_pair["scenario"],
                        "identity_1": template_output["identity_1"],
                        "identity_2": template_output["identity_2"],
                        "stereotype_1": template_output["stereotype_1"],
                        "stereotype_2": template_output["stereotype_2"],
                        "true_pairs": template_output["true_pairs"]
                    })
                except Exception as e:
                    logging.error(f"Error extracting template pair: {e}")
                    errors += 1
        except Exception as e:
            logging.error(f"Error extracting template pair: {e}")
            errors += 1
            
    return final_data

def main(num_scenarios_required, strategy):
    stereotypes = get_stereotypes()
    identities = get_identities()
    stereotype_identity_map = get_stereotype_identity_map()
    
    scenarios = get_scenario_pairs(stereotypes, identities, stereotype_identity_map)
    
    print("Total number of scenarios: ", len(scenarios))
    # print(scenarios[:5])
    
    sampled_scenarios = sample_scenarios(scenarios, num_scenarios_required, strategy)
    
    prompt_template = generation_agent_prompt
    
    results = Parallel(n_jobs=500)(
        delayed(get_templates)(prompt, prompt_template) 
        for prompt in sampled_scenarios
        )
    
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/raw_dump", exist_ok=True)
    with open("data/raw_dump/stereotype_generation_templates_new.jsonl", "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
            
    filtered_templates = filter_templates(results)
    print("Total number of filtered templates: ", len(filtered_templates))
    with open("data/stereotype_generation_templates_new.jsonl", "w") as f:
        for topic in filtered_templates:
            f.write(json.dumps(topic) + "\n")
    
    
if __name__ == "__main__":
    main(5, "all")