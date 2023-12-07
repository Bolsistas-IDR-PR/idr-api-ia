from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
import numpy as np
import os


class Service:

    # load file pdff  
    async def load_file_pdf(self, file_name : str):
        
        """ @params fiile_path: str 
            @return pages: list of str and dict
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # search a file path ../document
        # if document not exist create a new document path
        # TODO 
        file_path =  os.path.join(current_dir, '../document', f"{file_name}.pdf")
        loader = PyPDFLoader(file_path)
        pages =  loader.load_and_split()

        return pages 


    # split text file    
    async def split_text_to_document(self, content, metdata, chunk_size, chunk_overlap=0):

        """ @params text_file: str 
            @return texts: list of Document

            @TODO retornar uma lista de dicionario com o texto e o numero da pagina, todos os textos referente a pagina
        """
        # generate document list
        list_document = []
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        texts = text_splitter.split_text(content)
        for text in texts:
            document = Document(text, metdata['page'] + 1, metdata['source'])
            list_document.append(document)
        return list_document

    # read pdf file and split text
    async def read_pdf_file_and_split_document(self, pages, chunk_size = 500):

        """ 
            @params pages: list of str and dict
            returne list of Document
        """

        list_of_document = []
        for page in pages:
            texts = await self.split_text_to_document(page.page_content, page.metadata, chunk_size=chunk_size)
            list_of_document.extend(texts)
        return list_of_document
    
    # embeddings
    def embeddings(self, query, model):

        """
            @params query: str
            @return query_embedding: np.array
        """

        embeddings =  HuggingFaceEmbeddings(model_name=model)
        query_embedding =  embeddings.embed_query(query)
        return np.array(query_embedding)
    

    # cosine similarity
    def cosine_similarity(self, embedding1, embedding2):
        """
            Calcula a similaridade de cosseno entre dois vetores de embedding.

            :param embedding1: Primeiro vetor de embedding.
            :param embedding2: Segundo vetor de embedding.
            :return: Valor de similaridade de cosseno entre os dois vetores.
        """
            # Normalizar cada vetor para ter um comprimento de 1 (norma L2)
        embedding1_normalized = embedding1 / np.linalg.norm(embedding1)
        embedding2_normalized = embedding2 / np.linalg.norm(embedding2)

            # Calcular a similaridade de cosseno como o produto escalar dos vetores normalizados
        similarity = np.dot(embedding1_normalized, embedding2_normalized)

        return similarity
    

    


    async def most_similar(self, query, document_list : list, model="paraphrase-MiniLM-L6-v2", top_k = 5):

        """
            @params query: str
            @return: list[TopResponse]
        """
        list_of_document = []
        # embeddings da query 
        query_embedding = self.embeddings(query, model)

        # embeddings dos documentos        
        for document in document_list:
            document_embedding = self.embeddings(document.content, model) 
            most_similary =  self.cosine_similarity(embedding1=query_embedding,embedding2=document_embedding)
            resut  = most_similary * 100
            list_of_document.append(TopResponse(document, resut))
        list_of_document.sort(key=lambda x: x.similarity, reverse=True)
        # top k elementos dentro do list of document
        if top_k > len(list_of_document):
            return list_of_document
        return list_of_document[:top_k]
    




# classe document
class Document:
    def __init__(self, content, page, source):
        self.content = content
        self.page = page,
        self.source = source


    #crie um funcao que printe melhor essa classe
    def __repr__(self):
        return f"Document(content={self.content}, metadata={self.page}, source={self.source})"    


class TopResponse:
    def __init__(self, document, similarity):
        self.document = document
        self.similarity = similarity

    def __repr__(self):
        return f"TopResponse(document={self.document}, similarity={self.similarity})"    

if __name__ == '__main__': 
    service = Service()
    pages = service.load_file_pdf('test.pdf')


    document_list = service.read_pdf_file_and_split_document(pages, 100)
    lista_response = service.most_similar(
         "Na molécula de água a polaridade se dá porque o hidrogênio ateais para si os elétrons do oxigênio", document_list, top_k=1)
    print(lista_response)
   