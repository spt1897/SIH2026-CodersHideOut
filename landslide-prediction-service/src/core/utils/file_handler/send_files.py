import os
import io
from fastapi.responses import StreamingResponse , FileResponse
import mimetypes

#sending file bytes to client
async def send_filebytes(file_data:bytes,file_name:str,file_type:str,content_disposition_type:str):

    if not file_data:
        return
    
    file_data_stream = io.BytesIO(file_data)

    # Use 'inline' to preview in browser, or 'attachment' to force file download
    headers = {
        'Content-Disposition': f"{content_disposition_type} ; filename={file_name}"
    }

    return StreamingResponse(
        file_data_stream,
        media_type=file_type,
        headers=headers
    )

#sending existing file to client
async def send_file_from_storage(file_path:str,file_name:str,content_disposition_type:str):
    if not os.path.exists(os.path.dirname(file_path)):
        return

    content_type, encoding = mimetypes.guess_type(file_path)
    if content_type is None or encoding is not None:
        content_type = "application/octet-stream"


    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type=content_type,
        content_disposition_type=content_disposition_type
    )
