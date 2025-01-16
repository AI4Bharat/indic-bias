import json
import os
import itertools
import random
import logging
from synth_data_gen.agents.agent import Agent
from tqdm import tqdm
from synth_data_gen.prompts.bias.generations import generation_agent_prompt
from rich.logging import RichHandler
from joblib import Parallel, delayed
from config import AZURE_OPENAI_BASE_URL, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION


# topics_file = "data/bias_generation_topics.jsonl"
topics_file = "synth_data_gen/taxonomy/bias_indic_topics.jsonl"
    


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

def get_topics():
    topics = []
    with open(topics_file, 'r') as f:
        for line in f:
            topics.append(json.loads(line))
    
    return topics



def sample_topics(topics, num_topics_required, strategy="random"):
    if strategy == "random":
        return random.sample(topics, num_topics_required)
    elif strategy == "sequential":
        return topics[:num_topics_required]
    elif strategy == "all":
        return topics
    else:
        raise ValueError("Invalid strategy")
    
def get_templates(prompt, prompt_template):
    try:
        single_prompt_template = prompt_template.format(**prompt)
            
        agent_config = {
            "model_name": "gpt4o-data-gen",
            "model_type": "azure",
            "logger": logging.getLogger("rich"),
            "api_url": AZURE_OPENAI_BASE_URL,
            "api_key": AZURE_OPENAI_API_KEY,
            "api_version": AZURE_OPENAI_API_VERSION,
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
        
        gen_intent = agent.run_single()
        gen_intent.update(prompt)
    
        return gen_intent
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
                        "positive_template": template_pair["positive"],
                        "negative_template": template_pair["negative"],
                        "topic": template_output["topic"],
                        "topic_description": template_output["topic_description"],
                        "concept": template_output["concept"],
                        "concept_description": template_output["concept_description"]
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

def main(num_topics_required, strategy):
    topics = get_topics()
                      
                        
    print("Total number of topics: ", len(topics))
    
    sampled_topics = sample_topics(topics, num_topics_required, strategy)
    
    prompt_template = generation_agent_prompt
    # print(prompt_template)
        
    results = Parallel(n_jobs=5)(
            delayed(get_templates)(topic, prompt_template)
            for topic in sampled_topics
        )
        
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/raw_dump", exist_ok=True)
    with open("data/raw_dump/bias_indic_generation_templates.jsonl", "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
            
    filtered_templates = filter_templates(results)
    print("Total number of filtered templates: ", len(filtered_templates))
    with open("data/bias_indic_generation_templates.jsonl", "w") as f:
        for topic in filtered_templates:
            f.write(json.dumps(topic) + "\n")
    
        
def parse_args():
    pass


if __name__ == "__main__":
    main(5, "all")
    
    
    