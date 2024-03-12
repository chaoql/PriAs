import os
from langchain_community.vectorstores import Chroma
from django.shortcuts import render
from django.views.generic.base import View
import apps.QA.RAG.chain as chain
from apps.QA.RAG.chain import contextualizeChain
from apps.QA.forms import questionForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.QA.RAG.vectorStore import createStore
from langchain_ai21 import AI21Embeddings
from apps.QA.RAG.load import load_web
from langchain_core.messages import AIMessage, HumanMessage
from apps.QA.RAG.llm import getLLM


@method_decorator(csrf_exempt, name="dispatch")
class FirstView(View):
    models = ["gpt-3.5-turbo", "百度千帆大模型"]
    dbs = os.listdir("D:\\MyPyCharm\\PrivateDocAssistant\\apps\\QA\\VectorStore")

    def get(self, request, *args, **kwargs):
        current_page = 'index'
        return render(request, "index.html", {"models": self.models, "model": "百度千帆大模型",
                                              "db": "Intial_db", "temperature": 0,
                                              "dbs": self.dbs, 'current_page': current_page})

    def post(self, request, *args, **kwargs):
        question_form = questionForm(request.POST)
        if question_form.is_valid():
            second_question = question_form.cleaned_data["question"]  # What are common ways of doing it?
            model = question_form.cleaned_data["model"]
            print("模型：" + model)
            db = question_form.cleaned_data["db"]
            temperature = question_form.cleaned_data["temperature"]
            docs = load_web(web_path="https://lilianweng.github.io/posts/2023-06-23-agent/")
            splits = chain.split(docs, chunk_size=1000, chunk_overlap=200)
            filenames = os.listdir("D:\\MyPyCharm\\PrivateDocAssistant\\apps\\QA\\VectorStore")
            if "Intial_db" not in filenames:  # 初始数据库
                createStore("Intial_db", splits)
                print("创建初始知识库：Intial_db")
            # ！ 程序启动时就应该创建初始知识库，并存入一个空文件
            persist_directory = "apps/QA/VectorStore/" + db
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=AI21Embeddings())
            rag_chain = chain.chain(vectorstore=vectorstore, model_name=model, temperature=temperature)
            contextualize_q_chain = contextualizeChain(llm=getLLM(model_name=model, temperature=temperature))

            chat_history = []
            question = "What is Task Decomposition?"
            ai_msg = rag_chain.invoke(
                {"question": question, "chat_history": chat_history, "contextualize_q_chain": contextualize_q_chain})
            chat_history.extend([HumanMessage(content=question), ai_msg])  # 首次执行没有历史记录，正常调用retriever->prompt->llm
            # 第二次执行存在历史记录，调用顺序为：
            # contextualize_q_prompt -> llm -> StrOutputParser -> retriever -> prompt -> llm
            # second_question = "What are common ways of doing it?"
            answer = rag_chain.invoke({"question": second_question, "chat_history": chat_history,
                                       "contextualize_q_chain": contextualize_q_chain})

            # answer = rag_chain.invoke(question)
            current_page = 'index'
            print("问题：" + question)  # What is Task Decomposition?
            print("模型：" + model)
            print("知识库：" + db)
            print("temperature：" + str(temperature))
            print("答案：" + answer)
            return render(request, "index.html", {"question": second_question, "message": str(answer),
                                                  "models": self.models, "model": model,
                                                  "db": db, "temperature": temperature,
                                                  "dbs": self.dbs,
                                                  'current_page': current_page})
        return render(request, "index.html")


class knowladgeManagementView(View):
    dbs = os.listdir("D:\\MyPyCharm\\PrivateDocAssistant\\apps\\QA\\VectorStore")

    def get(self, request, *args, **kwargs):
        current_page = "km"
        return render(request, "knowladgeManagementIndex.html",
                      {'current_page': current_page, 'dbs': self.dbs})

    def post(self, request, *args, **kwargs):
        pass
