from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
from tempfile import NamedTemporaryFile
import uvicorn
import shutil
import os

app = FastAPI(
    title='Firebase Auth',
    docs_url='/'
)

templates = Jinja2Templates(directory='templates')

class PATH(BaseModel):
    path: str

class DOWNLOAD_PATH(BaseModel):
    path: str

FILE_PATH = "/Users/jeeban_jyoti_patra/Desktop/DATA/paths.txt"

def create_zip_archive(folder_path: str):
    with NamedTemporaryFile(delete=False) as tmp_file:
        shutil.make_archive(tmp_file.name, 'zip', folder_path)
        return tmp_file.name + '.zip'
    
    

@app.get('/fetch-tree')
def Fetch_Tree():
    paths = {}
    try:
        paths["message"] = "paths fetched successfully"
        with open(FILE_PATH, 'r') as f:
            paths["paths"] = f.readlines()
        return paths
    except:
        paths["message"] = "error occured, paths could not be fetched"
        paths["paths"] = []
    return paths

@app.post('/fetch-path')
def Fetch_Path(PATH: PATH):
    paths = {}
    try:
        paths["message"] = "paths fetched successfully"
        paths["paths"] = os.listdir(PATH.path)
    except:
        paths["message"] = "error occured, paths could not be fetched"
        paths["paths"] = []
    return paths

@app.post('/download-file')
async def Download_File(DOWNLOAD_PATH: DOWNLOAD_PATH):
    return FileResponse(DOWNLOAD_PATH.path, filename=os.path.basename(DOWNLOAD_PATH.path))

@app.post('/download-folder')
async def Download_Folder(DOWNLOAD_PATH: DOWNLOAD_PATH):
    folder_path = DOWNLOAD_PATH.path

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"message": "folder not found"}
    
    zip_file_path = create_zip_archive(folder_path)
    return StreamingResponse(open(zip_file_path, "rb"), media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={Path(zip_file_path).name}"})

@app.get('/frontend', response_class=HTMLResponse)
def Serve_Site(request: Request):
    context = {"request": request, "files": "hello"}
    return templates.TemplateResponse('index.html', context)



if __name__ == '__main__':
    uvicorn.run('main:app', host="localhost", port=8000)