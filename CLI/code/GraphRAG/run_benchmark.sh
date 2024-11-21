# !/bin/bash

use_platform='False'
llm_id='Qwen/Qwen2.5-32B-Instruct'
input_file_path='/home/jovyan/grob/test.pdf'
prompt_file='/home/jovyan/GraphRAG/graphrag_prompt.json'
# context_file_path='/home/jovyan/UPM/Clark/GraphRAG/result/Qwen2.5-32B-Instruct/'
context_file_path='/home/jovyan/GraphRAG/result/test/'
graph_file_path='/home/jovyan/GraphRAG/result/test/'

# Define the target directory
directory="/home/jovyan/GraphRAG/paper_all"

# Check if the target is not a directory
if [ ! -d "$directory" ]; then
    exit 1
fi

# Loop through files in the target directory
for file in "$directory"/*; do
  if [ -f "$file" ]; then
      var=$(echo "$file" | cut -d "_" -f 3)
      ind=$(echo "$var" | cut -d "." -f 1)
      output_file="${context_file_path}result_${ind}.json"
      graph_file="${graph_file_path}graph_${ind}.gml"
      if [ -f "$output_file" ]; then
          echo "file exist"
      else
          python graphrag.py --use_platform "$use_platform" --llm_id "$llm_id" --input_file_path "$file" --prompt_file "$prompt_file" --context_file_path "$output_file" --graph_file_path "$graph_file"
          echo $output_file
    #   break
      fi
      # python graphrag.py --use_platform use_platform --llm_id llm_id --input_file_path "$file" 
  fi
echo "DONE"
done