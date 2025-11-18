from PIL import Image, ImageFile
from transformers import AutoImageProcessor, AutoModel
from time import perf_counter
import numpy as np
import torch
from pathlib import Path
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from tqdm import tqdm
from io import BytesIO
from chromadb.api.types import Embeddable
ImageFile.LOAD_TRUNCATED_IMAGES = True
import streamlit as st
from utils import get_logger
logger = get_logger(__name__)
from s3 import S3

class EfficientNetImageEmbedding(EmbeddingFunction[Embeddable]):
    def __init__(self, model_name: str = 'google/efficientnet-b7') -> None:
        super().__init__()
        self.model_name = model_name
        self.device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Processor: resize, convert to tensor [C,H,W] (channels × height × width),
        # normalize pixels, add batch dim [B,C,H,W]
        self.processor = AutoImageProcessor.from_pretrained(self.model_name)
        # Model: transform the tensor to embeddings or prediction
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
        
    def preprocess_image(self, img_path: Path):
        try:
            pil_img = Image.open(img_path).convert('L').convert('RGB')
            inputs = self.processor(images=pil_img, return_tensors='pt').to(self.device)
            return inputs
        except Exception as e:
            logger.error(f'Error while loading {img_path}: {e}.', exc_info=True)
    
    def compute_one_embedding(self, img_path: Path):
        tensor_dict = self.preprocess_image(img_path)
        if tensor_dict is not None:
            pixel_values = tensor_dict['pixel_values']
            with torch.no_grad():
                outputs = self.model(pixel_values=pixel_values)
            emb = outputs.pooler_output[0].cpu().numpy().tolist()  # vecteur numpy
            return emb
    
    def compute_embeddings(self, file_paths: list[Path], batch_size: int = 10):
        batch_embeddings = []
        
        for img_path in file_paths:
            emb = self.compute_one_embedding(img_path)
            batch_embeddings.append(emb)
            
            # Yield batch regularly
            if len(batch_embeddings) == batch_size:
                yield batch_embeddings
                batch_embeddings = []
        
        # At the end, yield last batch if < 10
        if batch_embeddings:
            yield batch_embeddings