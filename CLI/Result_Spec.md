## CLI Result Specification

### Generation Model
This item contains the large lanugage model (llm) reference id. 

*Example:*

```json
"generation_model": "meta-llama/Llama-3.2-3B-Instruct"
```


### Similarity Model
This item contains the similarity model reference id (the model is used in RAG searching stage).

*Example:*

```json
"similarity_model": "Salesforce/SFR-Embedding-Mistral"
```


### Similarity Metric
This item contains the calculation metric used in the RAG searching stage

*Example:*

```json
"similarity_metric": "Cosine_Similarity"
```


### Result
This item contains all relevant generation results, which includes:
<!-- - **question_category**: This item refers to what the result is about, possible choice: [catalyst/co_catalyst, light_source/lamp, reaction_medium, reactor_type, operation_mode]
- **query**: This item contains the prompt used for the llm generation
- **generation**: This item contains the generation result from the llm model
- **evidence**: This item contains the evidence to support the RAG algorithm, which contains **pdf_refercence** and **similiarity_score**
    * **pdf_reference**: This item contains the original text extracted by the similarity model
    * **similiarity_score**: This item contains the similarity score that are calcuated between quesry embedding and pdf_reference embedding, the calculation metric is the similarity metric. -->

| Property | Excepected Value | Definition |
| :----- | :---- | :---- |
| **question_category** | String   | This item refers to what the query is about, five possible choices are given below |
| **query** | String | This item contains the prompt used for the llm generation |
| **generation** | Dictionary | This item contains the generation result from the llm model, formatted as question_category: answer in a dictionary, as given in the table below  |
| **evidence** | Dictionary | This item contains the evidence to support the RAG algorithm, which contains **pdf_refercence** and **similiarity_score** |
| **pdf_reference** | String | This item contains the original text extracted by the similarity model |
| **similiarity_score** | Float | This item contains the similarity score that are calcuated between quesry embedding and pdf_reference embedding, the calculation metric is the similarity metric. |

*generation format:*

The choices for **individual category** and **expected value** are given below, as the definition for each category.

```json
"generation":{
    "individual category": "excepted value"
}
```

*Choices for question_category and expected value, as the choices for generation:*

| Category | Definition | Excepected Value |
| :----- | :---- | :---- |
| **catalyst/co_catalyst** | The query is about the catalyst condition  | The catalyst and co_catalyst used in the experiment |
| **light_source/lamp** | The query is about the light usage condition about the experiment | **light_source**: 'UV', 'Solar', 'UV-Vis', 'Monochromatic', 'Solar Simulator'<br>**lamp**: 'Fluorescent', 'Mercury', 'Halogen', 'Mercury-Xenon', 'LED', 'Tungsten', 'Xenon', 'Tungsten-Halide', 'Solar Simulator' |
| **reaction_medium** | The query is about the reaction medium used in the experiment | 'Liquid', 'Gas' |
| **reactor_type** | The query is about the type of the reactor used in the experiment | 'Slurry', 'Fixed-bed', 'Optical Fiber', 'Monolithic', 'Membrane', 'Fluidised-bed' |
| **operation_mode** | The query is about how the operation is conducted | 'Batch', 'Continuous', 'Batch/Continuous' |



*Example:*
```json
"question_category": "catalyst/co_catalyst",
"query": "\nPlease find the name of the catalyst...",
"generation": {
    "catalyst": "TiO2",
    "co_catalyst": "Cu"
}
"evidence": [
    {
        "pdf reference": "of TiO 2 photocatalyst.The in situ IR experiments are still in progress to investigate the mechanism aspects of the catalyst.",
        "similarity score": 0.4707722067832947
    },
    {
        "pdf reference": "other hydrocarbons might have been generated, but in small quantities which is too low to be detected.Photocatalytic activity is presented by a product yield, e.g., lmol/(g catal.), and quantum efficiency (U Q ) that can be evaluated with Eq. ( 1) below 1.This calculation is based on methanol yield at 6 h of the reaction. The results of quantum efficiency calculation are displayed in Table 2.The formation of methanol was found to be much more effective on Cu 2 loaded TiO 2 catalyst.The highest methanol",
        "similarity score": 0.49091827869415283
    },
    ...
]