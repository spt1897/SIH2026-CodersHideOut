from fastapi import FastAPI, UploadFile, File,HTTPException, status
import aiofiles
import fnmatch


#in router function
async def ReceiveFileInStorage(file:UploadFile, content_type_patterns:list[str],chunk_size:int, file_path):
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No File uploaded."
            )

        if not content_type_patterns:
            content_type_patterns=['*']

        if not file.content_type:
            file.content_type =""

        if not any(fnmatch(file.content_type.lower(),content_type_pattern.lower()) 
                   for content_type_pattern in content_type_patterns):
            filename =file.filename
            await file.close()
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Uploaded file: {filename} type is not supported."
            )
        
        try:
            chunk_size = 1024*1024 if not chunk_size else chunk_size
            size =0 
            async with aiofiles.open(file_path, "wb") as out_file:
                while chunk := await file.read(chunk_size):
                    await out_file.write(chunk)
                    size += len(chunk)

            return {
                "filename" :file.filename,
                "content_type": file.content_type.lower(),
                "size": size,
                "filepath" : file_path
            }

        finally:
            await file.close()


#depends
def ReceiveFileInStorage_D(content_type_patterns:list[str],chunk_size:int,file_path:str):
    async def receiver(file:UploadFile = File(...)):
        return await ReceiveFileInStorage(file=file,content_type_patterns=content_type_patterns,chunk_size=chunk_size,file_path=file_path)

    return receiver