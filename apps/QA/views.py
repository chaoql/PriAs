from django.shortcuts import render
from django.views.generic.base import View
import apps.QA.chain as chain
from apps.QA.forms import questionForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name="dispatch")
class FirstView(View):
    def get(self, request, *args, **kwargs):
        current_page = 'index'
        return render(request, "index.html", {"models": ["gpt-3.5-turbo"],
                                              "functions": ["LLM问答", "结合知识库问答"], 'current_page': current_page})

    def post(self, request, *args, **kwargs):
        question_form = questionForm(request.POST)
        if question_form.is_valid():
            question = question_form.cleaned_data["question"]
            docs = chain.load()
            splits = chain.split(docs)
            vectorstore = chain.store(splits)
            rag_chain = chain.chain(vectorstore, "gpt-3.5-turbo", temperature=0)
            message = rag_chain.invoke(question)
            current_page = 'index'
            return render(request, "index.html", {"question": question, "message": str(message),
                                                  "models": ["gpt-3.5-turbo"],
                                                  "functions": ["LLM问答", "结合知识库问答"],
                                                  'current_page': current_page})
        return render(request, "index.html")


class knowladgeManagementView(View):
    def get(self, request, *args, **kwargs):
        current_page = "km"
        return render(request, "knowladgeManagementIndex.html", {'current_page': current_page})

    def post(self, request, *args, **kwargs):
        pass
