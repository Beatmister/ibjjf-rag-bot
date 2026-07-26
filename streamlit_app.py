import streamlit as st
import time
from config import *
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate



st.set_page_config(page_title="IBJJF Regelwerk-Bot", page_icon="🥋")
st.title("🥋 IBJJF Regelwerk-Bot")
st.caption("RAG-Chatbot über die offiziellen IBJJF-Wettkampfregeln")

prompt_template =  """ Du bist ein hilfreicher Assistent, der Fragen zum offiziellen IBJJ Regelwerk (Brazilian Jiu-Jitsu Wettkampfregeln) beantwortet.
Nutze AUSSCHLIESSLICH den folgenden Kontext aus dem Regelwerk, um die Frage zu beantworten. Wenn die Antwort nicht im Kontext steht, sage ehrlich, dass du das im Regelwerk nicht finden konntest. Erfinde keine Regeln!
Antworte auf Deutsch, auch wenn der KOntext auf Englisch ist.

Kontext: {context}

Frage: {input}

Antwort:
"""


@st.cache_resource
def build_chain():
        embeddings = OllamaEmbeddings(model=EMBEDIING_MODEL)
        vectorstore = Chroma(
                persist_directory=PERSIST_DIR,
                embedding_function=embeddings
        )
        
        if vectorstore._collection.count() == 0:
                return None

        retriever = vectorstore.as_retriever(search_kwargs={'k':TOP_K})
        llm = ChatOllama(model=LLM_MODEL, temperature=0.1)
        
        prompt = ChatPromptTemplate.from_template(prompt_template)

        combine_docs_chain = create_stuff_documents_chain(llm, prompt)

        return create_retrieval_chain(
            retriever,
            combine_docs_chain
        )

chain = build_chain()
    
if chain is None:
        st.error(f"Es wird keine Vectordatenbank gefunden '{PERSIST_DIR}'.")
        st.error(f"Führe zuerst das Program 'vector_db.py' aus.")
        st.stop()
else:
        if "success_message" not in st.session_state:
            tmp = st.empty()
            tmp.success("Der Bot wurde erfolgreich geladen. Du kannst nun Fragen stellen.")
            time.sleep(3)
            tmp.empty()
            st.session_state.success_message = True



if "messages" not in st.session_state:
        st.session_state.messages = []
 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
question = st.chat_input("Stelle deine Frage  zum IBJJF Regelwerk")

if question:
    st.session_state.messages.append({"role":"user", "content":question})
    with st.chat_message('user'):
        st.markdown(question)
        
    with st.chat_message('assistant'):
        with st.spinner("Durchsuche Regelwerk..."):
                result = chain.invoke({"input": question})
                answer = result["answer"]
                source = result["context"]

                st.markdown(answer)

                with st.expander("Regelwerk"):
                    for i, doc in enumerate(source, 1):
                        page = doc.metadata.get("page number", "?")
                        st.markdown(f"\n--- Quelle {i} (Seite {page}) ---")
                        st.write(doc.page_content[:450] + "...")

    st.session_state.messages.append({"role":"assistant", "content":answer})
