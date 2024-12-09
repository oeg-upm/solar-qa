# Version Json CLI

import streamlit as st
import tempfile
import json
import os
from PyPDF2 import PdfReader
import time
import requests
import fitz
import io
import pandas as pd

# Función para inicializar claves en st.session_state
def initialize_votes_state(analysis_idx, paragraph_idx, voter_name):
    key_upvote = f"{voter_name}_votes_up_{analysis_idx}_{paragraph_idx}"
    key_downvote = f"{voter_name}_votes_down_{analysis_idx}_{paragraph_idx}"

    if key_upvote not in st.session_state:
        st.session_state[key_upvote] = False  # Cambiar a booleano para "Positive"
    if key_downvote not in st.session_state:
        st.session_state[key_downvote] = False  # Cambiar a booleano para "Negative"

    return key_upvote, key_downvote

# Transformar JSON
def transform_json(input_json):
    transformed_data = {
        "paper_title": input_json.get("paper_title", "Not available"),
        "DOI": input_json.get("DOI", "Not available"),
        "analysis": input_json.get("result", [])
    }
    return transformed_data

# Página principal
def json_page():
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 13, 1])
    with col2:
        st.image("/Users/alexandrafaje/Desktop/Solar/solar_chem/logo_pg.png", width=600)

    st.markdown("<h2 style='text-align: center;'>JSON INFORMATION</h2>", unsafe_allow_html=True)

    uploaded_json = st.file_uploader("Upload JSON file", type="json")

    if uploaded_json is not None:
        try:
            json_content = json.load(uploaded_json)
            transformed_json = transform_json(json_content)

            # Solicitar nombre del usuario
            st.markdown("### Please enter your name to continue:")
            voter_name = st.text_input("Enter your name:")

            if voter_name:
                st.success(f"Welcome, {voter_name}! You can now cast your votes.")

                # Información general del documento
                with st.expander("Paper Information"):
                    st.markdown(f"""
                        <h4 style='color:#333;'>TITLE:</h4>
                        <p style='font-size:16px; color:#555;'>{transformed_json['paper_title']}</p>
                        <h4 style='color:#333;'>DOI:</h4>
                        <p style='font-size:16px; color:#555;'>{transformed_json['DOI']}</p>
                        """, unsafe_allow_html=True)

                if "analysis" in transformed_json:
                    st.subheader("Analysis")
                    votes_data = []

                    for analysis_idx, analysis in enumerate(transformed_json["analysis"]):
                        # Mostrar información clave encima del expander
                        generation = analysis.get("generation", {})
                        info = " | ".join(
                            f"**{key.replace('_', ' ').capitalize()}**: {value.strip()}"
                            for key, value in generation.items()
                        )
                        st.markdown(info)

                        # Crear expander para detalles específicos de la categoría
                        with st.expander("View details"):
                            if "evidence" in analysis:
                                st.markdown("### Evidence and References")
                                for paragraph_idx, evidence in enumerate(analysis["evidence"]):
                                    pdf_reference = evidence.get("pdf_reference", "Not available")

                                    # Inicializar estado de votos para cada párrafo
                                    key_upvote, key_downvote = initialize_votes_state(analysis_idx, paragraph_idx, voter_name)

                                    st.markdown(f"#### Paragraph {paragraph_idx + 1}")
                                    st.markdown(f"- **PDF reference:** {pdf_reference}")

                                    # Botones de votación
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button("Positive", key=f"{voter_name}_button_up_{analysis_idx}_{paragraph_idx}"):
                                            st.session_state[key_upvote] = True  # Marcar como "Positive"
                                            st.session_state[key_downvote] = False  # Desmarcar "Negative"
                                    with col2:
                                        if st.button("Negative", key=f"{voter_name}_button_down_{analysis_idx}_{paragraph_idx}"):
                                            st.session_state[key_downvote] = True  # Marcar como "Negative"
                                            st.session_state[key_upvote] = False  # Desmarcar "Positive"

                                    # Mostrar el estado actual del voto
                                    if st.session_state[key_upvote]:
                                        st.markdown("✅ You voted **Positive** for this paragraph.")
                                    elif st.session_state[key_downvote]:
                                        st.markdown("❌ You voted **Negative** for this paragraph.")
                                    else:
                                        st.markdown("No vote recorded yet.")

                                    st.markdown("---")

                                    # Guardar los datos de votos
                                    votes_data.append({
                                        "Voter": voter_name,
                                        "Category": analysis.get("question_category", "Unknown"),
                                        "Paragraph": paragraph_idx + 1,
                                        "PDF reference": pdf_reference,
                                        "Positive Vote": st.session_state[key_upvote],
                                        "Negative Vote": st.session_state[key_downvote]
                                    })

                    # Botón para descargar el archivo CSV
                    st.markdown("### Download Your Votes")
                    if votes_data:
                        df = pd.DataFrame(votes_data)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"{voter_name}_votes.csv",
                            mime="text/csv"
                        )
            else:
                st.warning("Please enter your name to enable voting.")
        except Exception as e:
            st.error(f"Error loading JSON file: {e}")


            
    # Agregar espacio antes del pie de página
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)    

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center;'>
        <a href="https://github.com/oeg-upm/solar-qa" style="text-decoration: none;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" alt="GitHub Logo" width="18" style="vertical-align: middle;"/>
        https://github.com/oeg-upm/solar-qa
        </a> | CLI Version: 1 | © 2024 SolarChem
    </div>
    """, unsafe_allow_html=True)

    # Crear una columna para centrar la imagen
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    with col2:
        st.image("/Users/alexandrafaje/Desktop/Solar/solar_chem/logo_uni.png", width=150)
        

# Cargamos el JSON automaticamente
def load_json_automatically(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            query_data = json.load(f)
        #st.write("Archivo JSON cargado automáticamente.")
        return query_data
    else:
        st.error(f"JSON file not found in path: {json_path}")
        return None

# Pagina principal
def main_page():

    # Agregar espacio
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 13, 1])
    with col2:
        st.image("/Users/alexandrafaje/Desktop/Solar/solar_chem/logo_pg.png", width=600)

    #Mostrar imagen con logo pero sin columna
    #st.image("/Users/alexandrafaje/Desktop/Solar/solar_chem/logo_pg.png", width=600)

    # Agregar espacio
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

    # Cargar archivo JSON de configuración
    json_path = "prompts.json"  # Usa una ruta relativa
    query_data = load_json_automatically(json_path)

    # Cargar el archivo PDF
    uploaded_pdf = st.file_uploader("Upload your PDF file", type=["pdf", "json"])
    print(uploaded_pdf)
    
    doi = st.text_input('DOI (Optional):')

    # Verificar si se ha subido un archivo y si se ha presionado el botón Submit
    if uploaded_pdf is not None and st.button("Submit"):
        with st.spinner('Analyzing your paper... Please be patient'):
            try:
                # Crear un diccionario de argumentos
                args_dict = {
                    "use_platform": "True",
                    #"user_key": "",
                    "llm_id": "llama3-groq-8b-8192-tool-use-preview",
                    #"hf_key": "",
                    "llm_platform": "groq",
                    "sim_model_id": "Salesforce/SFR-Embedding-Mistral",
                    #"sim_model_id": "nomic-ai/nomic-embed-text-v1.5",
                    "input_file_path": uploaded_pdf.name,
                    "prompt_file_pdf": json_path,
                    "context_file_path": "context_result.json"
                }
                
                # Enviar solicitud al backend
                response = requests.post("http://127.0.0.1:8000/analysis/", json=args_dict)
                temp = response.json()
                #print(temp)
                #with open("temp.json", "wb") as f:
                #    json.dumps(temp)
                
                # Verificar si la respuesta fue exitosa
                if response.status_code == 200:
                    #generation_model = response.json()["generation_model"]
                    result = response.json()["result"]
                    context = response.json()["context"]
                    context["DOI"] = doi
                    generation_model = context["generation_model"]
                    #print(response.json())
                    #st.write("Backend response:", context)

                    # Mostrar Resultados Principales
                    if result:
                        st.subheader("Analysis - Main results")
                        st.write("Catalyst: " + str(result.get("catalyst", "Not available")))
                        st.write("Co_catalyst: " + str(result.get("co_catalyst", "Not available")))
                        st.write("Light_source: " + str(result.get("Light_source", "Not available")))
                        st.write("Lamp: " + str(result.get("Lamp", "Not available")))
                        st.write("Reaction_medium: " + str(result.get("Reaction_medium", "Not available")))
                        st.write("Reactor_type: " + str(result.get("Reactor_type", "Not available")))
                        st.write("Operation_mode: " + str(result.get("Operation_mode", "Not available")))

                        # Mostrar el modelo utilizado
                        #generation_model = response.json().get("generation_model", "Not available")
                        st.markdown(f"**Model used:** {generation_model}")

                    # Mostrar Evidencias Detalladas con el formato específico
                    st.subheader("Detailed evidence")
                    
                    evidencias = context.get("result", [])  # Lista de evidencias
                    
                    titulos = [
                        "Catalyst: Type " + str(result.get("catalyst", "Not available")) + 
                        " | Co_catalyst: Type " + str(result.get("co_catalyst", "Not available")),
                        "Light_source: Type " + str(result.get("Light_source", "Not available")) + 
                        " | Lamp: Type " + str(result.get("Lamp", "Not available")),
                        "Reaction_medium: Type " + str(result.get("Reaction_medium", "Not available")),
                        "Reactor_type: Type " + str(result.get("Reactor_type", "Not available")),
                        "Operation_mode: Type " + str(result.get("Operation_mode", "Not available"))
                    ]

                    for idx, evidence_entry in enumerate(evidencias):
                        if idx < len(titulos):
                            expander_title = titulos[idx]
                        else:
                            expander_title = "Evidencia {}".format(idx + 1)
                        
                        with st.expander(expander_title):
                            for e_idx, detalle in enumerate(evidence_entry.get("evidence", [])):
                                pdf_reference = detalle.get("pdf_reference", "Not available")
                                #similarity_score = detalle.get("similarity_score", "No disponible")
                                
                                st.markdown(f"**Paragraph {e_idx + 1}**")
                                #st.markdown(f"- **Puntuación de Similitud:** `{similarity_score}`")
                                st.markdown(f"- **PDF reference:** {pdf_reference}")
                                st.markdown("---")
                else:
                    st.error("Error processing PDF.")
                    st.write("Server response:", response.text)


   
                #json_string = json.dumps(temp)
                json_string = json.dumps(context)
                #st.json(json_string, expanded=True)
                st.download_button(
                    label = "Download: result.json",
                    data = json_string,
                    file_name = "result.json",
                    mime = "application/json"
                    )
                    
                    
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")

    # Agregar espacio antes del pie de página
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center;'>
        <a href="https://github.com/oeg-upm/solar-qa" style="text-decoration: none;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" alt="GitHub Logo" width="18" style="vertical-align: middle;"/>
        https://github.com/oeg-upm/solar-qa
        </a> | CLI Version: 1 | © 2024 SolarChem
    </div>
    """, unsafe_allow_html=True)

    # Crear una columna para centrar la imagen
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    with col2:
        st.image("/Users/alexandrafaje/Desktop/Solar/solar_chem/logo_uni.png", width=150)

