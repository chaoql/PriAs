import os
from langchain import hub
from apps.QA.RAG.prompt import contextualizePrompt, qaPrompt
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv, find_dotenv
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_core.messages import AIMessage, HumanMessage
from apps.QA.RAG.llm import getLLM
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

_ = load_dotenv(find_dotenv())  # 导入环境


def format_docs(docs):
    """
    提取检索文档内容
    :param docs: docs
    :return:
    """
    return "\n\n".join(doc.page_content for doc in docs)


def split(docs, chunk_size=1000, chunk_overlap=200):
    """
    切割文本
    :return:
    """
    # chunk_size=1000指定了每个文本块的大小为1000个字符
    # chunk_overlap=200指定了文本块之间的重叠部分为200个字符。
    # add_start_index=True ，这样每个分裂的文档在初始文档中开始的字符索引就被保存为元数据属性“start_index”。
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                                                   add_start_index=True)
    splits = text_splitter.split_documents(docs)
    return splits


def store(splits, embeddings_name):
    """
    向量数据库存储
    :return:
    """
    # 指定了使用OpenAI的嵌入模型来对文档进行嵌入（embedding）操作。通过这个步骤，文档数据将被转换为向量表示，以便进行后续的分析和处理。
    # embeddings = AI21Embeddings()
    embeddings = QianfanEmbeddingsEndpoint()
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    return vectorstore


def contextualizeChain(llm):
    contextualize_q_prompt = contextualizePrompt()
    contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()  # 对问题进行背景说明的链
    return contextualize_q_chain


def get_message_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(session_id, url=os.getenv("REDIS_URL"))


def chain(vectorstore, model_name, temperature):
    retriever = vectorstore.as_retriever()
    llm = getLLM(model_name, temperature)
    contextualize_q_chain = contextualizeChain(llm)
    qa_prompt = qaPrompt()
    rag_chain = (
            RunnablePassthrough.assign(
                context=contextualize_q_chain | retriever | format_docs
            )
            | qa_prompt
            | llm
            | StrOutputParser()
    )
    with_message_history = RunnableWithMessageHistory(
        rag_chain,
        get_message_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    return with_message_history
