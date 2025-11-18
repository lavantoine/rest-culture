import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings, QueryResult
from embeddings import EfficientNetImageEmbedding
import hashlib
from pathlib import Path
from pprint import pprint
from utils import get_logger
logger = get_logger(__name__)

class ChromaBase():
    def __init__(self) -> None:
        self.embedding_fn = EfficientNetImageEmbedding()
        self.chroma_client = chromadb.PersistentClient(path=Path(__file__).parent / '.local')
        self.collection = self.chroma_client.get_or_create_collection(
            name='my_collection',
            embedding_function=self.embedding_fn
        )
    
    def generate_id(self, file_path: Path) -> str:
        file_name = file_path.name
        id = hashlib.md5(data=file_name.encode("utf-8")).hexdigest()
        return id
    
    def keep_new_only(self, file_paths: list[Path]):
        """
        Check if file is already encoded in ChromaBD.

        Args:
            file_paths (list[Path]): List of source Path. Only the file name will be used.

        Returns:
            tuple[list[str], list[Path]]: Ids and paths of the files to be encoded.
        """        
        existing_ids = set(self.collection.get()["ids"])
        candidate_ids = [self.generate_id(file_path) for file_path in file_paths]

        new_ids = []
        new_file_paths = []
        for candidate_id, file_path in zip(candidate_ids, file_paths):
            if candidate_id not in existing_ids:
                new_ids.append(candidate_id)
                new_file_paths.append(file_path)
        logger.info(f'{len(new_ids)}/{len(file_paths)} new files.')
        return new_ids, new_file_paths
    
    def add_to_collection(self, file_paths: list[Path], prefix: str) -> None:
        ids, file_paths = self.keep_new_only(file_paths)
        metadatas = [{"path": f'{prefix}/{file_path.name}', "name": file_path.name} for file_path in file_paths]

        if ids and file_paths:
            for i, batch_embeddings in enumerate(self.embedding_fn.compute_embeddings(file_paths)):
                start = i * 10
                end = start + len(batch_embeddings)
                
                batch_ids = ids[start:end]
                batch_metadatas = metadatas[start:end]
                batch_names = [metadata['name'] for metadata in batch_metadatas]
                
                self.collection.upsert(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    metadatas=batch_metadatas
                )
                logger.info(msg=f"{', '.join(batch_names)} embeddings added to collection.")

    def query_image(self, img_path: Path, n_results: int, include: list = ["distances", 'metadatas']) -> QueryResult:
        return self.collection.query(
            query_embeddings=self.embedding_fn.compute_one_embedding(img_path),
            n_results=n_results,
            include=include
            ) # type: ignore