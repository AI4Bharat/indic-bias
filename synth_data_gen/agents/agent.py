import yaml
import pytz
import random
import logging
import jsonlines
from models.openai import *
from datetime import datetime
from utils.parser import JSONparser, LangchainJSONParser
from rich.logging import RichHandler


logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True, show_level=True, show_time=True),
        logging.FileHandler("TEMP.log")
    ]
)

class Agent:
    def __init__(self, config, parser=None):
        self.logger = config["logger"]
        self.api_url = config["api_url"]
        self.api_key = config["api_key"]
        self.model_name = config["model_name"]
        self.agent_name = config["agent_name"]
        self.max_tokens = config["max_tokens"]
        self.temperature = config["temperature"]
        self.output_path = config["output_path"]
        self.output_is_json= config["json_output"]
        self.parser_type = config["parser_type"]
        self.single_run_prompt = config["single_run_prompt"]
        self.recursive_run_prompt = config["recursive_run_prompt"]
        self.model_type = config.get("model_type", "openai")
        self.api_version = config.get("api_version", None)
        self.model = self.get_model(api_url=self.api_url, api_key=self.api_key, api_version=self.api_version)
        self.parser = parser
        
        
    def get_model(self, api_url, api_key, api_version=None):
        if self.model_type == "openai":
            model = OpenAIModel(api_url=api_url, api_key=api_key)
        elif self.model_type == "azure":
            model = AzureOpenAIModel(api_url=api_url, api_key=api_key, api_version=api_version)
        else:
            raise ValueError("Invalid model type. Please provide a valid model type.")
        
        return model

    def run_single(self):

        self.logger.info(f"Executing single run for Agent: {self.agent_name}")
        self.logger.info(
            f"Agent: {self.agent_name} is using the following prompt: {self.single_run_prompt}")
        
        model_output = self.model.infer_model(
            model=self.model_name,
            prompt=self.single_run_prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        if self.parser_type == 'langchain' and self.parser is None and self.output_is_json:
            raise ValueError("Parser object is required for Langchain parser type.")
        elif self.parser_type == 'langchain' and self.output_is_json:
            model_output_text = LangchainJSONParser(markdown_text=model_output.choices[0].message.content, parser=self.parser, model_name=self.model_name)
        elif self.parser_type == 'regular' and self.output_is_json:
            model_output_text = JSONparser(markdown_text=model_output.choices[0].message.content, model_name=self.model_name) 
        else:
            model_output_text = model_output.choices[0].message.content
            
        if model_output_text is None:
            raise ValueError("Model output is empty. Please check the model output.")

        output_dict = {
            "model_name": self.model_name,
            "model_output": model_output_text,
            "input_prompt": self.single_run_prompt,
            "agent_name": self.agent_name,
            "recursive": False,
            "token_usage": {
                "completion_tokens": model_output.usage.completion_tokens,
                "prompt_tokens": model_output.usage.prompt_tokens,
                "total_tokens": model_output.usage.total_tokens
            },
            "metadata": {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": 1.0
            },
            "timestamp": str(datetime.now(pytz.timezone("Asia/Kolkata")))
        }

        self.logger.info(f"Agent: {self.agent_name} produced the following output: {output_dict['model_output']}")

        return output_dict

    def run_recursive(self, n_recursive: int) -> None:
        self.logger.info(f"Running a recursive run for Agent: {self.agent_name}")

        single_output = self.run_single()

        for i in range(n_recursive):
            try:
                self.logger.info(f"Running iteration {i+1} of recursive run for Agent: {self.agent_name}")

                if i == 0:
                    prompt = self.recursive_run_prompt.format(**single_output["model_output"])
                    with jsonlines.open(self.output_path, "a") as writer:
                        writer.write(single_output)

                model_output = self.model.infer_model(
                    model=self.model_name,
                    prompt=prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )

                if model_output == "OPENAI_INVALID_REQUEST":
                    continue

                model_output_text = JSONparser(markdown_text=model_output.choices[0].message.content, model_name=self.model_name) if self.output_is_json else model_output.choices[0].message.content
                prompt = self.recursive_run_prompt.format(**model_output_text)

                output_dict = {
                    "status": "Success",
                    "model_name": self.model_name,
                    "model_output": model_output_text,
                    "input_prompt": prompt,
                    "agent_name": self.agent_name,
                    "recursive": True,
                    "token_usage": {
                        "completion_tokens": model_output.usage.completion_tokens,
                        "prompt_tokens": model_output.usage.prompt_tokens,
                        "total_tokens": model_output.usage.total_tokens
                    },
                    "metadata": {
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "top_p": 1.0
                    },
                    "timestamp": str(datetime.now(pytz.timezone("Asia/Kolkata")))
                }

                self.logger.info(f"Agent: {self.agent_name} produced the following output: {output_dict['model_output']}")

                with jsonlines.open(self.output_path, "a") as writer:
                    writer.write(output_dict)

            except Exception as e:
                self.logger.error(f"Error occurred during recursive run for Agent: {self.agent_name}")
                self.logger.error(f"Error: {e}")
                continue    