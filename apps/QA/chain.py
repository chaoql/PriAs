import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # 导入环境


def format_docs(docs):
    """
    提取检索文档内容
    :param docs: docs
    :return:
    """
    return "\n\n".join(doc.page_content for doc in docs)


def load():
    """
    加载知识库
    """
    bs_strainer = bs4.SoupStrainer(class_=("post-content", "post-title", "post-header"))
    loader = WebBaseLoader(  # 使用  WebBaseLoader  来将  HTML  页面中的所有文本加载到文档格式中，以便我们可以使用下游。
        web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
        bs_kwargs={"parse_only": bs_strainer},  # 指定了在解析HTML或XML文档时应该仅考虑包含特定CSS类的标签。
    )
    docs = loader.load()
    return docs


def split(docs):
    """
    切割文本
    :return:
    """
    # Indexing: Split
    # chunk_size=1000指定了每个文本块的大小为1000个字符
    # chunk_overlap=200指定了文本块之间的重叠部分为200个字符。
    # add_start_index=True ，这样每个分裂的文档在初始文档中开始的字符索引就被保存为元数据属性“start_index”。
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
    splits = text_splitter.split_documents(docs)
    return splits


def store(splits):
    """
    向量数据库存储
    :return:
    """
    # 指定了使用OpenAI的嵌入模型来对文档进行嵌入（embedding）操作。通过这个步骤，文档数据将被转换为向量表示，以便进行后续的分析和处理。
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    return vectorstore


def chain(vectorstore, model_name, temperature):
    # Retrieve and generate using the relevant snippets of the blog.
    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")  # RAG提示模板
    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )
    return rag_chain
