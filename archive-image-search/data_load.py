from pathlib import Path
from s3 import S3
from tqdm import tqdm
import shutil
from chroma_client import ChromaBase

def load_to_s3(root):
    ...

def encode_to_chroma(root):
    pass

def synchronise():
    # if load_to_s3() == 'updated'
    ...

recto_tree = Path.home() / 'code/m2rs/data/mae/recto_tree'
recto = Path.home() / 'code/m2rs/data/mae/recto'
one_img = Path.home() / 'code/m2rs/data/dummy/clair-obscur.jpg'

# s3 = S3()
# s3.upload_file_list([one_img], 'dummy')

# total = 0
# for _ in s3.iter_s3_keys(''):
#     total += 1



# s3.upload_file_list(source_files, 'recto')

# print(f'Total files: {len(source_files)}')

# for source_path in tqdm(source_files):
#     dest_path = recto_dest / source_path.name
#     shutil.move(source_path, recto_dest)
#     tqdm.write(f'Ok: from {source_path} to {dest_path}')

# for obj in recto_tree.rglob('*'):
#     if obj.is_file():
#         print(obj)

jpgs = [source_path for source_path in recto.rglob('*.jpg')]
tifs = [source_path for source_path in recto.rglob('*.tif')]
source_files = jpgs + tifs

# 1. Ensure S3 is synchronized with local
# 2. Encode img from local
chroma_base = ChromaBase()
chroma_base.add_to_collection(source_files, 'recto')