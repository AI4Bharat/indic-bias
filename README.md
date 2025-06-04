# FairI Tales: Evaluation of **Fair**ness in **I**ndian Contexts with a focus on Bias and Stereotypes

FairI = "**Fair**"ness for "**I**"ndia

[📜 Paper](https://arxiv.org/abs/2406.13439) | [🤗 HF Dataset](https://huggingface.co/datasets/ai4bharat/fbi)

We present **Indic-Bias**, a comprehensive benchmark to evaluate the fairness of LLMs across 85 Indian Identity groups, focusing on **Bias** and **Stereotypes**. We create three tasks - Plausibility, Judgment, and Generation, and evaluate 14 popular LLMs to identify allocative and representational harms. 

👉 The detailed list of all the identities can be found [here](https://github.com/AI4Bharat/indic-bias/blob/master/synth_data_gen/taxonomy/identites.json).


## Setup

Install required dependencies:

```bash
pip install -r requirements.txt
```

We use a mix of API-based (e.g., OpenAI, Azure, GCP) and locally hosted models (via [VLLM's OpenAI compatible server](https://docs.vllm.ai/en/v0.8.3/serving/openai_compatible_server.html). Store all API keys, base URLs, and configurations in the `config.py` file.

## Taxonomy Creation
The taxonomy for creating the Indic-Bias benchmark was driven by human experts. 

For Bias, experts first came up with a list of potential social constructs. These were then further expanded to obtain granular topics by prompting GPT-4o to generate task-specific topics. The list of social constructs can be found [here](https://github.com/AI4Bharat/indic-bias/blob/master/synth_data_gen/taxonomy/bias_indic_topics.jsonl). To get granular topics, run the below scripts:

```bash
python synth_data_gen/agents/bias/<task_name>_topics.py
```
where, ```task_name``` is either ```plausible_scenarios``` or ```judgement``` or ```generation```.

For **Stereotype**, we work with expert sociologists and human annotators of the 22 constitutionally recognized Indian languages and come up with a detailed list of potential stereotypes of the different identities considered. The detailed list of stereotypes can be found [here](https://github.com/AI4Bharat/indic-bias/blob/master/synth_data_gen/taxonomy/stereotype_map.json).




## Generating the Benchmark
We use OpenAI's GPT-4o model to generate the benchmark, which is driven by the above manually created taxonomy. We create templates for each task grounded in the topics (both bias and stereotypes). Each template has one/two placeholders of the form ```<identity>``` that are later populated by different identities to create actual benchmark instances that are then sent to various LLMs based on the prompts for each specific task.

To create templates, run the following script for bias:

```bash
python synth_data_gen/agents/bias/<task_name>_templates.py
```
And for stereotypes:
```bash
python synth_data_gen/agents/stereotype/<task_name>_templates.py
```
where, ```task_name``` is either ```plausible_scenarios``` or ```judgement``` or ```generation```.

All the prompts used for creating the data can be found [here](https://github.com/AI4Bharat/indic-bias/tree/master/synth_data_gen/prompts)

## Evaluation
We evaluate 14 popular LLMs, including both open and closed-source models. We accessed the closed-source models via their respective API providers (OpenAI, Azure, and GCP). For open-source LLMs, we host the models via the OpenAI-compatible server provided by [VLLM](https://docs.vllm.ai/en/v0.8.3/serving/openai_compatible_server.html). 

The evaluation process comprises three main steps.

### 1. Create Prompts Batch
The benchmark templates are first populated with different identities to form actual instances. Prompts to be sent to LLMs are then created for each task and are stored in a JSONL batch file. This enables inference using both asynchronous batch mode (as supported by [OpenAI](https://platform.openai.com/docs/guides/batch) and [GCP](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/batch-prediction-gemini)) and conventional synchronous API calls.

Run the following command to create prompts:

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
  - ```--plausible```: For plausible scenario task.
  - ```--plausible_cot```: For plausible scenario task with Chain-of-Thought reasoning.
  - ```--plausible_none```: For plausible scenario task with a "none of the above" option.
  - ```--judgement```: For Judgment task.
  - ```--judgement_cot```: For Judgment task with Chain-of-Thought reasoning.
  - ```--judgement_none```: For Judgment task with a "none of the above" option.
  - ```--generation```: For the Generation task.
- ```IDENTITIES_PATH```: Path to the file containing identity terms (e.g., religion.json, caste.json).
- ```IDENTITY_TYPE```: Type of identity (choose from ```['tribe', 'caste', 'religion', 'region']```).
- ```TEMPLATES_PATH```: Path to the file containing prompt templates in JSON format.
- ```OUTPUT_PATH```: Path to save the generated prompts as a JSON file.

Convert prompts to OpenAI-compatible [batch format](https://platform.openai.com/docs/guides/batch). 

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
Once prompt batches are created, run inference using synchronous or batch API calls.

For synchronous mode:

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

Alternatively, you can use batch APIs (see [`batch_llm_call.py`](https://github.com/AI4Bharat/indic-bias/blob/master/utils/batch_llm_call.py)). 

#### Evaluator LLM
For evaluating the `generation` task, we use the LLM-as-an-Evaluator paradigm, involving a two-step process: creating prompts and then batching them for inference using an evaluator LLM (```Llama-3.3-70B-Instruct``` in our case).

Bias Generation task Evaluator LLM:
```bash
python evaluations/bias/evaluator_llm.py \
  --results_file RESULTS_FILE \
  --original_data_file ORIGINAL_DATA_FILE \
  --templates_file TEMPLATES_FILE \
  --identity_file IDENTITY_FILE \
  --identity_type IDENTITY_TYPE \
  --output_file OUTPUT_FILE
```
or Stereotype Generation task Evaluator LLM:
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

Then create the LLM batch and call the evaluator LLM as discussed above.

### 3. Compute the Results
After inference, parse the model outputs and compute ELO ratings and other task-specific metrics.

Run the below command to parse the results and compute the ELO rating for Bias Tasks.
```bash
python evaluations/bias/compute_elo_ranking.py \
  --<TASK_NAME>
  --results_file_path RESULTS_FILE_PATH \
  --original_data_file_path ORIGINAL_DATA_FILE_PATH \
  --output_file_path OUTPUT_FILE_PATH
```
- ```TASK_NAME```: Flag to specify for which task prompt to create. Possible values here are:
  - ```--plausible```: For plausible scenario task.
  - ```--plausible_cot```: For plausible scenario with CoT task.
  - ```--judgement```: For Judgment task.
  - ```--judgement_cot```: For Judgment CoT task.
  - ```--generation```: For Generation task.
- ```RESULTS_FILE_PATH```: Path to the file containing model results.
- ```ORIGINAL_DATA_FILE_PATH```: Path to the original data used to create the results.
- ```OUTPUT_FILE_PATH```: Path to save the final generated prompts.

Run the below command to compute the Stereotype Association Rates (SAR) for the Stereotype Tasks.

```bash
python evaluations/stereotype/compute_scores.py \
  --<TASK_NAME>
  --results_file_path RESULTS_FILE_PATH \
  --original_data_file_path ORIGINAL_DATA_FILE_PATH \
  --output_file_path OUTPUT_FILE_PATH
```
- ```TASK_NAME```: Flag to specify for which task prompt to create. Possible values here are:
  - ```--plausible```: For plausible scenario task.
  - ```--plausible_cot```: For plausible scenario with CoT task.
  - ```--judgement```: For Judgment task.
  - ```--judgement_cot```: For Judgment CoT task.
  - ```--generation```: For Generation task.
- ```RESULTS_FILE_PATH```: Path to the file containing model results.
- ```ORIGINAL_DATA_FILE_PATH```: Path to the original data used to create the results.
- ```OUTPUT_FILE_PATH```: Path to save the final generated prompts.

## Citation

If you used this repository or our models, please cite our work:

```bibtex
pending
```




