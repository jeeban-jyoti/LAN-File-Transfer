from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
from tempfile import NamedTemporaryFile
import requests
import uvicorn
import socket
import shutil
import os

app = FastAPI(
    title='Firebase Auth',
    docs_url='/'
)
# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory='templates')

class PATH(BaseModel):
    path: str

FILE_PATH = "/Users/jeeban_jyoti_patra/Desktop/DATA/paths.txt"

# =============================== ADDITIONAL FUNCTIONS ================================
def create_zip_archive(folder_path: str):
    with NamedTemporaryFile(delete=False) as tmp_file:
        shutil.make_archive(tmp_file.name, 'zip', folder_path)
        return tmp_file.name + '.zip'
    
def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = '127.0.0.1'
    return ip

def get_file_from_ip(ip):
    ips = []
    data = {}
    paths = {}
    ip = ip.split('.')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.001)

    for j in range(256):

        try:
            print(ip[0] +'.'+ip[1]+'.'+ip[2]+'.'+str(j))
            s.connect((ip[0] +'.'+ip[1]+'.'+ip[2]+'.'+str(j), 8000))
            ips.append(ip[0] +'.'+ip[1]+'.'+ip[2]+'.'+str(j))
        except:
            continue
    
    print(ips)
    for i in ips:
        try:
            if i == getIP():
                with open(FILE_PATH, 'r') as f:
                    temp = f.read().split('\n')
                    data[i] = temp
                    for t in temp:
                        paths[t] = i
                continue
            api_url = "http://"+i+":8000/fetch-tree"
            response = requests.get(api_url, timeout=10)
            if response.json()["paths"] != ['']:
                data[i] = response.json()["paths"]
                temp = response.json()["paths"]
                for t in temp:
                    paths[t] = i
        except:
            continue
    print(paths)
    return data, paths

def get_file_from_name(name: str):
    ips = []
    data = {}
    paths = {}
    ip = getIP()
    ip = ip.split('.')
    for i in range(130,140):
        for j in range(256):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.001)
            try:
                print(ip[0] +'.'+ip[1]+'.'+str(i)+'.'+str(j))
                s.connect((ip[0] +'.'+ip[1]+'.'+str(i)+'.'+str(j), 8000))
                ips.append(ip[0] +'.'+ip[1]+'.'+str(i)+'.'+str(j))
            except:
                continue
    print(ips)
    for i in ips:
        try:
            if i == ip:
                with open(FILE_PATH, 'r') as f:
                    temp = f.read().split('\n')
                    data[i] = temp
                    for t in temp:
                        if name in t:
                            paths[t] = i
                continue
            api_url = "http://"+i+":8000/fetch-tree"
            response = requests.get(api_url, timeout=10)
            if response.json()["paths"] != ['']:
                data[i] = response.json()["paths"]
                temp = response.json()["paths"]
                for t in temp:
                    print(t)
                    if name in t:
                        paths[t] = i
        except:
            continue
    print(paths)
    return data, paths

def getLANFilessocket(ip = getIP()):
    data = {}
    paths = {}
    ips = []
    ip = ip.split('.')
    if ip == '127.0.0.1':
        return []
    for i in range(256):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.001)
        try:
            s.connect((ip[0] +'.'+ip[1]+'.'+ip[2]+'.'+str(i), 8000))
            ips.append(ip[0] +'.'+ip[1]+'.'+ip[2]+'.'+str(i))
        except:
            continue
    for i in ips:
        try:
            if i == getIP():
                with open(FILE_PATH, 'r') as f:
                    temp = f.read().split('\n')
                    data[i] = temp
                    for t in temp:
                        paths[t] = i
                continue
            api_url = "http://"+i+":8000/fetch-tree"
            response = requests.get(api_url, timeout=10)
            if response.json()["paths"] != ['']:
                data[i] = response.json()["paths"]
                temp = response.json()["paths"]
                for t in temp:
                    paths[t] = i
        except:
            continue
    print(paths)
    return data, paths

# =============================== API END POINTS ================================
@app.get('/fetch-tree')
async def Fetch_Tree():
    paths = {}
    try:
        paths["message"] = "paths fetched successfully"
        with open(FILE_PATH, 'r') as f:
            paths["paths"] = f.read().split('\n')
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
async def Send_File(path: PATH):
    print(path.path)
    if not os.path.exists(path.path):
        return {"message": "file not found"}
    print("file sent")
    return FileResponse(path.path, filename=os.path.basename(path.path))

@app.post('/download-folder')
async def Send_Folder(DOWNLOAD_PATH: PATH):
    
    folder_path = DOWNLOAD_PATH.path

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"message": "folder not found"}
    
    zip_file_path = create_zip_archive(folder_path)
    return StreamingResponse(open(zip_file_path, "rb"), media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={Path(zip_file_path).name}"})

@app.post('/download-path-ip/{ip}')
async def Get_resource_ip(ip: str, path: PATH):
    _, files = getLANFilessocket(ip)
    for i in files:
        if path.path == i:
            return {"name_found": True, "fileName": i, "ip": files[i]}
    return {"name_found": False, "fileName": None, "ip": None}



@app.get('/frontend', response_class=HTMLResponse)
def Serve_Site(request: Request):
    _, files = getLANFilessocket()
    ip = getIP().split('.')
    context = {"request": request, "files": files, "ip": ip[0] +'.'+ip[1]+'.'+ip[2]+'.0', "path": "/", "ips": files}
    return templates.TemplateResponse('index.html', context)


@app.get('/ip_decreament/{ip}')
def ip_decreament(ip: str, request: Request):
    i = ip.split('.')
    _, files = getLANFilessocket(i[0] +"."+i[1]+"."+str(int(i[2])-1)+"."+i[3])
    context = {"request": request, "files": files, "ip": i[0] +"."+i[1]+"."+str(int(i[2])-1)+".0", "path": "/", "ips": files}
    return templates.TemplateResponse('index.html', context)

@app.get('/ip_increament/{ip}')
def ip_increament(ip: str, request: Request):
    i = ip.split('.')
    _, files = getLANFilessocket(i[0] +"."+i[1]+"."+str(int(i[2])+1)+"."+i[3])
    context = {"request": request, "files": files, "ip": i[0] +"."+i[1]+"."+str(int(i[2])+1)+".0", "path": "/", "ips": files}
    return templates.TemplateResponse('index.html', context)

@app.get('/searchFile/{search_data}')
def SearchFile(search_data: str, request: Request):
    _, files = get_file_from_name(search_data)
    return files

@app.get('/searchIP/{search_data}')
def SearchIP(search_data: str, request: Request):
    _, files = get_file_from_ip(search_data)
    return files


if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000)