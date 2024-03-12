from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.llms import QianfanLLMEndpoint
from langchain_ai21 import AI21Embeddings


def getLLM(model_name="百度千帆大模型", temperature=0):
    if model_name == "gpt-3.5-turbo":
        return ChatOpenAI(model_name=model_name, temperature=temperature)  # openai: gpt-3.5
    elif model_name == "百度千帆大模型":
        return QianfanLLMEndpoint(streaming=True)
