from django.db import models

class Car(models.Model):
    model = models.CharField(max_length=50, verbose_name='Марка автомобиля')
    price = models.FloatField(verbose_name='Цена аренды за день')
    status = models.PositiveSmallIntegerField(default='1', verbose_name='Состояние автомобиля')
    start_use_date = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='Дата начала аренды автомобиля')
    end_use_date = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='Дата завершения аренды автомобиля')
    order = models.ForeignKey('Order', null=True, blank=True, on_delete=models.CASCADE, verbose_name='Заказ')

    class Meta:
        verbose_name_plural = 'Автомобили'
        verbose_name = 'Автомобиль'
        ordering = ['-status']

class Order(models.Model):
    comment = models.TextField(verbose_name='Комментарий')

    class Meta:
        verbose_name_plural = 'Заказы'
        verbose_name = 'Заказ'