import streamlit as st
import pandas as pd
import numpy as np
import time
from utils import get_local_images_path, get_lorem
from pathlib import Path
from chroma_client import ChromaBase
import torch
import uuid
from pprint import pprint
import tempfile
from PIL import Image
import io
from io import BytesIO
from s3 import S3

@st.cache_resource
def initialize_chroma() -> ChromaBase:
    chroma_base = ChromaBase()
    return chroma_base

def main() -> None:
    # Build Streamlit base page
    st.set_page_config(page_title="Recherche inversée sur des images d'archive (v 0.2)")
    st.title("Recherche inversée sur des images d'archive")
    st.markdown("Cette application lancée par la M2RS permet d'effectuer une recherche inversée sur le fonds 209SUP (cartons 933 à 1044) du ministère de l'Europe et des Affaires étrangères (**23 391 photographies**).")
    with st.sidebar:
        st.subheader('Accueil')
    
    s3 = S3()
    chroma_base = initialize_chroma()
    
    uploaded_image = st.file_uploader(label="Merci de déposer une image :", type=["jpg"])
    
    if uploaded_image is not None:
        img_bytes = uploaded_image.getvalue()
        img_name = uploaded_image.name
        img_pil = Image.open(BytesIO(img_bytes)).convert("RGB")
        
        buffer = io.BytesIO()
        try:
            if '.jpg' in img_name:
                img_pil.save(buffer, format="JPEG")
                buffer.seek(0)   
            s3.upload_from_buffer_to_user(buffer, img_name)
        except:
            ...
        
        _, center, _ = st.columns((1,2,1))
        center.image(
            image=img_bytes,
            caption=uploaded_image.name,
            use_column_width=True
        )
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img_path = Path(tmp.name)
            img_pil.save(img_path)
        
        st.subheader('Images similaires :')

        start = time.perf_counter()
        results = chroma_base.query_image(img_path, n_results=21)
        end = time.perf_counter()
        print(f"Query time : {end - start:.6f} sec.")
        
        cols = st.columns(3)
        for i, metadata in enumerate(results['metadatas'][0]):
            file_path = metadata['path']
            file_name = metadata['name']
            
            img_bytes = s3.download_file(file_path)
            
            with cols[i % 3]:
                st.image(
                    image=img_bytes,
                    use_column_width=True,
                    caption=file_name
                    )

        st.subheader('Debug :')
        my_results = {}
        for metadata, distance in zip(dict(results)['metadatas'][0], dict(results)['distances'][0]):
            name = metadata['name']
            my_results[name] = distance

        st.write(dict(my_results))

if __name__ == '__main__':
    main()