import os 
from config import *
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate



prompt_template = """ Du bist ein hilfreicher Assistent, der Fragen zum offiziellen IBJJ Regelwerk (Brazilian Jiu-Jitsu Wettkampfregeln) beantwortet.

Nutze AUSSCHLIESSLICH den folgenden Kontext aus dem Regelwerk, um die Frage zu beantworten. Wenn die Antwort nicht im Kontext steht, sage ehrlich, dass du das im Regelwerk nicht finden konntest. Erfinde keine Regeln!

Antworte auf Deutsch, auch wenn der KOntext auf Englisch ist.

Kontext: {context}

Frage: {input}

Antwort:
"""

def build_chain():
    if not os.path.exists(PERSIST_DIR):
        raise FileNotFoundError(
            f"Keine Vectordatenbank gefunden {PERSIST_DIR} \n"
            f"Bitte zuerst vector_db.py ausführen."
        )
    embeddings = OllamaEmbeddings(model=EMBEDIING_MODEL)
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings,
    )
    
    if vectorstore._collection.count() == 0:
        raise FileNotFoundError(
            f"Die Vektordatenbank '{PERSIST_DIR}' ist leer. \n"
            f"Bitte zuerst 'python vector.py' ausführen."
        )

    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    
    llm = ChatOllama(model=LLM_MODEL, temperature=0.1)
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(
        retriever,
        combine_docs_chain
    )
    
def main():
    print("Baue RAG-Chain auf...")
    chain = build_chain()    
    print("Fertig. Stelle deine Frage  zum IBJJF Regelwerk (Zum Beenden: 'q' oder 'exit'). \n") 
    
    while True:
        question = input("Du: ").strip()
        if question.lower() in ("q") or question.lower() in ("exit"):
            print("Bis bald")
            break
        if not question:
            continue
        
        result = chain.invoke({"input": question})
        answer = result["answer"]
        print(f"\nBot: {answer}\n")
        source = result["context"]

        show_sources = input("Quellen anzeigen? (j/n): ").strip().lower()
        
        if show_sources == "j":
            for i, doc in enumerate(source, 1):
                page = doc.metadata.get("page number", "?")
                print(f"\n--- Quelle {i} (Seite {page}) ---")
                print(doc.page_content[:450] + "...")
        elif show_sources == "q":
            print("Bis bald")
            break
        print()
        

if __name__ == "__main__":
    main()