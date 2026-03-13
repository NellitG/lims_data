from django.db import models

class SoilSample(models.Model):

    client_name = models.CharField(max_length=200, null=True, blank=True)
    client_phone = models.CharField(max_length=50, null=True, blank=True)

    town = models.CharField(max_length=200, null=True, blank=True)
    county = models.CharField(max_length=200, null=True, blank=True)
    sub_county = models.CharField(max_length=200, null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)

    sample_id = models.CharField(max_length=100)

    previous_crop = models.CharField(max_length=200, null=True, blank=True)
    next_crop = models.CharField(max_length=200, null=True, blank=True)

    date_sample_received = models.DateField(null=True)

    test_required = models.CharField(max_length=100, default="Soil Test")

    def __str__(self):
        return self.sample_id