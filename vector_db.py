import os
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from config import *

def load_pdf(path) -> list:
    reader = PdfReader(path)
    documents = []
    for page_number, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        documents.append(Document(page_content=text, metadata={"source": path, "page number": page_number}))
    
    return documents
     

def main():
    if not os.path.exists(DATA_PATH):
        print(
            f"PDF nicht gefunden unter '{DATA_PATH}'. "
            f"Lade das IBJJF-Regelwerk herunter und lege es dort ab."
        )
    
    documents = load_pdf(DATA_PATH)
    
    print("Zerlege Text in Chunks")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents=documents)
    print(f"{len(chunks)} Chunks")
    
    embeddings = OllamaEmbeddings(model=EMBEDIING_MODEL)
    
    
    if os.path.exists(PERSIST_DIR):
        import shutil
        shutil.rmtree(PERSIST_DIR)
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )
    print(f"Fertig! Vektordatenbank gespeichert unter '{PERSIST_DIR}'")
    print(f"Anzahl gespeicherter Chunks: {vectorstore._collection.count()}")
 
 
if __name__ == "__main__":
    main()     