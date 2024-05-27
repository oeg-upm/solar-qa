# Result Specification

## Generation

#### Generation Result

- generated_item: Generation Result by the model
- ground_truth_item: The anotated result from the paper
- DOI: Reference of the paper

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

Model Info:
```
Model ID: meta-llama/Meta-Llama-3-70B-Instruct
Model URL: https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct
```

Result based on LLama-3-70B:

```
    "catalyst": " TiO2",
    "co_catalyst": " Ag",
    "Light_source": " UV",
    "Lamp": " Hg",
    "Reaction_medium": " Liquid",
    "Reactor_type": " Slurry",
    "Operation_mode": " Batch",
    "catalyst_ground": "TiO2",
    "co_catalyst_ground": "Ag",
    "Light_source_ground": "UV",
    "Lamp_ground": "Mercury",
    "Reactor_type_ground": "Slurry",
    "Reaction_medium_ground": "Liquid",
    "Operation_mode_ground": "Batch",
    "DOI": "10.1016/j.apcatb.2010.02.030"
```


## Evaluation
- The Avgerage accuarcy for each item, calculated according to `Evaluation Process` in `README`

