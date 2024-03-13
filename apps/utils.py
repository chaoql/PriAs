def parameters():
    return {'max_length': 1000}


def printMidRes(question, model, db, temperature, answer):
    print("问题：" + question)  # What is Task Decomposition?
    print("模型：" + model)
    print("知识库：" + db)
    print("temperature：" + str(temperature))
    print("答案：" + answer)
