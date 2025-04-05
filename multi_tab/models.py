# multi_tab/models.py
from django.db import models

class QuizResult(models.Model):
    OPERATION_TYPES = [
        ('multiplication', 'Умножение'),
        ('division', 'Деление'),
        ('squares', 'Квадраты чисел'),
    ]
    
    username = models.CharField(max_length=100)
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    question = models.CharField(max_length=50)
    user_answer = models.IntegerField()
    correct_answer = models.IntegerField()
    is_correct = models.BooleanField()
    attempts = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}: {self.question} = {self.user_answer} ({'✓' if self.is_correct else '✗'})"