import os
from langchain_ai21 import AI21Embeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import RedisChatMessageHistory

def createStore(Kname, texts):
    """
    创建新知识库
    :return:
    """
    filenames = os.listdir(os.getenv("persist_directory"))
    if Kname in filenames:
        return False
    persist_directory = "apps/QA/VectorStore/" + Kname
    embeddings = AI21Embeddings()
    vectordb = Chroma.from_documents(documents=texts, embedding=embeddings, persist_directory=persist_directory)
    vectordb.persist()
    return True
