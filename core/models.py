from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ---- CUSTOM USER ----
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    def __str__(self):
        return f" ({self.role})"

# ---- SPECIALIST ----
class Specialist(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

# ---- DOCTOR ----
class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specialty = models.ForeignKey(
        Specialist,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors'
    )
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    available_times = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

# ---- PATIENT ----
class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.get_full_name()

# ---- APPOINTMENT ----
class Appointment(models.Model):
    patient = models.ForeignKey(
        Patient,
        null=True,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default='pending')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.user.username} → {self.doctor.user.username} @ {self.date} {self.time}"

# ---- PAYMENT ----
class Payment(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(
        max_length=50,
        choices=[('mpesa', 'M-Pesa'), ('stripe', 'Stripe')]
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"

# ---- SYMPTOM TO SPECIALTY MAP ----
class SymptomSpecialtyMap(models.Model):
    symptom = models.CharField(max_length=100)
    specialty = models.ForeignKey(
        Specialist,
        on_delete=models.CASCADE,
        related_name='symptom_mappings'
    )

    def __str__(self):
        return f"{self.symptom} → {self.specialty.name}"
