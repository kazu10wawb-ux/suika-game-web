from django.db import models

# Create your models here.
from django.db import models

class GameScore(models.Model):
    player_name = models.CharField(max_length=100, default="プレイヤー1")
    steps = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player_name}: {self.steps}歩"