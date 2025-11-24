import streamlit as st
# import pandas as pd
# import numpy as np
import time
# from utils import get_local_images_path, get_lorem
from pathlib import Path
from chroma_client import ChromaBase
# import torch
# import uuid
from pprint import pprint
import tempfile
from PIL import Image
import io
from io import BytesIO
from s3 import S3

@st.cache_resource(show_spinner=False)
def initialize_chroma() -> ChromaBase:
    chroma_base = ChromaBase()
    return chroma_base

@st.cache_resource(show_spinner=False)
def initialize_s3():
    s3 = S3()
    return s3

def show_home_md():
    md_path = Path(__file__).parent.parent / "md" / "home.md"
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    st.markdown(''.join(lines))

def main() -> None:
    with st.spinner('Chargement, merci de patienter...'):
        s3 = initialize_s3()
        chroma_base = initialize_chroma()
        show_home_md()
    
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
            st.toast(f"{img_name} sauvegardée.", icon=':material/save:')
        except:
            ...
        
        _, center, _ = st.columns((1,2,1))
        center.image(
            image=img_bytes,
            caption=uploaded_image.name,
            width='stretch'
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
        for i, (metadata, distance) in enumerate(zip(results['metadatas'][0], (results)['distances'][0])):
            file_path = metadata['path']
            file_name = metadata['name']
            caption = f'{file_name} (score : {distance:.2f})'
            
            img_bytes = s3.download_file(file_path)
            
            with cols[i % 3]:
                st.image(
                    image=img_bytes,
                    width='stretch',
                    caption=caption
                    )

if __name__ == '__main__':
    main()