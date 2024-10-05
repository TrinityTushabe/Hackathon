from django.contrib import admin

from .models import HealthTip, FirstAidProcedure, USSDSession, HealthcareProfessional

# Register your models here
admin.site.register(HealthTip)
admin.site.register(FirstAidProcedure)
admin.site.register(USSDSession)
admin.site.register(HealthcareProfessional)