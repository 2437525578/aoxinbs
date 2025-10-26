from django.db import models
from django.utils import timezone  # 对应 datetime


# 迁移 Chemical 模型
class Chemical(models.Model):
    name_cn = models.CharField(max_length=255)
    cas_no = models.CharField(max_length=50, unique=True)
    specification = models.CharField(max_length=255, null=True, blank=True)
    form_state = models.CharField(max_length=50, null=True, blank=True)
    hazard_classes = models.TextField(null=True, blank=True)  # 存储为逗号分隔的字符串
    signal_word = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='chemicals_images/', null=True, blank=True)
    def __str__(self):
        return f'{self.name_cn} ({self.cas_no})'

    # 辅助属性，用于 Serializer 处理列表
    @property
    def hazard_classes_list(self):
        if self.hazard_classes:
            return self.hazard_classes.split(',')
        return []

    @hazard_classes_list.setter
    def hazard_classes_list(self, value_list):
        self.hazard_classes = ','.join(value_list)