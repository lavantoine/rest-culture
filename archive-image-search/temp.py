import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
# st.set_option('deprecation.showfileUploaderEncoding', False)

# Upload an image and set some options for demo purposes
st.header("Cropper Demo")
img_file = st.sidebar.file_uploader(label='Upload a file', type=['png', 'jpg'])

if img_file:
    img = Image.open(img_file)
    # Get a cropped image from the frontend
    cropped_img = st_cropper(img,
                             realtime_update=True,
                             box_color='#FF4B4B',
                             aspect_ratio=None)
    
    # Manipulate cropped image at will
    st.write("Preview")
    _ = cropped_img.thumbnail((250,250))
    st.image(cropped_img)