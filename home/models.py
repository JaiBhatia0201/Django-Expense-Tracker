from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Expense(models.Model):
    EXPENSE_TYPE_CHOICES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True),
    salary = models.IntegerField(default=0)
    name = models.CharField(max_length=100, default='something')
    price = models.IntegerField(default=0)
    type = models.CharField(max_length=7, choices=EXPENSE_TYPE_CHOICES, default="expense")
    date = models.DateField(default=date.today)
    category = models.CharField(max_length=100, default="miscellaneous")
    
    def __str__(self):
        return f"{self.name} - {self.type} - {self.price}"