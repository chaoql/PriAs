import os
from langchain_community.vectorstores import Chroma
from django.shortcuts import render
from django.views.generic.base import View
import apps.QA.RAG.chain as chain
from apps.QA.forms import questionForm, dbForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.QA.RAG.vectorStore import createStore
from langchain_ai21 import AI21Embeddings
from apps.QA.RAG.load import load
import apps.utils as utils


@method_decorator(csrf_exempt, name="dispatch")
class FirstView(View):
    models = ["gpt-3.5-turbo", "百度千帆大模型"]

    def get(self, request, *args, **kwargs):
        dbs = os.listdir(os.getenv("persist_directory"))
        current_page = 'index'
        return render(request, "index.html", {"models": self.models, "model": "百度千帆大模型",
                                              "db": "Intial_db", "temperature": 0,
                                              "dbs": dbs, 'current_page': current_page})

    def post(self, request, *args, **kwargs):
        question_form = questionForm(request.POST)
        dbs = os.listdir(os.getenv("persist_directory"))
        if question_form.is_valid():
            question = question_form.cleaned_data["question"]  # What are common ways of doing it?
            model = question_form.cleaned_data["model"]
            db = question_form.cleaned_data["db"]
            temperature = question_form.cleaned_data["temperature"]
            filenames = os.listdir(os.getenv("persist_directory"))
            if "Intial_db" not in filenames:  # 初始数据库
                # docs = load(path="https://lilianweng.github.io/posts/2023-06-23-agent/")
                file = open(os.path.join(os.getenv("FILE_PATH") + "setting.md"), "w")
                file.write("#setting.txt")
                file.close()
                docs = load(os.path.join(os.getenv("FILE_PATH") + "setting.md"))
                # docs = load(path="C:\\Users\\14153\\Desktop\\test.md")
                splits = chain.split(docs, chunk_size=1000, chunk_overlap=200)
                createStore("Intial_db", splits)
                db = "Intial_db"
                self.append(db)
            # 程序启动时就应该创建初始知识库，并存入一个空文件!!!!!
            persist_directory = "apps/QA/VectorStore/" + db
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings()
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)  # 加载向量数据库
            with_message_history = chain.chain(vectorstore=vectorstore, model_name=model, temperature=temperature)

            session_id = "test_11"  # 考虑如何对聊天记录编号？？？？？
            answer = with_message_history.invoke(
                {"input": question},
                config={"configurable": {"session_id": session_id}},
            )
            # 测试：（下述问题仅能通过RAG得到的答案回答，用于测试RAG是否成功；第二个问题用于测试问题一的聊天记录是否已被大模型考虑在内）
            # What is Task Decomposition?
            # What are common ways of doing it?
            current_page = 'index'
            utils.printMidRes(question, model, db, temperature, answer)
            return render(request, "index.html", {"question": question, "message": str(answer),
                                                  "models": self.models, "model": model,
                                                  "db": db, "temperature": temperature,
                                                  "dbs": dbs, 'current_page': current_page})
        return render(request, "index.html")


@method_decorator(csrf_exempt, name="dispatch")
class knowladgeManagementView(View):
    current_page = "km"

    def get(self, request, *args, **kwargs):
        dbs = os.listdir(os.getenv("persist_directory"))
        dbs.append("新建知识库")
        return render(request, "knowladgeManagementIndex.html",
                      {'current_page': self.current_page, 'dbs': dbs})

    def post(self, request, *args, **kwargs):
        db_form = dbForm(request.POST, request.FILES)
        dbs = os.listdir(os.getenv("persist_directory"))
        if db_form.is_valid():
            chunk_size = db_form.cleaned_data["chunk_size"]
            chunk_overlap = db_form.cleaned_data["chunk_overlap"]
            file = db_form.cleaned_data["file_"]
            db = db_form.cleaned_data["db"]
            kname = db_form.cleaned_data["kname"]
            path = os.path.join(os.getenv("FILE_PATH"), file.name)  # 拼接文件路径
            with open(path, "wb") as f:  # 写入文件
                for chunk in file.chunks():
                    f.write(chunk)
            print(db)
            print(chunk_size)
            print(chunk_overlap)
            print(file.content_type)
            print(kname)
            if kname == '#':
                pass
            if db in dbs:  # 向知识库中增添文档
                persist_directory = "apps/QA/VectorStore/" + db
                import chromadb
                vectorstore = Chroma(persist_directory=persist_directory)
                doc = load(path)
                splits = chain.split(doc, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                print(splits[0].metadata)
                client = chromadb.PersistentClient(path=persist_directory)
                print(vectorstore._collection.name)
                # uses base model and cpu
                import chromadb.utils.embedding_functions as embedding_functions
                openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    model_name="text-embedding-3-small"
                )
                collection = client.get_collection(name=vectorstore._collection.name, embedding_function=openai_ef)
                collection.add(documents=[str(i) for i in splits],
                               metadatas=[i.metadata for i in splits],
                               ids=[str(i) for i in range(len(splits))])
                print(vectorstore._collection.count())
            elif db == "新建知识库":
                docs = load()
                createStore()
                print()
            return render(request, "knowladgeManagementIndex.html",
                          {'current_page': self.current_page, 'dbs': dbs, 'db': db})
        return render(request, "knowladgeManagementIndex.html",
                      {'current_page': self.current_page, 'dbs': dbs})
