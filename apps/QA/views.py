import os
from langchain_community.vectorstores import Chroma
from django.shortcuts import render
from django.views.generic.base import View
import apps.QA.RAG.chain as chain
from apps.QA.forms import questionForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.QA.RAG.vectorStore import createStore
from langchain_ai21 import AI21Embeddings

@method_decorator(csrf_exempt, name="dispatch")
class FirstView(View):
    def get(self, request, *args, **kwargs):
        current_page = 'index'
        return render(request, "index.html", {"models": ["gpt-3.5-turbo"], "model": "gpt-3.5-turbo",
                                              "function": "LLM问答", "temperature": 0,
                                              "functions": ["LLM问答", "结合知识库问答"], 'current_page': current_page})

    def post(self, request, *args, **kwargs):
        question_form = questionForm(request.POST)
        if question_form.is_valid():
            question = question_form.cleaned_data["question"]
            model = question_form.cleaned_data["model"]
            function = question_form.cleaned_data["function"]
            function_text = ""
            if function == 1:
                function_text = "LLM问答"
            else:
                function_text = "结合知识库问答"
            temperature = question_form.cleaned_data["temperature"]
            docs = chain.load_web(web_path="https://lilianweng.github.io/posts/2023-06-23-agent/")
            splits = chain.split(docs, chunk_size=1000, chunk_overlap=200)
            filenames = os.listdir("D:\\MyPyCharm\\PrivateDocAssistant\\apps\\QA\\VectorStore")
            if "Intial_db" not in filenames:  # 初始数据库
                createStore("Intial_db", splits)
                print(1)
            vectorstore = Chroma(persist_directory="Intial_db", embedding_function=AI21Embeddings())
            rag_chain = chain.chain(vectorstore=vectorstore, model_name=model, temperature=temperature)
            message = rag_chain.invoke(question)
            current_page = 'index'
            print(question)
            print(model)
            print(function_text)
            return render(request, "index.html", {"question": question, "message": str(message),
                                                  "models": ["gpt-3.5-turbo"], "model": model,
                                                  "function": function_text, "temperature": temperature,
                                                  "functions": ["LLM问答", "结合知识库问答"],
                                                  'current_page': current_page})
        return render(request, "index.html")


class knowladgeManagementView(View):
    def get(self, request, *args, **kwargs):
        current_page = "km"
        return render(request, "knowladgeManagementIndex.html", {'current_page': current_page})

    def post(self, request, *args, **kwargs):
        pass
