from django.db import models


# Create your models here.
class ImageTransform(models.Model):
    image = models.FileField(upload_to="transformed_images/")
