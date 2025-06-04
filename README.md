# FairI Tales: Evaluation of **Fair**ness in **I**ndian Contexts with a focus on Bias and Stereotypes

FairI = "**Fair**"ness for "**I**"ndia

[📜 Paper](https://arxiv.org/abs/2406.13439) | [🤗 HF Dataset](https://huggingface.co/datasets/ai4bharat/fbi)

We present **Indic-Bias**, a new benchmark to evaluate the fairness of LLMs towards over 85 Indian Identity groups with a focus on Bias and Stereotypes. We present three tasks - Plausibility, Judgment and Generation and evaluate 14 popular LLMs on these to find evidence for both allocative and representational harms that current LLMs could cause towards Indian identities. The detailed list of all the identities can be found [here](https://github.com/AI4Bharat/indic-bias/blob/master/synth_data_gen/taxonomy/identites.json).

## Setup

To run the data generation and evaluation scripts, you need to install the required packages by running the following command:

```bash
pip install -r requirements.txt
```

We use various API providers including Gemini, Azure, etc for accessing various models. Additionally for open source models, we host the models via the OpenAI compatible server provided by [VLLM](https://docs.vllm.ai/en/v0.8.3/serving/openai_compatible_server.html). Please store all the API keys, base URLs and other environment variables in the ```config.py``` file.

## Taxonomy Creation
The taxonomy for creating the IndicBias benchmark was driven by human experts. For **Bias**, human experts first come up with a list of potential social constructs. These are then further expanded to get granular topics by prompting GPT-4o to get task specific topics. The list of social constructs can be found [here](https://github.com/AI4Bharat/indic-bias/blob/master/synth_data_gen/taxonomy/bias_indic_topics.jsonl). To get granular topics, run the below scripts:

```bash
python synth_data_gen/agents/bias/<task_name>_topics.py
```
where, ```task_name``` is either ```plausible_scenarios``` or ```judgement``` or ```generation```.

For **Stereotype**, we work with expert sociologists and human annotators of the 22 constituionally recognized Indian languages and come up with a detailed list of potential stereotypes of the different identities considered. The detailed list of stereotypes can be found [here](https://github.com/AI4Bharat/indic-bias/blob/master/synth_data_gen/taxonomy/stereotype_map.json).




## Generating the Benchmark
We use OpenAI's GPT-4o model to generate the benchmark which is driven by the above manually created taxonomy. We create templates for each task grounded in the topics (both bias and stereotypes). Each template has one/two placeholders of the form ```<identity>``` that are later populated by different identities to create actual benchmark instances that are then sent to various LLMs based on the prompts for each specific task.

To create templates, run the below scripts for bias:

```bash
python synth_data_gen/agents/bias/<task_name>_templates.py
```
and for stereotypes:
```bash
python synth_data_gen/agents/stereotype/<task_name>_templates.py
```
where, ```task_name``` is either ```plausible_scenarios``` or ```judgement``` or ```generation```.

All the prompts used for creating the data can be found [here](https://github.com/AI4Bharat/indic-bias/tree/master/synth_data_gen/prompts)

## Evaluation
We evaluate 14 popular LLMs including both open and closed-source models. We accessed the closed-source models via their respective API providers (OpenAI, Azure and GCP). For open-source LLMs, we host the models via the OpenAI compatible server provided by [VLLM](https://docs.vllm.ai/en/v0.8.3/serving/openai_compatible_server.html). 

For running the evaluations, we follow a three step process.

### 1. Create Prompts Batch
The benchmark templates are first taken and populated with different identities to form actual instances. Prompts for sending to LLMs are then created based on the task and all are stored in a batch as a jsonl file. The benefit of this is to enable running inference both via asynchronous batch mode (as provided by both [OpenAI](https://platform.openai.com/docs/guides/batch) and [GCP](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/batch-prediction-gemini) or the conventional synchronous API calls.

First, use the following command to create prompts.

```bash
python evaluations/<TYPE>/create_prompts.py \
  --TASK_NAME \
  --identities_path IDENTITIES_PATH \
  --identity_type IDENTITY_TYPE \
  --templates_path TEMPLATES_PATH \
  --output_path OUTPUT_PATH
```
Where, ```<TYPE>``` is ```bias``` or ```stereotype```.
- ```TASK_NAME```: Flag to specify for which task prompt to create. Possible values here are:
  - ```--plausible```: Generate plausible scenario prompts.
  - ```--plausible_cot```: Generate plausible prompts with Chain-of-Thought reasoning.
  - ```--plausible_none```: Add a "none of the above" option to plausible prompts.
  - ```--judgement```: Generate judgmental prompts.
  - ```--judgement_cot```: Generate judgment prompts with Chain-of-Thought reasoning.
  - ```--judgement_none```: Add a "none of the above" option to judgment prompts.
  - ```--generation```: Generate open-ended generation prompts.
- ```IDENTITIES_PATH```: Path to the file containing identity terms (e.g., religion.json, caste.json).
- ```IDENTITY_TYPE```: Type of identity (choose from ```['tribe', 'caste', 'religion', 'region']```).
- ```TEMPLATES_PATH```: Path to the file containing prompt templates in JSON format.
- ```OUTPUT_PATH```: Path to save the generated prompts as a JSON file.

Once the prompts are created, we format them into a batch jsonl file in the as per the [OpenAI standard](https://platform.openai.com/docs/guides/batch). Use the below command to create the prompt batch.


```bash
python utils/create_llm_batch.py \
  --input_path INPUT_PATH \
  --output_path OUTPUT_PATH \
  --model_name MODEL_NAME \
  --max_tokens MAX_TOKENS \
  --temperature TEMPERATURE \
  --debug
```
- ```INPUT_PATH```: Path to the input JSONL file containing prompts.
- ```OUTPUT_PATH```: Path where the model outputs will be saved.
- ```MODEL_NAME```: Name of the model to use. Possible values are `gpt-4o`, `gpt-4o-mini`, `azure-gpt-4o`, `azure-gpt-4o-mini`, `llama-1b`, `llama-3b`, `llama-8b`, `llama-70b`, `gemma-2b`, `gemma-9b`, `gemma-27b`, `mistral-small`, `mistral-7b`, `mixtral`, `qwen-3b`, `qwen-7b`, `qwen-14b`, `qwen-32b`, `claude3-opus`
- ```MAX_TOKENS```: (Default: 2048) Maximum number of tokens to generate per prompt.
- ```TEMPERATURE```: (Default: 0.8) Sampling temperature for controlling output randomness.
- ```--debug```: Optional flag to enable debug mode to create a smaller batch of 500 prompts.

### 2. Call the model
Once the prompt batches are created, we run the inference on the model. We can either run this synchronously using the conventional API or call using batch mode. To run it synchronously, run the below command:

```bash
python utils/parallel_llm_call.py \
  --input_file_name INPUT_FILE_NAME \
  --output_file_name OUTPUT_FILE_NAME \
  --n_jobs N_JOBS \
  --debug
```
- ```INPUT_FILE_NAME```: Path to the input JSONL file, i.e., the batch file created above.
- ```OUTPUT_FILE_NAME```: Path where the processed results will be saved.
- ```N_JOBS```: Number of parallel jobs to run (controls the number of concurrent API calls or model executions).
- ```--debug```: Optional flag to enable debug mode to create a smaller batch of 500 prompts.

Alternatively, one could use Batch API provided by OpenAI and GCP. Check [this](https://github.com/AI4Bharat/indic-bias/blob/master/utils/batch_llm_call.py) script. 

### 3. Evaluator LLM
To evaluate the generation task, we use LLM-as-an-Evaluator paradigm. We again follow a two step process here - create prompt and then create batch. We then call our evaluator LLM (```Llama-3.3-70B-Instruct``` in our case).

To create the prompts, run the below command:

---

Use the following command to generate evaluation prompts for comparing two responses:

```bash
python evaluations/bias/evaluator_llm.py \
  --results_file RESULTS_FILE \
  --original_data_file ORIGINAL_DATA_FILE \
  --templates_file TEMPLATES_FILE \
  --identity_file IDENTITY_FILE \
  --identity_type IDENTITY_TYPE \
  --output_file OUTPUT_FILE
```
or 
```bash
python evaluations/stereotype/evaluator_llm.py \
  --results_file RESULTS_FILE \
  --original_data_file ORIGINAL_DATA_FILE \
  --identity_type IDENTITY_TYPE \
  --output_file OUTPUT_FILE
```
- ```RESULTS_FILE```: Path to the file where the final evaluation prompts will be saved.
- ```ORIGINAL_DATA_FILE```: Path to the input file containing scenarios and responses to evaluate.
- ```TEMPLATES_FILE```: Path to the file containing prompt templates.
- ```IDENTITY_FILE```: Path to the file containing identity terms to inject into prompts.
- ```IDENTITY_TYPE```: Type of identity to use (choose from `religion`, `region`, `caste`, `tribe`).
- ```OUTPUT_FILE```: Path to the output file where generated prompts will be stored.

Then create the llm batch and call the LLM, by following the same previous steps.



