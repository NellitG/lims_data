from django.contrib import admin
from .models import SoilSample

class SoilSampleAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'client_name', 'town', 'county', 'date_sample_received')
    # search_fields = ('sample_id', 'client_name', 'town', 'county')
    # list_filter = ('county', 'date_sample_received')

admin.site.register(SoilSample, SoilSampleAdmin)