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




