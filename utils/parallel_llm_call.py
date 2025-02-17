import os
import json
import argparse
import backoff
import logging
from tqdm import tqdm
from openai import OpenAI, AzureOpenAI
from openai import RateLimitError as OpenAIRateLimitError
from joblib import Parallel, delayed
from anthropic import Anthropic
from anthropic import RateLimitError as AnthropicRateLimitError
from config import *



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def read_jsonl(file_name):
    results_data = []
    with open(file_name) as f:
        for line in f:
            results_data.append(json.loads(line))
    return results_data

def write_jsonl(file_name, responses):
    with open(file_name, 'w') as f:
        for response in responses:
            f.write(json.dumps(response) + '\n')
            
def format_anthropic_messages(messages):
    formatted_messages = []
    for message in messages:
        if message['role'] == 'system':
            system_prompt = message['content']
            continue
        else:
            formatted_message = {
                'role': message['role'],
                'content': [
                    {
                        "type": "text",
                        "text": message['content']
                    }
                ]
            }
            formatted_messages.append(formatted_message)
    return system_prompt, formatted_messages


def format_openai_result_dict(res, custom_id):
    result_dict = {
            'id' : f"parallel_req_{res['id']}",
            "custom_id": custom_id,
            "response": {
                "status_code": 200,
                "request_id": None,
                "body":{
                    "id": res['id'],
                    "object": "chat.completion",
                    "created": res['created'],
                    "model": res['model'],
                    "choices": res['choices'],
                    "usage": res['usage'],
                    "system_fingerprint": res['system_fingerprint']
                }
            },
            "error": None
        }
    return result_dict

def format_anthropic_result_dict(res, custom_id):
    result_dict = {
            'id' : f"parallel_req_{res['id']}",
            "custom_id": custom_id,
            "response": {
                "status_code": 200,
                "request_id": None,
                "body":{
                    "id": res['id'],
                    "object": "chat.completion",
                    "created": None,
                    "model": res['model'],
                    "choices": [{
                        'finish_reason': res['stop_reason'],
                        'index': 0,
                        'logprobs': None,
                        'message': {
                            'content': res['content'][0]['text'],
                            'role': res['role'],
                            'function_call': None,
                            'tools_call': None,
                            'name': None
                        }
                    }],
                    "usage": res['usage'],
                    "system_fingerprint": None
                }
            },
            "error": None
        }
    return result_dict


def call_openai(data_dict):
    openai_client = OpenAI(api_key = OPENAI_API_KEY)
    
    model = data_dict['body']['model']
    max_tokens = data_dict['body']['max_tokens']
    temperature = data_dict['body']['temperature']
    custom_id = data_dict['custom_id']
    messages = data_dict['body']['messages']
    
    try:
        res = openai_client.chat.completions.create(
            model = model, 
            messages = messages,
            max_tokens = max_tokens, 
            temperature = temperature
        )
        return_res = format_openai_result_dict(res.model_dump(), custom_id)
        return return_res
    except OpenAIRateLimitError as e:
        raise
    except Exception as e:
        print(e)
        logger.error(f"Error processing request for custom_id={custom_id}: {str(e)}")
        return {'error': str(e), 'custom_id': custom_id}
    
    
def call_azure_openai(data_dict):
    azure_openai_client = AzureOpenAI(
        azure_endpoint = AZURE_OPENAI_ENDPOINT,
        api_version = AZURE_OPENAI_API_VERSION,
        api_key = AZURE_OPENAI_API_KEY
        )
    
    if data_dict['body']['model'] == 'azure-gpt-4o':
        model = 'gpt4o-data-gen'
    # model = data_dict['body']['model']
    max_tokens = data_dict['body']['max_tokens']
    temperature = data_dict['body']['temperature']
    custom_id = data_dict['custom_id']
    messages = data_dict['body']['messages']
    
    try:
        res = azure_openai_client.chat.completions.create(
            model = model, 
            messages = messages,
            max_tokens = max_tokens, 
            temperature = temperature
        )
        return_res = format_openai_result_dict(res.model_dump(), custom_id)
        return return_res
    except OpenAIRateLimitError as e:
        raise
    except Exception as e:
        print(e)
        logger.error(f"Error processing request for custom_id={custom_id}: {str(e)}")
        return {'error': str(e), 'custom_id': custom_id}
        
        
