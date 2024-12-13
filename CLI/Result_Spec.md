# SolarRAG-CLI Result Specification

## Result Specification Table

Here is the table that describe the saved output json file:

| Category | Definition | DataType | Example |
| -------- | ------- | ------- | ------- |
| paper_title  | The title of the paper | String | Effect of silver doping on the TiO2 for photocatalytic reduction of CO2 |
| DOI | The DOI of the paper(extracted from the paper pdf file) | String | 10.1016/j.apcatb.2010.02.030 |
| generation_model | The ollama model id for llm generation | String | llama3.2:3b |
| similarity_model | The ollama model id for text embedding | String | nomic-embed-text |
| similarity_metric | The metric for calculating the similarity between embeddings  | String | Cosine_Similarity |
| rag_type | the type of rag pipeline, range=['fact', 'naive'] | String | fact |
| result | The list of generation result from the llm  | List | Details given velow |

The details for `result` part of the saved output json file:

| Category | Definition | DataType | Example | Range(if applicable) |
| -------- | ------- | ------- | ------- | ------- |
| question_category  | The category of the question for the llm | String | Light_source | [catalyst, co_catalyst, Light_source, Lamp, Reaction_medium, Reactor_type, Operation_mode] |
| query | The query for the llm | String | What is the Light_source used in the experiment? | Not applicable |
| generation | The generated answer from the llm | String | ###Light_source: UV | Not applicable |
| RAG_source | The information source provided for the RAG pipeline | String | generated_facts | Not applicable |
| selected_answer | The corresponding answer from the selection of choices | String | UV | Details are given below |
| evidences | The list of evidences for the RAG pipeline  | list | Details given below | Not applicable |

The range for `selected_answer` with correspongind `question_category`:
| question_category | Range(if applicable) |
| -------- | ------- |
| catalyst | Not applicable |
| co_catalyst | Not applicable |
| Light_source | 'UV', 'Solar', 'UV-Vis', 'Monochromatic', 'Solar Simulator', 'Do not Know' |
| Lamp | 'Fluorescent', 'Mercury', 'Halogen', 'Mercury-Xenon', 'LED', 'Tungsten', 'Xenon', 'Tungsten-Halide', 'Solar Simulator', 'Do not Know' |
| Reaction_medium | 'Liquid', 'Gas', 'Do not Know' |
| Reactor_type | 'Slurry', 'Fixed-bed', 'Optical Fiber', 'Monolithic', 'Membrane', 'Fluidised-bed', 'Do not Know' |
| Operation_mode | 'Batch', 'Continuous', 'Batch/Continuous', 'Do not Know' |

The details for `evidence` part of the `result` from the output json:

| Category | Definition | DataType | Example |
| -------- | ------- | ------- | ------- |
| similairty_score  | The similairty score between the query and correspond text provided to the embedding model | Float | 0.6205 |
| pdf_reference | The original text that are extracted from the paper | String | in the conventional focusing... |
| generated_fact | The generated facts based on the pdf_reference | String | Facts: 1. A homemade apparatus is used... |

> **_NOTE:_**  `generated_fact` only existed when the type of RAG pipeline is `fact` RAG.

## Example of the SolarRAG-CLI result

*Example:*
```json
    "paper_title": "Effect of silver doping on the TiO2 for photocatalytic reduction of CO2",
    "DOI": "10.1016/j.apcatb.2010.02.030",
    "generation_model": "llama3.2:3b",
    "similarity_model": "nomic-embed-text",
    "similarity_metric": "Cosine_Similarity",
    "rag_type": "fact",
    "result": [
        {
            "question_category": "catalyst",
            "query": "What is the chemical name of the catalyst used in the experiment",
            "generation": "###catalyst: Titanium dioxide (TiO2)",
            "RAG_source": "generated_facts",
            "selected_answer": {
                "catalyst": " Titanium dioxide (TiO2)"
            },
            "evidences": [
                {
                    "similairty_score": 0.6646425724029541,
                    "pdf_reference": "methods were described in our previous publication 39.It is important to minimize the influence of transport phenomena during kinetic measurements.The elimination of CO 2 diffusion from the bulk of gas through the gas-liquid interface in a laboratory batch slurry reactor was accomplished by saturating the liquid with pure CO 2 before the reaction had been started 4,11.Catalyst loading of 1 g dm -3 was chosen to avoid concentration gradients in the bulk of stirred liquid with TiO 2 suspension due to the scattering effect of light caused by the high TiO 2 concentration 11,16,40,41.The",
                    "generated_facts": "Facts:\n1. The methods described in publication 39 were used for kinetic measurements.\n2. Kinetic measurements should minimize influence.\n3. CO2 diffusion from the bulk of gas through the gas-liquid interface was accomplished by saturating the liquid with pure CO2.\n4. Saturating the liquid with pure CO2 resulted in a high concentration of TiO2 suspension due to scattering effects of light.\n5. The scattering effect of light caused concentration gradients in the reactor.\n6. Concentration gradients in the reactor were avoided by choosing an optimal catalyst loading.\n7. An optimal catalyst loading was used to eliminate CO2 diffusion from the bulk of gas.\n8. Eliminating CO2 diffusion from the bulk of gas resulted in a laboratory batch slurry reactor being used for reaction.\n9. A laboratory batch slurry reactor was used to accomplish elimination of CO2 diffusion.\n10. The elimination of CO2 diffusion was achieved by using a TiO2 suspension that scattered light."
                },
                ...
            ]
        }
    ]
```