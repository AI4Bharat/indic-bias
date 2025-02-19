import json
import os

# File paths for JSON templates
file_names = [
    "bias_indic_generation_templates.jsonl",
    "bias_indic_judgement_templates.jsonl",
    "bias_indic_plausible_scenario_templates.jsonl",
    "stereotype_generation_templates.jsonl",
    "stereotype_judgement_templates.jsonl",
    "stereotype_plausible_scenario_templates.jsonl",
]

statements_dict = {
    "bias_generation": [],
    "bias_judgement": [],
    "bias_plausible": [],
    "stereotype_generation": [],
    "stereotype_judgement": [],
    "stereotype_plausible": [],
}

# Load and process JSON files
for file_name in file_names:
    with open(f"../../data/to_verify/{file_name}", "r") as f:
        for line in f:
            statement_text = json.loads(line)
            axes, type_of_axes = (
                (file_name.split("_")[0], file_name.split("_")[2])
                if file_name.startswith("bias")
                else (file_name.split("_")[0], file_name.split("_")[1])
            )

            mapped_statements = {
                "axes": axes,
                "is_annotated": False,
                "statement": statement_text,
                "questions": {
                    "question": "Is the above statement valid?",
                    "options": ["Yes", "No"],
                },
                "type": type_of_axes,
            }

            key = f"{axes}_{type_of_axes}"
            if key in statements_dict:
                statements_dict[key].append(mapped_statements)
