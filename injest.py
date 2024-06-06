from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import os
class Injest:
    suf = None
    DATA_PATH = "upload/"
    DB_FAISS_PATH = "vectorstores/db_faiss"

    def __init__(self):
        suf = None
        DATA_PATH = "upload/"
        DB_FAISS_PATH = "vectorstores/db_faiss"
    #Remove old files
    def clear_folder(self):
        print('clean folder...')
        if os.path.exists(self.DATA_PATH):
            for filename in os.listdir(self.DATA_PATH):
                file_path = os.path.join(self.DATA_PATH, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def load_documents(self):
        print("Here Load! from directory")
        loader = DirectoryLoader(self.DATA_PATH, glob = "*.pdf", loader_cls=PyPDFLoader)
        #apply loader to data
        data = loader.load()

        return data
    
    
    def split_text(self, data):
        print("Here Split! and splitting text data into smaller chunks")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 100)
        #apply text_splitter to data
        texts = text_splitter.split_documents(data)

        return texts
    
    def get_embeddings(self, text_splits):
        print("Here Embed!")
        embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})        # 
        return embeddings
    
    #at this stage we have the embeding of pdf so now want to save somewhere to query from it
    def save_embeddings(self, texts, embeddings):
        db = FAISS.from_documents(texts, embeddings)
        db.save_local(self.DB_FAISS_PATH)


