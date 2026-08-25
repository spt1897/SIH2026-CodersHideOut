from weasyprint import HTML
import os
import aiofiles
import io
from fastapi.responses import StreamingResponse , FileResponse
from jinja2 import Environment,FileSystemLoader

'''
This module is to generate pdfs (for example:pdfs to show a report/analytics etc.)
dynamically using dynamic data. It also provides functionalities to store it,
or send pdfs to client as attachment or inline.
'''

#generate dynamic pdfs
async def generate_pdf(template_path:str,dynamic_datas:dict ={}):
    if not os.path.exists(os.path.dirname(template_path)):
        return None

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(os.path.dirname(template_path))
    
    # 2. Render dynamic HTML string
    rendered_html = template.render(**dynamic_datas)

    pdf_data = HTML(string = rendered_html,base_url=".").write_pdf()
    return pdf_data



#saving pdf bytes to File Storage
async def save_pdf_bytes_to_storage(pdf_data:bytes,path:str):
    if not pdf_data:
        return False

    os.makedirs(path=os.path.dirname(path),exist_ok=True)

    async with aiofiles.open(path,"wb") as f:
        await f.write(pdf_data)

    return True

#sending pdf bytes to client
async def send_pdf(pdf_data:bytes,pdf_name:str,content_disposition_type:str):

    if not pdf_data:
        return
    
    pdf_data_stream = io.BytesIO(pdf_data)

    # Use 'inline' to preview in browser, or 'attachment' to force file download
    headers = {
        "Content-Disposition": f"{content_disposition_type}; filename={pdf_name}"
    }

    return StreamingResponse(
        pdf_data_stream,
        media_type="application/pdf",
        headers=headers
    )

#sending existing pdf file to client
async def send_pdf_from_storage(pdf_file_path:str,pdf_name:str,content_disposition_type:str):
    if not os.path.exists(os.path.dirname(pdf_file_path)):
        return

    return FileResponse(
        path=pdf_file_path,
        filename=pdf_name,
        media_type="application/pdf",
        content_disposition_type=f"{content_disposition_type}" 
    )



