from django.shortcuts import render
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from .models import Doctor, Patient, Appointment, Specialist, Payment, SymptomSpecialtyMap
from .serializers import (
    DoctorSerializer,
    PatientSerializer,
    AppointmentSerializer,
    SpecialistSerializer,
    PaymentSerializer,
    SymptomSpecialtyMapSerializer,
    RegisterSerializer
)

User = get_user_model()

# 🔐 User Registration View
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# Doctor ViewSet (CRUD - Admin only)
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAdminUser]

# Doctor Listings by Specialty (Public)
class DoctorBySpecialtyView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        specialty = self.request.query_params.get('specialty')
        if specialty:
            return Doctor.objects.filter(specialty__iexact=specialty)
        return Doctor.objects.all()

# Patient ViewSet
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

# Appointment ViewSet
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            patient = Patient.objects.get(user=self.request.user)
            serializer.save(patient=patient)
        except Patient.DoesNotExist:
            raise PermissionDenied("You must have a patient profile to book an appointment.")

# Book Appointment (Quick Create)
class AppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# View My Bookings
class MyAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).order_by('-date')

# Specialist ViewSet
class SpecialistViewSet(viewsets.ModelViewSet):
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer
    permission_classes = [permissions.AllowAny]

# Symptom Matching Assistant
class SymptomMatchView(generics.ListAPIView):
    serializer_class = SymptomSpecialtyMapSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        symptom = self.request.query_params.get('symptom')
        if symptom:
            return SymptomSpecialtyMap.objects.filter(symptom__icontains=symptom)
        return SymptomSpecialtyMap.objects.none()

# Payment ViewSet
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
