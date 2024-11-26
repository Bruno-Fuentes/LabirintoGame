from django.db import models

# Create your models here.
from django.db import models

from django.db import models

class Score(models.Model):
    # Defina os campos do modelo aqui
    name = models.CharField(max_length=100)
    points = models.IntegerField()
    time_spent = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.points}"
