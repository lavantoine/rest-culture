import boto3
from boto3.s3.transfer import TransferConfig
from botocore.client import Config
from botocore.config import Config
from botocore.exceptions import ClientError  # <- ajout nécessaire
import streamlit as st
from pathlib import Path
from io import BytesIO
from utils import get_logger
logger = get_logger(__name__)
from PIL import Image
from pprint import pprint
from time import sleep
from tqdm import tqdm


class S3():
    def __init__(self) -> None:
        self.client = boto3.client(
            's3',
            aws_access_key_id=st.secrets['OVH']['ACCESS_KEY_ID'],
            aws_secret_access_key=st.secrets['OVH']['SECRET_ACCESS_KEY'],
            endpoint_url=st.secrets['OVH']['ENDPOINT'],
            config=Config(signature_version='s3v4')  # works well with OVH
        )
        self.bucket = 'images-mae'
        self.config = TransferConfig(
            max_concurrency=20,  # threads
            multipart_threshold= int(1024 * 1024 / 2),  # .5 Mo
            multipart_chunksize= int(1024 * 1024 / 2), 
        )
        
    def __str__(self) -> str:
        buckets = ', '.join(self.list_buckets())
        return f'{'-' * 50}\ns3 OVH with buckets: {buckets}\n{'-' * 50}\n'
    
    def upload_file_list(self, sources: list[Path], folder) -> None:
        existing_keys = set(self.iter_s3_keys(folder))
        # n = len(sources)
        # text = 'Vérification des photos, merci de patienter...'
        # bar = st.progress(0.0, text)
        
        for source_path in tqdm(sources):
            s3_path = Path(folder) / source_path.name
            if str(s3_path) not in existing_keys:
                self.upload_file(source_path, s3_path)
                tqdm.write(f'✅ {s3_path} uploaded.')
            else:
                tqdm.write(f'⏭️ {s3_path} already on bucket, skipping...')
                
        #     bar.progress(value=float((i+1)/n), text=f'{text} ({i}/{n})')
        # bar.empty()
    
    def upload_file(self, source_path: Path, s3_path: Path) -> None:
        try:
            self.client.upload_file(source_path, self.bucket, str(s3_path), Config=self.config)
        except Exception as e:
            logger.error(f'❌ Error while uploading file to \"{s3_path}\": {e}', exc_info=True)
    
    def download_file(self, file_path: Path) -> BytesIO:
        try:
            file_obj = BytesIO()
            self.client.download_fileobj(self.bucket, file_path, file_obj)
            file_obj.seek(0)
            logger.info(f'⬇️ {file_path} accessed')
            return file_obj
        except Exception as e:
            logger.error(f'❌ Error while retrieving file \"{file_path}\": {e}', exc_info=True)
            error_img_path = Path(__file__).parent / 'media/404.png'
            with Image.open(error_img_path) as img:
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                return buffer
    
    def file_exists(self, filename):
        try:
            self.client.head_object(Bucket=self.bucket, Key=filename)
            return True
        except ClientError as e:
                if e.response['Error']['Code'] == "404":
                    return False
                else:
                    raise
    
    def list_buckets(self) -> list[str]:
        return [bucket['Name'] for bucket in self.client.list_buckets()['Buckets']]
        
    def get_file_paths(self, folder) -> list[str]:
        paginator = self.client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=self.bucket, Prefix=folder)
        
        file_paths = []
        
        for page in page_iterator:
            if 'Contents' in page:
                file_paths.extend(obj['Key'] for obj in page['Contents'])
        return file_paths
    
    # def delete_folder(self, path: str) -> None:
    #     """
    #     Delete folder in OVH Bucket. If path is an empty string, the whole bucket will be erased.

    #     Args:
    #         path (str): String path of the folder to delete.
    #     """        
    #     if not path:
    #         logger.warning("WIPING ENTIRE BUCKET IN 10 SEC")
    #         sleep(10)
            
    #     paginator = self.client.get_paginator('list_objects_v2')
    #     for page in paginator.paginate(Bucket=self.bucket, Prefix=path):
    #         if 'Contents' in page:
    #             delete_batch = {
    #                 'Objects': [{'Key': obj['Key']} for obj in page['Contents']]
    #             }
    #             self.client.delete_objects(Bucket=self.bucket, Delete=delete_batch)
    #             batch_list = [o['Key'] for o in page['Contents']]
    #             print(f"Deletion batch from {batch_list[0]['Key']} to  {batch_list[-1]['Key']}.")
    
    def iter_s3_keys(self, prefix):
        # response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                yield obj['Key']
                
    def upload_from_buffer_to_user(self, buffer, file_name) -> None:
        self.client.upload_fileobj(
                buffer,
                self.bucket,
                f'user/{file_name}',
                ExtraArgs={"ContentType": "image/jpeg"}
        )