def call_llama3(data_dict):
    openai_client = OpenAI(
        base_url = LLAMA3_BASE_URL,
        api_key = LLAMA3_API_KEY
    )
    
    model_map = {
        'llama-1b': 'meta-llama/Llama-3.2-1B-Instruct',
        'llama-3b': 'meta-llama/Llama-3.2-3B-Instruct',
        'llama-8b': 'meta-llama/Llama-3.1-8B-Instruct',
        'llama-70b': 'meta-llama/Llama-3.3-70B-Instruct'
    }
    
    model = model_map[data_dict['body']['model']]
    max_tokens = data_dict['body']['max_tokens']
    temperature = data_dict['body']['temperature']
    custom_id = data_dict['custom_id']
    messages = data_dict['body']['messages']
    
    try:
        res = openai_client.chat.completions.create(
            model = model, 
            messages = messages,
            max_tokens = max_tokens, 
            temperature = temperature
        )
        return_res = format_openai_result_dict(res.model_dump(), custom_id)
        return return_res
    except OpenAIRateLimitError as e:
        raise
    except Exception as e:
        print(e)
        logger.error(f"Error processing request for custom_id={custom_id}: {str(e)}")
        return {'error': str(e), 'custom_id': custom_id}
    

def call_claude(data_dict):
    anthropic_client = Anthropic(
        api_key = CLAUDE_API_KEY
    )
    
    model = data_dict['body']['model']
    if model == 'claude3-opus':
        model = 'claude-3-opus-20240229'
    max_tokens = data_dict['body']['max_tokens']
    temperature = data_dict['body']['temperature']
    custom_id = data_dict['custom_id']
    system_prompt, messages = format_anthropic_messages(data_dict['body']['messages'])
    
    try:
        res = anthropic_client.messages.create(
            model = model,
            max_tokens = max_tokens,
            temperature = temperature,
            system = system_prompt,
            messages = messages
        )
        return_res = format_anthropic_result_dict(res.to_dict(), custom_id)
        return return_res
    except AnthropicRateLimitError as e:
        raise
    except Exception as e:
        print(e)
        logger.error(f"Error processing request for custom_id={custom_id}: {str(e)}")
        return {'error': str(e), 'custom_id': custom_id}
    

def call_gemma(data_dict):
    openai_client = OpenAI(
        base_url = GEMMA_BASE_URL,
        api_key = GEMMA_API_KEY
    )
    
    model_map = {
        'gemma-2b': 'google/gemma-2-2b-it',
        'gemma-9b': 'google/gemma-2-9b-it',
        'gemma-27b': 'google/gemma-2-27b-it'
    }
    
    model = model_map[data_dict['body']['model']]
    max_tokens = data_dict['body']['max_tokens']
    temperature = data_dict['body']['temperature']
    custom_id = data_dict['custom_id']
    if "system" in data_dict['body']['messages'][0]['role']:
        messages = data_dict['body']['messages'][1:]
    else:
        messages = data_dict['body']['messages']
    
    try:
        res = openai_client.chat.completions.create(
            model = model, 
            messages = messages,
            max_tokens = max_tokens, 
            temperature = temperature
        )
        return_res = format_openai_result_dict(res.model_dump(), custom_id)
        return return_res
    except OpenAIRateLimitError as e:
        raise
    except Exception as e:
        print(e)
        logger.error(f"Error processing request for custom_id={custom_id}: {str(e)}")
        return {'error': str(e), 'custom_id': custom_id}

def call_mistral(data_dict):
    openai_client = OpenAI(
        base_url = MISTRAL_BASE_URL,
        api_key = MISTRAL_API_KEY
    )
    
    model_map = {
        'mistral-7b': 'mistralai/Mistral-7B-Instruct-v0.3', 
        'mixtral': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
        'mistral-small': 'mistralai/Mistral-Small-Instruct-2409'
    }
    
    model = model_map[data_dict['body']['model']]
    max_tokens = data_dict['body']['max_tokens']
    temperature = data_dict['body']['temperature']
    custom_id = data_dict['custom_id']
    messages = data_dict['body']['messages']
    
    try:
        res = openai_client.chat.completions.create(
            model = model, 
            messages = messages,
            max_tokens = max_tokens, 
            temperature = temperature
        )
        return_res = format_openai_result_dict(res.model_dump(), custom_id)
        return return_res
    except OpenAIRateLimitError as e:
        raise
    except Exception as e:
        print(e)
        logger.error(f"Error processing request for custom_id={custom_id}: {str(e)}")
        return {'error': str(e), 'custom_id': custom_id}

