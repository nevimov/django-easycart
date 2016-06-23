from django.db import models


class Item(models.Model):
    category = models.CharField(max_length=50, editable=False)
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.category:
            self.category = self.__class__.__name__.lower()
        super(Item, self).save(*args, **kwargs)


class Book(Item):
    author = models.CharField(max_length=40)


class Magazine(Item):
    issue = models.CharField(max_length=40)
