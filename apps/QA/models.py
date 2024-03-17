from django.db import models


class knowledgeStore(models.Model):
    """
    知识库模型
    """
    # on_delete参数表示对应的外键被删除后，当前数据应该怎么办？CASCADE表示级联删除，SET_NULL表示设置为空
    ks_name = models.CharField(max_length=50, verbose_name="知识库名")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    state = models.BooleanField(blank=True, verbose_name="状态")
    data_num = models.IntegerField(verbose_name="数据条目数")
    class Meta:
        verbose_name = "知识库"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.ks_name


class DocStore(models.Model):
    """
    知识库文件模型
    """
    # on_delete参数表示对应的外键被删除后，当前数据应该怎么办？CASCADE表示级联删除，SET_NULL表示设置为空
    ks_name = models.ForeignKey(knowledgeStore, verbose_name=u"知识库名", null=True, blank=True,
                                on_delete=models.CASCADE)
    doc_name = models.CharField(max_length=50, verbose_name="文件名称")
    load_time = models.DateTimeField(auto_now_add=True, verbose_name="加载时间")
    state = models.BooleanField(blank=True, verbose_name="状态")

    class Meta:
        verbose_name = "知识库文件"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.doc_name


class chatTopic(models.Model):
    """
    聊天主题模型
    """
    # on_delete参数表示对应的外键被删除后，当前数据应该怎么办？CASCADE表示级联删除，SET_NULL表示设置为空
    ct_name = models.CharField(max_length=50, verbose_name="聊天主题名称")
    ct_session_id = models.CharField(max_length=50, null=True, verbose_name="主题检索id")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    state = models.BooleanField(blank=True, verbose_name="状态")

    class Meta:
        verbose_name = "聊天主题"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.ct_name


class chatHistory(models.Model):
    """
    聊天记录模型
    """
    # on_delete参数表示对应的外键被删除后，当前数据应该怎么办？CASCADE表示级联删除，SET_NULL表示设置为空
    ct_name = models.ForeignKey(chatTopic, verbose_name=u"聊天主题", null=True, blank=True, on_delete=models.CASCADE)
    ch_content = models.CharField(max_length=5000, verbose_name="聊天记录")
    state = models.BooleanField(blank=True, verbose_name="状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="发送/回复时间")

    class Meta:
        verbose_name = "聊天记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.ch_name
