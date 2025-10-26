from django.db import models
from chemicals.models import Chemical # 关联到化学品定义
from django.conf import settings     # 关联到用户

class InventoryItem(models.Model):
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE, related_name='inventory_items', verbose_name="化学品")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="存放位置")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="数量")
    unit = models.CharField(max_length=20, verbose_name="单位") # 如: ml, g, L, kg, 瓶
    batch_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="批号")
    purchase_date = models.DateField(blank=True, null=True, verbose_name="采购日期")
    expiry_date = models.DateField(blank=True, null=True, verbose_name="有效期至")
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='added_inventory', verbose_name="添加人")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="最后更新")
    # unique_id = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="唯一标识码") # 可选：如二维码/条形码

    class Meta:
        verbose_name = "库存条目"
        verbose_name_plural = verbose_name
        ordering = ['chemical__name_cn', 'location'] # 默认排序

    def __str__(self):
        location_str = f" @ {self.location}" if self.location else ""
        return f"{self.chemical.name_cn} - {self.quantity} {self.unit}{location_str}"