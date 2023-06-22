
from django.db import models

# Create your models here.

from django.db import models

class Asset(models.Model):
    id = models.AutoField(primary_key=True)
    tag_number = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id} - {self.tag_number}"

