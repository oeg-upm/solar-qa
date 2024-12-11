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

| Property | Mandatory? | Expected Value | Definition |
| :----- | :---- | :---- | :---- |
| **question_category** | Yes | String   | This item refers to what the query is about, five possible choices are given below |
| **query** | Yes | String | This item contains the prompt used for the llm generation |
| **generation** | Yes | Dictionary | This item contains the generation result from the llm model, formatted as question_category: answer in a dictionary, as given in the table below  |
| **evidence** | Yes | Dictionary | This item contains the evidence to support the RAG algorithm, which contains **pdf_refercence** and **similiarity_score** |
| **pdf_reference** | Yes | String | This item contains the original text extracted by the similarity model |
| **similiarity_score** | Yes | Float | This item contains the similarity score that are calcuated between quesry embedding and pdf_reference embedding, the calculation metric is the similarity metric. |

*generation format:*

Generation contains the result from llm's generation, the result only have one category of the item/items, with the corresponding expected value/values.
The choices for **individual category** and **expected value** are given below.

```json
"generation":{
    "individual category": "excepted value",
    ...
}
```

*Choices for question_category and expected value, as the choices for generation:*

| Category | Expected Value |Definition |
| :----- | :---- | :---- |
| **catalyst/co_catalyst** | The catalyst and co_catalyst used in the experiment |The query is about the catalyst condition  | 
| **light_source/lamp** | **light_source**: 'UV', 'Solar', 'UV-Vis', 'Monochromatic', 'Solar Simulator'<br>**lamp**: 'Fluorescent', 'Mercury', 'Halogen', 'Mercury-Xenon', 'LED', 'Tungsten', 'Xenon', 'Tungsten-Halide', 'Solar Simulator' | The query is about the light usage condition about the experiment | 
| **reaction_medium** | 'Liquid', 'Gas' | The query is about the reaction medium used in the experiment | 
| **reactor_type** | The query is about the type of the reactor used in the experiment | 'Slurry', 'Fixed-bed', 'Optical Fiber', 'Monolithic', 'Membrane', 'Fluidised-bed' | 
| **operation_mode** | 'Batch', 'Continuous', 'Batch/Continuous' | The query is about how the operation is conducted | 



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
        "pdf_reference": "of TiO 2 photocatalyst.The in situ IR experiments are still in progress to investigate the mechanism aspects of the catalyst.",
        "similarity_score": 0.4707722067832947
    },
    {
        "pdf_reference": "other hydrocarbons might have been generated, but in small quantities which is too low to be detected.Photocatalytic activity is presented by a product yield, e.g., lmol/(g catal.), and quantum efficiency (U Q ) that can be evaluated with Eq. ( 1) below 1.This calculation is based on methanol yield at 6 h of the reaction. The results of quantum efficiency calculation are displayed in Table 2.The formation of methanol was found to be much more effective on Cu 2 loaded TiO 2 catalyst.The highest methanol",
        "similarity_score": 0.49091827869415283
    },
    ...
]