# About page
def about_page():

    # Agregar espacio
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 13, 1])
    with col2:
        st.image("/Users/alexandrafaje/Desktop/Solar/solar_chem/logo_pg.png", width=600)
    
    #st.image("/Users/alexandrafaje/Desktop/Solar/solar_chem/logo_pg.png", width=600)

    
    st.markdown("<h2 style='text-align: center;'>ABOUT</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        """
        <div style="max-width: 800px; margin: 0 auto; padding: 50px 20px;">
            <p style="font-size: 1.2em; text-align: justify; line-height: 1.6;">
                Solarchem is an innovative platform designed to leverage artificial intelligence for the analysis of scientific papers in chemistry. 
                Our mission is to provide researchers, students, and professionals with an efficient way to extract key insights from academic documents 
                by automating the process of answering questions and highlighting relevant information.
            </p>
            <p style="font-size: 1.2em; text-align: justify; line-height: 1.6;">
                We use two advanced AI models based on Retrieval-Augmented Generation (RAG): a generation model and a similarity model. 
                These models process scientific PDFs, answering key questions about methodologies, findings, and more. 
                Each answer is linked to the specific paragraph in the document, ensuring accuracy and transparency. 
                Additionally, we provide a highlighted version of the PDF, marking relevant sections. Users can download this annotated PDF for future reference.
            </p>
            <h2 style="text-align: center; font-size: 2em; font-family: 'Arial', sans-serif; font-weight: bold;">How It Works</h2>
            <p style="font-size: 1.2em; text-align: justify; line-height: 1.6;">
                On our website, you first upload a PDF, which is processed using AI to generate key answers. 
                You will then receive evidence for these answers, with the option to download the PDF with the relevant sections highlighted or a JSON file containing the extracted data.
            </p>
            <p style="font-size: 1em; font-weight: bold;">
                Developed by: This website was carefully crafted by Alexandra Faje.
            </p>
            <p style="font-size: 1em; font-weight: bold;">
                Powered by: The platform is hosted and maintained by Clark Wang, Erick Cedeño, Ana Iglesias and Daniel Garijo, ensuring top-tier performance, security, and reliability.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown("---")

    st.markdown("""
    <div style='text-align: center;'>
        <a href="https://github.com/oeg-upm/solar-qa" style="text-decoration: none;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" alt="GitHub Logo" width="18" style="vertical-align: middle;"/>
        https://github.com/oeg-upm/solar-qa
        </a> | CLI Version: 1 | © 2024 SolarChem
    </div>
    """, unsafe_allow_html=True)

    # Crear una columna para centrar la imagen
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    with col2:
        st.image("/Users/alexandrafaje/Desktop/Solar/solar_chem/logo_uni.png", width=150)


# Función principal para gestionar las páginas
def main():
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    # Barra de navegación con botones en línea
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
    with col2:
        if st.button("Home", key="home_button"):
            st.session_state.page = "Home"
    with col3:
        if st.button("JSON", key="json_button"):
            st.session_state.page = "Json"
    with col4:
        if st.button("About", key="about_button"):
            st.session_state.page = "About"

    # Cargar la página seleccionada
    if st.session_state.page == "Home":
        main_page()
    elif st.session_state.page == "About":
        about_page()
    elif st.session_state.page == "Json":
        json_page()

if __name__ == "__main__":
    main()
    
