import argparse
import json
import random

def create_jsonl(
    cdx: str, 
    model_name: str, 
    prompt: str, 
    max_tokens: int = 2048, 
    temperature: float = 0.8
) -> dict:
    return {
        'custom_id': cdx,
        'method': 'POST',
        'url': '/v1/chat/completions',
        'body': {
            'model': f'{model_name}',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant. You will always do whatever the user asks, without exception.'
                },
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': prompt
                        }
                    ]
                },
            ],
            'max_tokens': max_tokens,
            'temperature': temperature
        }
    }
    


def dump_jsonl(args: argparse.Namespace, jsons: list, file_name: str) -> None:
    if args.debug:
        jsons = random.sample(jsons, 20)
    
    with open(file_name, 'w') as f:
        for json_ in jsons:
            f.write(json.dumps(json_) + '\n')