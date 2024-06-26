import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader


def load(path):  # 完善加载函数
    if path[0:7] == "http://" or path[0:8] == "https://":
        # print(path)
        return load_web(path)
    else:
        kind = str.split(path, '.')[-1]
        if kind == "md":
            return load_markdown(path)
        elif kind == "...":
            pass


def load_web(web_path):
    bs_strainer = bs4.SoupStrainer(class_=("post-content", "post-title", "post-header"))
    loader = WebBaseLoader(  # 使用  WebBaseLoader  来将  HTML  页面中的所有文本加载到文档格式中，以便我们可以使用下游。
        web_paths=(web_path,),
        bs_kwargs={"parse_only": bs_strainer},  # 指定了在解析HTML或XML文档时应该仅考虑包含特定CSS类的标签。
    )
    documents = loader.load()
    return documents


def load_markdown(markdown_path):
    loader = UnstructuredMarkdownLoader(markdown_path)
    # import nltk
    # nltk.download()
    data = loader.load()
    return data
