import re
import json
from synth_data_gen.models.openai import *
from langchain_core.output_parsers import JsonOutputParser

def fix_json(json_str: str, model_name: str, max_tokens: int, temperature: float) -> dict:
    model = OpenAIModel(api_url="http://localhost:8000/v1", api_key="token-123")

    json_fix_prompt = """
    Fix the JSON below. Ensure that the JSON is valid and follows the correct structure. Only return the fixed JSON.\n
    {broken_json}
    """

    model_output = model.infer_model(
        model=model_name,
        prompt=json_fix_prompt.format(broken_json=json_str),
        max_tokens=max_tokens,
        temperature=temperature
    )

    fixed_json = JSONparser(markdown_text=model_output.choices[0].message.content, model_name=model_name)

    return fixed_json



def JSONparser(markdown_text: str, model_name: str) -> dict:
    try:
        parser = JsonOutputParser()
        result = parser.parse(markdown_text)

        # if match:
        #     json_str = match.group(0) 

        #     try:
        #         data = json_repair.loads(json_str)
                
        #     except json.JSONDecodeError:
        #         raise ValueError(f"Error decoding JSON:\n{json_str}")
            
        #     return data
        if result:
            return result
        
        else:
            print(f"No JSON found in the markdown text:\n{markdown_text}")
            raise ValueError("No JSON found in the markdown text.")
    
    except Exception as e:

        print(f"Error parsing JSON: {e}")
        print(f"Deploying fix for the JSON.. please wait..")
        fixed_json = fix_json(json_str=markdown_text, model_name="meta-llama/Llama-3.3-70B-Instruct", max_tokens=8192, temperature=0.2)

        return fixed_json
    
def LangchainJSONParser(markdown_text, parser, model_name):
        
    try:
        result = parser.parse(markdown_text)
        return result
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(f"Deploying fix for the JSON.. please wait..")
        return None