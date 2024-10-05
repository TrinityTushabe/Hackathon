from django.db import models

class HealthTip(models.Model):
    keyword = models.CharField(max_length=50)
    content = models.TextField()

class FirstAidProcedure(models.Model):
    keyword = models.CharField(max_length=50)
    steps = models.TextField()

class USSDSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    current_menu = models.CharField(max_length=50)
    last_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class HealthcareProfessional(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    specialty = models.CharField(max_length=100)