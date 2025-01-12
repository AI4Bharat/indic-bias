from abc import ABC, abstractmethod
from typing import Dict
from langchain_openai import ChatOpenAI, AzureChatOpenAI

import openai

class BaseModel(ABC):
    """
    ABC class to initialize different LLMs.
    """
    
    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the base model with API URL and API key.

        Args:
            api_url (str): The base URL to initialize for the endpoint.
            api_key (str): The API key used for authenticating.
        """
        self.api_url = api_url
        self.api_key = api_key
        
    @abstractmethod
    def format_prompt(self, prompt: str, history: list) -> list:
        """
        Abstract method to be implemented by subclasses for formatting the prompt for the API request.

        Args:
            prompt (str): The initial prompt to start the conversation.
            history (list): The list of previous messages in the conversation.

        Returns:
            list: The formatted prompt for the API request.
        """
        pass

    @abstractmethod
    def infer_model(self, model: str, prompt: list, max_tokens: int = 4096, temperature: float = 0.5) -> Dict:
        """
        Abstract method to be implemented by subclasses for performing inference using the specified model.

        Args:
            model (str): The identifier of the LLM to be used for inference.
            prompt (str): The prompt or input text for the model to generate a response.
            max_tokens (int, optional): The maximum number of tokens to generate in the response. Defaults to 4096.
            temperature (float, optional): The sampling temperature for randomness in the model's response. Defaults to 0.5.

        Returns:
            Dict: The completion response from the API.
        """
        pass
    
    @abstractmethod
    def langchain_model(self, model: str):
        """
        Abstract method to be implemented by subclasses for returning the Langchain-format model.

        Args:
            model (str): The identifier of the AI model to be used for inference.
        """
        pass
        


class OpenAIModel(BaseModel):
    """
    A model for using OpenAI's API.

    Attributes:
        api_url (str): The base URL for the OpenAI API endpoint.
        api_key (str): The API key used for authenticating with the OpenAI API.
    """

    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the Model instance with the OpenAI API client.

        Args:
            api_url (str): The base URL for the OpenAI API endpoint.
            api_key (str): The API key used for authenticating with the OpenAI API.
        """
        super().__init__(api_url, api_key)
        self.client = openai.OpenAI(
            base_url=self.api_url,
            api_key=self.api_key
        )
        
    def format_prompt(self, prompt: str, history: list = None, sys_prompt: str = None ) -> list:
        """
        Formats the prompt for the OpenAI API request. Prompt response pairs are by default stored in OpenAI format.

        Args:
            sys_prompt (str): The system prompt to start the conversation.
            prompt (str): The user prompt to continue the conversation.
            history (list): The list of previous messages in the conversation.

        Returns:
            list: The formatted prompt for the OpenAI API request.
        """
        formatted_prompt = []
        
        if sys_prompt is not None:
            formatted_prompt.append({"role": "system", "content": sys_prompt})
        
        if history is not None:
            formatted_prompt.extend(history)
            
        formatted_prompt.append({"role": "user", "content": prompt})
        
            
        return formatted_prompt

    def infer_model(self, model: str, prompt: str, history: list = None, sys_prompt: str = None, max_tokens: int = 4096, temperature: float = 0.5, top_p: float = 1.0 ) -> Dict:
        """
        Performs inference using the specified AI model from the OpenAI API.

        Args:
            model (str): The identifier of the AI model to be used for inference.
            prompt (str): The prompt or input text for the model to generate a response.
            max_tokens (int, optional): The maximum number of tokens to generate in the response. Defaults to 4096.
            temperature (float, optional): The sampling temperature for randomness in the model's response. Defaults to 0.5.

        Returns:
            Dict: The completion response from the OpenAI API.

        Raises:
            Exception: If any unexpected error occurs during the API call.
            openai.error.InvalidRequestError: If the OpenAI API request is invalid (e.g., 400 errors).
        """
        try:
            completion = self.client.chat.completions.create(
                model=model,
                top_p=top_p, 
                temperature=temperature,
                max_tokens=max_tokens,
                messages=self.format_prompt(
                    prompt=prompt, 
                    history=history,
                    sys_prompt=sys_prompt
                )
            )

            return completion

        except openai.error.InvalidRequestError as e:
            print(f"Caught OpenAI 400 error: {e}")
            return {"error": "OPENAI_INVALID_REQUEST", "details": str(e)}

        except Exception as e:
            raise Exception(f"API call failed: {e}")
        
    def langchain_model(self, model: str, max_tokens: int = 4096, temperature: float = 0, top_p: float = 1.0 ):
        """
        Returns the Langchain-format model for the specified model.

        Args:
            model (str): The identifier of the AI model to be used for inference.
            max_tokens (int, optional): The maximum number of tokens to generate in the response. Defaults to 4096.
            temperature (float, optional): The sampling temperature for randomness in the model's response. Defaults to 0.5.
            top_p (float, optional): The nucleus sampling parameter for the model's response. Defaults to 1.0.
            
            
        """
        
        llm = ChatOpenAI(
            base_url=self.api_url,
            api_key=self.api_key,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        
        return llm
        
        

class AzureOpenAIModel(BaseModel):
    """
    A model for using OpenAI's API.

    Attributes:
        api_url (str): The base URL for the OpenAI API endpoint.
        api_key (str): The API key used for authenticating with the OpenAI API.
    """

    def __init__(self, api_url: str, api_key: str, api_version: str):
        """
        Initialize the Model instance with the OpenAI API client.

        Args:
            api_url (str): The base URL for the OpenAI API endpoint.
            api_key (str): The API key used for authenticating with the OpenAI API.
        """
        super().__init__(api_url, api_key)
        self.client = openai.AzureOpenAI(
            azure_endpoint=self.api_url,
            api_key=self.api_key,
            api_version=api_version
        )
        
    def format_prompt(self, prompt: str, history: list = None, sys_prompt: str = None ) -> list:
        """
        Formats the prompt for the OpenAI API request. Prompt response pairs are by default stored in OpenAI format.

        Args:
            sys_prompt (str): The system prompt to start the conversation.
            prompt (str): The user prompt to continue the conversation.
            history (list): The list of previous messages in the conversation.

        Returns:
            list: The formatted prompt for the OpenAI API request.
        """
        formatted_prompt = []
        
        if sys_prompt is not None:
            formatted_prompt.append({"role": "system", "content": sys_prompt})
        
        if history is not None:
            formatted_prompt.extend(history)
            
        formatted_prompt.append({"role": "user", "content": prompt})
        
            
        return formatted_prompt

    def infer_model(self, model: str, prompt: str, history: list = None, sys_prompt: str = None,max_tokens: int = 4096, temperature: float = 0.5, top_p: float = 1.0 ) -> Dict:
        """
        Performs inference using the specified AI model from the OpenAI API.

        Args:
            model (str): The identifier of the AI model to be used for inference.
            prompt (str): The prompt or input text for the model to generate a response.
            max_tokens (int, optional): The maximum number of tokens to generate in the response. Defaults to 4096.
            temperature (float, optional): The sampling temperature for randomness in the model's response. Defaults to 0.5.

        Returns:
            Dict: The completion response from the OpenAI API.

        Raises:
            Exception: If any unexpected error occurs during the API call.
            openai.error.InvalidRequestError: If the OpenAI API request is invalid (e.g., 400 errors).
        """
        try:
            completion = self.client.chat.completions.create(
                model=model,
                top_p=top_p, 
                temperature=temperature,
                max_tokens=max_tokens,
                messages=self.format_prompt(
                    prompt=prompt, 
                    history=history,
                    sys_prompt=sys_prompt
                )
            )

            return completion

        except openai.error.InvalidRequestError as e:
            print(f"Caught OpenAI 400 error: {e}")
            return {"error": "OPENAI_INVALID_REQUEST", "details": str(e)}

        except Exception as e:
            raise Exception(f"API call failed: {e}")
        
    def langchain_model(self, model: str, max_tokens: int = 4096, temperature: float = 0, top_p: float = 1.0 ):
        """
        Returns the Langchain-format model for the specified model.

        Args:
            model (str): The identifier of the AI model to be used for inference.
            max_tokens (int, optional): The maximum number of tokens to generate in the response. Defaults to 4096.
            temperature (float, optional): The sampling temperature for randomness in the model's response. Defaults to 0.5.
            top_p (float, optional): The nucleus sampling parameter for the model's response. Defaults to 1.0.
            
            
        """
        
        llm = AzureChatOpenAI(
            azure_endpoint=self.api_url,
            api_key=self.api_key,
            api_version=self.api_version,
            azure_deployment=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        
        return llm
