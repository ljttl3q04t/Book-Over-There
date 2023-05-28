import datetime

from django.db import models
from django.db.models import ManyToManyField
from django.db.models.fields.files import FieldFile
from django.utils import timezone


class BaseModel(models.Model):
    class Meta:
        abstract = True

    def as_dict(self, fields=None, exclude=None):
        opts = self._meta
        data = {}
        fs = list(opts.concrete_fields) + opts.virtual_fields + list(opts.many_to_many)
        for f in fs:
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if isinstance(f, ManyToManyField):
                if self.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = list(f.value_from_object(self).values_list('pk', flat=True))
            else:
                data[f.name] = f.value_from_object(self)
        return data

    def as_json(self, fields=None, exclude=None, **kwargs):
        """
        Return a JSON-dumpable dict
        """
        data = self.as_dict(fields, exclude)
        for attr in data:
            if isinstance(data[attr], datetime.time):
                data[attr] = data[attr].strftime(kwargs.get('time_format', '%H:%M:%S'))
            elif isinstance(data[attr], datetime.time):
                data[attr] = data[attr].strftime(kwargs.get('date_format', '%Y-%m-%d %H:%M:%S'))
            elif isinstance(data[attr], FieldFile):
                file_data = {}
                for k in kwargs.get('file_attributes', ('url',)):
                    file_data[k] = data[attr].__getattribute__(k) if hasattr(data[attr], k) else ''
                data[attr] = file_data
        return data


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
