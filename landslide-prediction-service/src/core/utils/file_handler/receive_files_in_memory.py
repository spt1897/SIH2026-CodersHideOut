from fastapi import UploadFile, File, Form, HTTPException, status, Depends
from fnmatch import fnmatch
import asyncio

'''This module functions receive receive a file/files from user to processs
via the formdata through http request , extracts the file bytes to memory and 
returns a reference to it in memory for the service to process it.
This is recommended for small sized temporary files for processing like images etc.
Also matches file type patterns, supports multi file upload
'''

#used inside the router functions
async def ReceiveFileInMemory(file:UploadFile, content_type_patterns:list[str],max_file_size):
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No File uploaded."
            )

        if max_file_size and getattr(file,"size",None) and file.size>max_file_size:
            filename = file.filename
            await file.close()
            raise HTTPException(
                                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                                detail=f"File: {filename} size limit exceeded."
                            )

        if not content_type_patterns:
            content_type_patterns=['*']

        if not file.content_type:
            file.content_type =""

        if not any(fnmatch(file.content_type.lower(),content_type_pattern.lower()) 
                   for content_type_pattern in content_type_patterns):
            filename = file.filename
            await file.close()
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Uploaded file: {filename} type is not supported."
            )
        
        try:
            file_content = await file.read()
            size = len(file_content)
            if max_file_size and size>max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"File: {file.filename} size limit exceeded."
                )

            return {
                "filename" :file.filename,
                "content_type": file.content_type.lower(),
                "size": size,
                "content" : file_content
            }

        finally:
            await file.close()


#called from inside router func
async def ReceiveFilesInMemory(files:list[UploadFile], content_type_patterns,max_file_size):
    if not files:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail = "No Files uploaded."
                )
    try:
        file_datas =await asyncio.gather(*(ReceiveFileInMemory(file,content_type_patterns,max_file_size)
                                                for file in files))
    except Exception as err:
        for file in files:
            if file:
                await file.close()
        raise err
        

    return file_datas

#used directly in depends
def ReceiveFileInMemory_D( content_type_patterns:list[str],max_file_size=None):
    async def receiver(file:UploadFile = File(...)):
        return await ReceiveFileInMemory(file=file,content_type_patterns=content_type_patterns,max_file_size=max_file_size)
    return receiver


#used directly in depends
def ReceiveFilesInMemory_D(content_type_patterns:list[str],max_file_size=None):
    async def receiver(files:list[UploadFile] = File(...)):
        return await ReceiveFilesInMemory(files=files,content_type_patterns=content_type_patterns,max_file_size=max_file_size)

    return receiver

