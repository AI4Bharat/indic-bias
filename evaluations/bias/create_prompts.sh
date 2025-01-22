identity_types=("religion" "caste" "region")
#identity_type tribe is handled separately
model_list=(
        "llama-3b" "llama-1b" "llama-8b" "llama-70b"
        "gpt-4o" "gpt-4o-mini"
        "gemma-2b" "gemma-9b" "gemma-27b"
        "mistral-small" "mistral-7b" "mixtral"
        "qwen-3b" "qwen-7b" "qwen-14b" "qwen-32b"
        )


#For plausible scenarios task

# for identity_type in "${identity_types[@]}"
# do
#     echo "Creating prompts for ${identity_type}..."
#     python evaluations/bias/create_prompts.py --plausible\
#         --identities_path "synth_data_gen/taxonomy/identites.json" --identity_type $identity_type\
#         --templates_path "data/selection_1/bias_indic_plausible_scenario_templates.jsonl"\
#         --output_path "data/populated_templates/bias/bias_indic_plausible_scenario_${identity_type}.jsonl"

#     for model_name in "${model_list[@]}"
#     do
#         echo "    Creating batch for ${model_name}..."
#         python utils/create_llm_batch.py\
#             --input_path "data/populated_templates/bias/bias_indic_plausible_scenario_${identity_type}_positive.jsonl"\
#             --output_path "data/evaluations/input_batches/bias/bias_indic_plausible_scenario_${identity_type}_positive_${model_name}.jsonl"\
#             --model_name $model_name\
#             --max_tokens 1024\
#             --temperature 0

#         python utils/create_llm_batch.py\
#                 --input_path "data/populated_templates/bias/bias_indic_plausible_scenario_${identity_type}_negative.jsonl"\
#                 --output_path "data/evaluations/input_batches/bias/bias_indic_plausible_scenario_${identity_type}_negative_${model_name}.jsonl"\
#                 --model_name $model_name\
#                 --max_tokens 1024\
#                 --temperature 0
#     done
# done



#for judgement task

# for identity_type in "${identity_types[@]}"
# do
#     echo "Creating prompts for ${identity_type}..."
#     python evaluations/bias/create_prompts.py --judgement\
#         --identities_path "synth_data_gen/taxonomy/identites.json" --identity_type $identity_type\
#         --templates_path "data/selection_1/bias_indic_judgement_templates.jsonl"\
#         --output_path "data/populated_templates/bias/bias_indic_judgement_${identity_type}.jsonl"

#     for model_name in "${model_list[@]}"
#     do
#         echo "    Creating batch for ${model_name}..."
#         python utils/create_llm_batch.py\
#             --input_path "data/populated_templates/bias/bias_indic_judgement_${identity_type}_positive.jsonl"\
#             --output_path "data/evaluations/input_batches/bias/bias_indic_judgement_${identity_type}_positive_${model_name}.jsonl"\
#             --model_name $model_name\
#             --max_tokens 1024\
#             --temperature 0

#         python utils/create_llm_batch.py\
#                 --input_path "data/populated_templates/bias/bias_indic_judgement_${identity_type}_negative.jsonl"\
#                 --output_path "data/evaluations/input_batches/bias/bias_indic_judgement_${identity_type}_negative_${model_name}.jsonl"\
#                 --model_name $model_name\
#                 --max_tokens 1024\
#                 --temperature 0
#     done
# done



#for generation task

for identity_type in "${identity_types[@]}"
do
    echo "Creating prompts for ${identity_type}..."
    python evaluations/bias/create_prompts.py --generation\
        --identities_path "synth_data_gen/taxonomy/identites.json" --identity_type $identity_type\
        --templates_path "data/selection_1/bias_indic_generation_templates.jsonl"\
        --output_path "data/populated_templates/bias/bias_indic_generation_${identity_type}.jsonl"

    for model_name in "${model_list[@]}"
    do
        echo "    Creating batch for ${model_name}..."
        python utils/create_llm_batch.py\
            --input_path "data/populated_templates/bias/bias_indic_generation_${identity_type}_positive.jsonl"\
            --output_path "data/evaluations/input_batches/bias/bias_indic_generation_${identity_type}_positive_${model_name}.jsonl"\
            --model_name $model_name\
            --max_tokens 1024\
            --temperature 0

        python utils/create_llm_batch.py\
                --input_path "data/populated_templates/bias/bias_indic_generation_${identity_type}_negative.jsonl"\
                --output_path "data/evaluations/input_batches/bias/bias_indic_generation_${identity_type}_negative_${model_name}.jsonl"\
                --model_name $model_name\
                --max_tokens 1024\
                --temperature 0
    done
done