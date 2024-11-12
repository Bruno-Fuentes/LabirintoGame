from django.db import models

# Create your models here.
from django.db import models

class Score(models.Model):
    player_name = models.CharField(max_length=100)
    points = models.IntegerField()
    time_spent = models.FloatField()  # em segundos
    date_played = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player_name} - {self.points} pontos"