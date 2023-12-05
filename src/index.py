from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, ValidationError, Field
import shutil
import os
from typing import List

from service import Service

app  =  FastAPI()

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

#upload de arquivos pdf
@app.post("/uploadfile/", status_code=201, response_model=ResponseUpload)
async def create_upload_file(file: UploadFile = File(...)):
    # Salvar o arquivo na pasta data com caminho absoluto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, '../document', file.filename)
    
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "msg" : "upload realizado com sucesso"}


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





