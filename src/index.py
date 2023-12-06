from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError, Field
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from typing import List
import math
import fitz

from service import Service

app  =  FastAPI()

# Configuração do CORS
origins = [
    "https://*", 
    "http://*"
]  # Permitir CORS para qualquer origem

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    query: str = Field(..., title="Query", description="Query para busca de documentos")
    file_name : str = Field(..., title="Nome do arquivo", description="Nome do arquivo para busca de documentos")
    top_k : int
    model : str

class Response(BaseModel):
    document : list
    query : str

class ResponseUpload(BaseModel):
    filename : str
    msg : str
    # None or str
    size : None or str
    image_url :None or str 

class ResponseUploadImage(BaseModel):
    filename : str
    msg : str
    size : str              

class Document(BaseModel):
    content: str
    page: List[int]
    source: str

class TopResponse(BaseModel):
    document: Document
    similarity: float

class ReponseDocument(BaseModel):
    data: List[TopResponse]
    query: str     

class ResponseStatusCode(BaseModel):
    msg : str
    status_code : int

class ResponseUploadError(BaseModel):
    msg : str


app.mount("/images", StaticFiles(directory="../images"), name="images")

#upload de arquivos pdf
@app.post("/uploadfile/", status_code=201, response_model=ResponseUpload, responses={400 : {'model' : ResponseUploadError}})
async def create_upload_file(file: UploadFile = File(...)):
    
    # Verificar o tamanho do arquivo
    file_content = await file.read()

    if len(file_content) > 1000 * 1024:
        # tratar esse erro dentro do sistema
        raise HTTPException(status_code=400, detail="O tamanho do arquivo não pode ser maior que 500KB")
        
    # Salvar o arquivo na pasta data com caminho absoluto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, '../document', file.filename)

    #verificar se o arquivo existe
    if os.path.exists(file_path): 
        file_image_name = os.path.splitext(file.filename)[0]
        size = math.ceil(len(file_content) / 1000)
        return {"filename": file.filename, "msg" : "Upload feito com sucesso", "size" : f"{size}KB", "image_url" : f"/images/{file_image_name}.png"}  # Adicionamos o índice 0 ao nome do arquivo

    with open(file_path, 'wb') as buffer:
        buffer.write(file_content)
        
    doc = fitz.open(file_path)  
    
    image_url = None
    try:
        # Percorrer cada página e obter a primeira imagem
        for i in range(len(doc)):
            page = doc[i]
            pix = page.get_pixmap()
            base = os.path.splitext(file.filename)[0]

            # Ajustar o caminho para salvar as imagens
            images_dir = os.path.join(current_dir, '../images')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            image_path = os.path.join(images_dir, f"{base}.png")
            pix.save(image_path)
            image_url = f"/images/{base}.png"
            break    
    except Exception as e:
        print(f'Error ao gerar o arquivo {image_url}')
            
    # Calcular o tamanho do arquivo
    file_size = math.ceil(len(file_content) / 1000)

    if image_url is None:
        return {"filename": file.filename, "msg" : "upload realizado com sucesso", "size" : f"{file_size}KB", "image_url" : f"/images/gatinho.jpeg"}    

    return {"filename": file.filename, "msg" : "upload realizado com sucesso", "size" : f"{file_size}KB", "image_url" : image_url}
   

#retorno do status code
@app.get('/status/', status_code=200, response_model=ResponseStatusCode, responses={500 : {'model' : ResponseStatusCode}})
async def status(): 
    try:
        return {"msg" : "API em execução", "status_code": 200}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Servidor offline")  


#generate document response with metadata and content_text
@app.post("/answer/", status_code=200, response_model=ReponseDocument)
async def get_document(request : Query):
    try:
        service = Service()
        pdf_pages = await service.load_file_pdf(request.file_name)
        document_list = await service.read_pdf_file_and_split_document(pdf_pages, chunk_size=500)
        documents_response =  await service.most_similar(query=request.query, document_list=document_list, top_k=request.top_k, model=request.model)
        return {  "data" : documents_response, 'query' : request.query }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))    





