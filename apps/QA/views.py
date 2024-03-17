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
import time
from apps.QA.models import DocStore, chatTopic, chatHistory, knowledgeStore
from langchain_openai import OpenAIEmbeddings
import chromadb


@method_decorator(csrf_exempt, name="dispatch")
class FirstView(View):
    models = ["gpt-3.5-turbo", "百度千帆大模型"]

    def get(self, request, *args, **kwargs):
        dbs = os.listdir(os.getenv("persist_directory"))
        current_page = 'index'
        cts = chatTopic.objects.all().order_by("create_time")
        ct = cts[0]
        return render(request, "index.html", {"models": self.models, "model": "百度千帆大模型",
                                              "db": "Intial_db", "temperature": 0,
                                              "dbs": dbs, 'current_page': current_page, "cts": cts, "ct": ct})

    def post(self, request, *args, **kwargs):
        question_form = questionForm(request.POST)
        dbs = os.listdir(os.getenv("persist_directory"))
        if question_form.is_valid():
            # 获取数据
            question = question_form.cleaned_data["question"]
            model = question_form.cleaned_data["model"]
            db = question_form.cleaned_data["db"]
            temperature = question_form.cleaned_data["temperature"]
            old_topic = question_form.cleaned_data["old_topic"]
            new_topic = question_form.cleaned_data["new_topic"]

            # 选择或新建聊天主题
            session_id = ""
            now_ct_name = ""
            cts_raw = chatTopic.objects.all()
            cts = [i.ct_name for i in cts_raw]
            print("new_topic:" + new_topic)
            print("old_topic:" + old_topic)
            if new_topic or not cts_raw:  # 新建聊天主题(主动新建或者当前无主题)
                if not cts_raw:
                    if len(question) < 10:
                        new_topic = question[0:-1]
                    else:
                        new_topic = question[0:10]
                print("新建聊天主题：" + new_topic)
                timestamp = int(time.time())
                session_id = str(timestamp)
                chat_topic = chatTopic()
                chat_topic.ct_name = new_topic
                chat_topic.ct_session_id = session_id
                chat_topic.state = True
                chat_topic.save()
                now_ct_name = new_topic
                cts.append(now_ct_name)
            else:  # 使用旧聊天主题
                try:
                    session_id = chatTopic.objects.get(ct_name=old_topic).ct_session_id
                    print("使用现有聊天主题：" + old_topic)
                    now_ct_name = old_topic
                except chatTopic.DoesNotExist as e:
                    pass

            # 选择或新建知识库
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
                dbs.append(db)
                ks = knowledgeStore()
                ks.ks_name = "Intial_db"
                ks.state = True
                ks.data_num = len(splits)
                ks.save()
            # 程序启动时就应该创建初始知识库，并存入一个空文件!!!!!
            persist_directory = "apps/QA/VectorStore/" + db
            embeddings = OpenAIEmbeddings()
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)  # 加载向量数据库

            # 提问
            with_message_history = chain.chain(vectorstore=vectorstore, model_name=model, temperature=temperature)
            answer = with_message_history.invoke(
                {"input": question},
                config={"configurable": {"session_id": session_id}},
            )

            # 上传聊天记录
            chat_history = chatHistory()
            print("当前聊天主题为：" + now_ct_name)
            chat_history.ct_name = chatTopic.objects.get(ct_name=now_ct_name)
            chat_history.ch_content = question + "|||" + answer  # 使用|||符号作为问题与回答之间的分隔符
            chat_history.state = True
            chat_history.save()

            # 回传前端
            current_page = 'index'
            utils.printMidRes(question, model, db, temperature, answer)
            return render(request, "index.html", {"question": question, "message": str(answer),
                                                  "models": self.models, "model": model,
                                                  "db": db, "temperature": temperature,
                                                  "dbs": dbs, 'current_page': current_page,
                                                  "ct": now_ct_name, 'cts': cts})
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
            # 获取数据
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

            # 向数据库中新增文件
            if db in dbs:  # 向知识库中增添文档
                persist_directory = "apps/QA/VectorStore/" + db
                vectorstore = Chroma(persist_directory=persist_directory)
                doc = load(path)
                splits = chain.split(doc, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                client = chromadb.PersistentClient(path=persist_directory)
                import chromadb.utils.embedding_functions as embedding_functions
                openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    api_base=os.getenv("OPENAI_API_BASE"),
                    model_name="text-embedding-3-small"
                )
                # print("当前collection包含的数据条目数：" + str(vectorstore._collection.count()))
                collection = client.get_collection(name=vectorstore._collection.name, embedding_function=openai_ef)
                ks = knowledgeStore.objects.get(ks_name=db)
                collection.add(documents=[str(i) for i in splits],
                               metadatas=[i.metadata for i in splits],
                               ids=[str(i + ks.data_num) for i in range(len(splits))])
                ks.data_num += len(splits)  # 更新数据条目数
                ks.save()
                # print("添加后collection包含的数据条目数：" + str(vectorstore._collection.count()))
                ds = DocStore()  # 数据库新增文件
                ds.state = True
                ds.doc_name = file.name
                ds.ks_name = knowledgeStore.objects.get(ks_name=db)
                ds.save()
            elif db == "新建知识库" and kname:
                # 新数据库中加入setting文件
                fileSet = open(os.path.join(os.getenv("FILE_PATH") + "setting.md"), "w")
                fileSet.write("#setting.md")
                fileSet.close()
                docs = load(os.path.join(os.getenv("FILE_PATH") + "setting.md"))
                splits = chain.split(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                createStore(kname, splits)
                ks = knowledgeStore()
                ks.ks_name = kname
                ks.state = True
                ks.data_num = len(splits)
                # ks.save()

                # 新数据库中新增文件
                db = kname
                persist_directory = "apps/QA/VectorStore/" + db
                vectorstore = Chroma(persist_directory=persist_directory)
                doc = load(path)
                splits = chain.split(doc, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                client = chromadb.PersistentClient(path=persist_directory)
                import chromadb.utils.embedding_functions as embedding_functions
                openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    api_base=os.getenv("OPENAI_API_BASE"),
                    model_name="text-embedding-3-small"
                )
                # print("当前collection包含的数据条目数：" + str(vectorstore._collection.count()))
                collection = client.get_collection(name=vectorstore._collection.name, embedding_function=openai_ef)

                collection.add(documents=[str(i) for i in splits],
                               metadatas=[i.metadata for i in splits],
                               ids=[str(i + ks.data_num) for i in range(len(splits))])
                ks.data_num += len(splits)  # 更新数据条目数
                ks.save()
                # print("添加后collection包含的数据条目数：" + str(vectorstore._collection.count()))
                ds = DocStore()  # 数据库新增文件
                ds.state = True
                ds.doc_name = file.name
                ds.ks_name = knowledgeStore.objects.get(ks_name=db)
                ds.save()
                dbs.append(db)

            return render(request, "knowladgeManagementIndex.html",
                          {'current_page': self.current_page, 'dbs': dbs, 'db': db})
        return render(request, "knowladgeManagementIndex.html",
                      {'current_page': self.current_page, 'dbs': dbs})
