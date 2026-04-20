import zipfile
import os
from io import BytesIO

def create_zip(file_paths):
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in file_paths:
            zipf.write(path, arcname=os.path.basename(path))

    zip_buffer.seek(0)
    return zip_buffer