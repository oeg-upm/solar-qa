# !/bin/bash

llm_id='llama3.2:3b'
embedding_id='nomic-embed-text'
prompt_file='/home/jovyan/GraphRAG/self_developed/prompt.json'

# Define the target directory
input_directory="/home/jovyan/GraphRAG/self_developed/10_bench"
output_directory="/home/jovyan/GraphRAG/self_developed/context/"


if [ ! -d "$input_directory" ]; then
    exit 1
fi

for file in "$input_directory"/*; do
  if [ -f "$file" ]; then
      var=$(echo "$file" | cut -d "_" -f 4)
      ind=$(echo "$var" | cut -d "." -f 1)
      output_file="${output_directory}result_${ind}.json"
      if [ -f "$output_file" ]; then
          echo "file exist"
      else
          python FactsRAG.py --llm_id "$llm_id" --embedding_id "$embedding_id" --input_file_path "$file" --prompt_file "$prompt_file" --context_file_path "$output_file" 
          echo $output_file
      fi
  fi
echo "DONE"
done