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
            question = question_form.cleaned_data["question"]  # What are common ways of doing it?
            model = question_form.cleaned_data["model"]
            db = question_form.cleaned_data["db"]
            temperature = question_form.cleaned_data["temperature"]
            filenames = os.listdir(os.getenv("persist_directory"))
            if "Intial_db" not in filenames:  # 初始数据库
                docs = load_web(web_path="https://lilianweng.github.io/posts/2023-06-23-agent/")
                splits = chain.split(docs, chunk_size=1000, chunk_overlap=200)
                createStore("Intial_db", splits)
                print("创建初始知识库：Intial_db")
            # ！ 程序启动时就应该创建初始知识库，并存入一个空文件
            persist_directory = "apps/QA/VectorStore/" + db
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=AI21Embeddings())  # 加载向量数据库
            with_message_history = chain.chain(vectorstore=vectorstore, model_name=model, temperature=temperature)

            session_id = "test_9"  # 考虑如何对聊天记录编号？？？？
            answer = with_message_history.invoke(
                {"input": question},
                config={"configurable": {"session_id": session_id}},
            )
            # 测试：（下述问题仅能通过RAG得到的答案回答，用于测试RAG是否成功；第二个问题用于测试问题一的聊天记录是否已被大模型考虑在内）
            # What is Task Decomposition?
            # What are common ways of doing it?

            current_page = 'index'
            print("问题：" + question)  # What is Task Decomposition?
            print("模型：" + model)
            print("知识库：" + db)
            print("temperature：" + str(temperature))
            print("答案：" + answer)
            return render(request, "index.html", {"question": question, "message": str(answer),
                                                  "models": self.models, "model": model,
                                                  "db": db, "temperature": temperature,
                                                  "dbs": self.dbs, 'current_page': current_page})
        return render(request, "index.html")


class knowladgeManagementView(View):
    dbs = os.listdir("D:\\MyPyCharm\\PrivateDocAssistant\\apps\\QA\\VectorStore")

    def get(self, request, *args, **kwargs):
        current_page = "km"
        return render(request, "knowladgeManagementIndex.html",
                      {'current_page': current_page, 'dbs': self.dbs})

    def post(self, request, *args, **kwargs):
        pass
