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

class DisasterVictim(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

class Donation(models.Model):
    DONATION_TYPES = [
        ('AIRTIME', 'Airtime'),
        ('MONEY', 'Mobile Money'),
    ]
    donor_phone = models.CharField(max_length=20)
    recipient_phone = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donation_type = models.CharField(max_length=10, choices=DONATION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)