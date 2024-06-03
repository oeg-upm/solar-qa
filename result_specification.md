# Result Specification

## Generation

#### Generation Result

The Generation Result is dedicated in the file `Generation.json`. File contains:

- model_id: the reference id for the generative model
- prompt_template: the template for the prompt for generate the result
- result:

    - reference_index: paper index given in the dataset
    - DOI: DOI reference for the paper
    - generation: generated result

#### Ground Truth

The Ground Truth is dedicated in the file `Ground_Truth.json`. File contains:

- reference_index: paper index given in the dataset
- DOI: DOI reference for the paper
- ground_truth: annotated result

#### Generation Range
The Generation range for each item is given below:

```
    "Light_source": ["UV", "Solar", "UV-Vis", "Monochromatic", "Solar Simulator"],
    "Lamp" : ["Fluorescent", "Mercury", "Halogen", "Mercury-Xenon", "LED", "Tungsten", "Xenon", "Tungsten-Halide", "Solar Simulator"],
    "Reactor_type": ["Slurry", "Fixed-bed", "Optical Fiber", "Monolithic", "Membrane", "Fluidised-bed"],
    "Reaction_medium": ["Liquid", "Gas"],
    "Operation_mode" : ["Batch", "Continuous", "Batch/Continuous"]
```

#### Generation Example
Result based on LLama-3-70B:

```
generation:
{
    "catalyst": " TiO2",
    "co_catalyst": " Ag",
    "light_source": " UV",
    "lamp": " Hg",
    "reaction_medium": " Liquid",
    "reactor_type": " Slurry",
    "operation_mode": " Batch"
}
```


## Evaluation
The Average accuarcy for each item, calculated according to `Evaluation Process` in `README`.
The evaluation result is dedicated in `Evaluation.json`. File contains:

- generation_model_id: id reference for the generation model
- similarity_model_id: id refernce for the similarity model
- source_ground_truth: path for the file that contains the ground_truth
- source_generation: path for the file that contains the generation result
- evaluation_strategy: the evaluation strategy we adopt, detailed in `Evaluation Process` in `README`
- metric: the evaluation metric
- result:

    - item: the targeted item
    - value: evaluation numerical value based on the evalution metric   

#### Evaluation Example
Result based on LLama-3-70B:

```
evaluation:
{
    "generation_model_id": "meta-llama/Meta-Llama-3-70B-Instruct",
    "similarity_model_id": "Salesforce/SFR-Embedding-Mistral",
    "source_ground_truth": "/Solar/result/LLama_3_70B/Ground_Truth.json",
    "source_generation": "/Solar/result/LLama_3_70B/Generation.json",
    "evaluation_strategy": "rule-based",
    "metric": "accuracy",
    "result": [
        {"item": "catalyst",
        "acc": 0.8275862068965517},
        ...
        ]
}
```


## Context

The context or chunks that RAG system has selected to provide the context for the generative model.
The context is dedicated in `Context.json`. File contains:

- similarity_model_id: id refernce for the similarity model
- similarity_method: the method of calculating similarity
- context:

    - reference_index: paper index given in the dataset
    - contexts:

        - item: targeted item
        - context: a list of all the selected chunks from the original paper


```
context:
{
    "similarity_model_id": "Salesforce/SFR-Embedding-Mistral",
    "similarity_method": "Cosine_Similarity",
    "context": [
        {"reference_index": "1",
        "context": {
            "item": ["Operation_mode"],
            "chunk": ["XXXXX", "XXXXX"]
        }},
        ...
        ]
}
```