def call_qwen(data_dict):
    openai_client = OpenAI(
        base_url = QWEN_BASE_URL,
        api_key = QWEN_API_KEY
    )
    
    model_map = {
        'qwen-3b': 'Qwen/Qwen2.5-3B-Instruct',
        'qwen-7b': 'Qwen/Qwen2.5-7B-Instruct',
        'qwen-14b': 'Qwen/Qwen2.5-14B-Instruct',
        'qwen-32b': 'Qwen/Qwen2.5-32B-Instruct'
    }
    
    model = model_map[data_dict['body']['model']]
    max_tokens = data_dict['body']['max_tokens']
    temperature = data_dict['body']['temperature']
    custom_id = data_dict['custom_id']
    messages = data_dict['body']['messages']
    
    try:
        res = openai_client.chat.completions.create(
            model = model, 
            messages = messages,
            max_tokens = max_tokens, 
            temperature = temperature
        )
        return_res = format_openai_result_dict(res.model_dump(), custom_id)
        return return_res
    except OpenAIRateLimitError as e:
        raise
    except Exception as e:
        print(e)
        logger.error(f"Error processing request for custom_id={custom_id}: {str(e)}")
        return {'error': str(e), 'custom_id': custom_id}

    


@backoff.on_exception(backoff.expo, OpenAIRateLimitError)
def backoff_openai_call(data_dict):
    return call_openai(data_dict)

@backoff.on_exception(backoff.expo, Exception)
def backoff_azure_openai_call(data_dict):
    return call_azure_openai(data_dict)
    
@backoff.on_exception(backoff.expo, OpenAIRateLimitError)
def backoff_llama3_call(data_dict):
    return call_llama3(data_dict)

@backoff.on_exception(backoff.expo, Exception)
def backoff_claude_call(data_dict):
    return call_claude(data_dict)

@backoff.on_exception(backoff.expo, OpenAIRateLimitError)
def backoff_gemma_call(data_dict):
    return call_gemma(data_dict)

@backoff.on_exception(backoff.expo, OpenAIRateLimitError)
def backoff_mistral_call(data_dict):
    return call_mistral(data_dict)

@backoff.on_exception(backoff.expo, OpenAIRateLimitError)
def backoff_qwen_call(data_dict):
    return call_qwen(data_dict)

        
    
    

def parse_args():
    parser = argparse.ArgumentParser(description = 'parallel processing')
    parser.add_argument("--input_file_name", type=str, help = "Input file name")
    parser.add_argument("--output_file_name", type=str, help = "Output file name")
    parser.add_argument("--n_jobs", type=int, help = "Number of parallel jobs to run")
    parser.add_argument("--debug", action = 'store_true', help = "Debug mode")
    args = parser.parse_args()
    return args

def main(args):
    data = read_jsonl(args.input_file_name)
    if args.debug:
        data = data[:500]
    #check the model type
    if data[0]['body']['model'] in ['gpt-4o', 'gpt-4o-mini']:
        results = Parallel(n_jobs = args.n_jobs)(delayed(backoff_openai_call)(data_dict) for data_dict in tqdm(data))
        write_jsonl(args.output_file_name, results)
    elif data[0]['body']['model'] in ['azure-gpt-4o', 'azure-gpt-4o-mini']:
        results = Parallel(n_jobs = args.n_jobs)(delayed(backoff_azure_openai_call)(data_dict) for data_dict in tqdm(data))
        write_jsonl(args.output_file_name, results)
    elif data[0]['body']['model'] in ['llama-1b', 'llama-3b', 'llama-8b', 'llama-70b']:
        results = Parallel(n_jobs = args.n_jobs)(delayed(backoff_llama3_call)(data_dict) for data_dict in tqdm(data))
        write_jsonl(args.output_file_name, results)
    elif data[0]['body']['model'] in ['gemma-2b', 'gemma-9b', 'gemma-27b']:
        results = Parallel(n_jobs = args.n_jobs)(delayed(backoff_gemma_call)(data_dict) for data_dict in tqdm(data))
        write_jsonl(args.output_file_name, results)
    elif data[0]['body']['model'] in ['mistral-small', 'mistral-7b', 'mixtral']:
        results = Parallel(n_jobs = args.n_jobs)(delayed(backoff_mistral_call)(data_dict) for data_dict in tqdm(data))
        write_jsonl(args.output_file_name, results)
    elif data[0]['body']['model'] in ['qwen-3b', 'qwen-7b', 'qwen-14b', 'qwen-32b']:
        results = Parallel(n_jobs = args.n_jobs)(delayed(backoff_qwen_call)(data_dict) for data_dict in tqdm(data))
        write_jsonl(args.output_file_name, results)
    elif data[0]['body']['model'] in ['claude3-opus']:
        results = Parallel(n_jobs = args.n_jobs)(delayed(backoff_claude_call)(data_dict) for data_dict in tqdm(data))
        write_jsonl(args.output_file_name, results)
    # elif data[0]['body']['model'] in ['gemini-1.5-flash', 'gemini-1.5-pro']:
    #     results = Parallel(n_jobs = args.n_jobs)(delayed(backoff_gemini_call)(data_dict) for data_dict in tqdm(data))
    #     write_jsonl(args.output_file_name, results)
    else:
        print("Still pending")

if __name__ == '__main__':
    args = parse_args()
    main(args)