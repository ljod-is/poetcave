from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    name_dative = models.CharField(max_length=100, null=False, blank=False)
    birth_year = models.SmallIntegerField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)

    def __str__(self):
        return '%s (%d)' % (self.name, self.birth_year)
