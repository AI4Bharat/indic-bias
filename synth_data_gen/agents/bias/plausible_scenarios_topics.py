import json
import os
import itertools
import random
import logging
from agents.agent import Agent
from tqdm import tqdm
from prompts.bias.topics import plausible_scenario_topics_agent_prompt
from rich.logging import RichHandler
from joblib import Parallel, delayed
from config import AZURE_OPENAI_BASE_URL, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION


concepts_file = "taxonomy/bias_concepts.json"
    


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

def get_concepts():
    with open(concepts_file, 'r') as f:
        concepts = json.load(f)
        
    return concepts



def sample_concepts(concepts, num_concepts_required, strategy="random"):
    if strategy == "random":
        return random.sample(concepts, num_concepts_required)
    elif strategy == "sequential":
        return concepts[:num_concepts_required]
    elif strategy == "all":
        return concepts
    else:
        raise ValueError("Invalid strategy")
    
def get_topics(prompt, prompt_template):
    try:
        single_prompt_template = prompt_template.format(**prompt)
            
        agent_config = {
            "model_name": "gpt4o-data-gen",
            "model_type": "azure",
            "logger": logging.getLogger("rich"),
            "api_url": AZURE_OPENAI_BASE_URL,
            "api_key": AZURE_OPENAI_API_KEY,
            "api_version": AZURE_OPENAI_API_VERSION,
            "agent_name": "topic_agent",
            "max_tokens": 4096,
            "temperature": 0.8,
            "json_output": True,
            "parser_type": "regular",
            "output_path": "topic_outputs.jsonl",
            "single_run_prompt": single_prompt_template,
            "recursive_run_prompt": "",
        }
        
        agent = Agent(config = agent_config, parser = None)
        
        gen_intent = agent.run_single()
        gen_intent.update(prompt)
    
        return gen_intent
    except Exception as e:
        logging.error(f"Error generating prompt: {e}")
        return {"status": "error", "error": str(e), "dialect": prompt}
    
    
def filter_topics(results):
    proper_jsons = []
    for result in results:
        proper_jsons.append(result)
        
    final_data = []
    errors = 0
    for topic_output in tqdm(proper_jsons):
        try:
            for topic in topic_output["model_output"]:
                try:
                    final_data.append({
                        "topic": topic["topic"],
                        "topic_description": topic["description"],
                        "concept": topic_output["concept"],
                        "concept_description": topic_output["concept_description"]
                    })
                except Exception as e:
                    print("Error: ", e)
                    errors += 1
                    continue
        except Exception as e:
            print("Error: ", e)
            errors += 1
            continue
        
    return final_data

def main(num_concepts_required, strategy):
    concepts = get_concepts()
                      
                        
    print("Total number of concepts: ", len(concepts))
    
    sampled_concepts = sample_concepts(concepts, num_concepts_required, strategy)
    
    prompt_template = plausible_scenario_topics_agent_prompt
    # print(prompt_template)
        
    results = Parallel(n_jobs=20)(
            delayed(get_topics)(concept, prompt_template)
            for concept in sampled_concepts
        )
        
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/raw_dump", exist_ok=True)
    with open("data/raw_dump/bias_plausible_scenario_topics.jsonl", "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
            
    filtered_topics = filter_topics(results)
    print("Total number of filtered topics: ", len(filtered_topics))
    with open("data/bias_plausible_scenario_topics.jsonl", "w") as f:
        for topic in filtered_topics:
            f.write(json.dumps(topic) + "\n")
    
        
def parse_args():
    pass


if __name__ == "__main__":
    main(5, "all")
    
    
    