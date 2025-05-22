from django.db import models
from django.contrib.auth.models import User

class Specialist(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialist, on_delete=models.SET_NULL, null=True)
    bio = models.TextField()
    is_available = models.BooleanField(default=True)
    available_times = models.JSONField(default=list)  # e.g., ["Monday 10AM-2PM"]

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.get_full_name()

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, null=True, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default='pending')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.user.username} → {self.doctor.user.username} @ {self.date} {self.time}"

class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=[('mpesa', 'M-Pesa'), ('stripe', 'Stripe')])
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"

class SymptomSpecialtyMap(models.Model):
    symptom = models.CharField(max_length=100)
    specialty = models.ForeignKey(Specialist, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.symptom} → {self.specialty.name}"
