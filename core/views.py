from django.shortcuts import render
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Doctor, Patient, Appointment, Specialist, Payment, SymptomSpecialtyMap
from .serializers import (
    DoctorSerializer,
    PatientSerializer,
    AppointmentSerializer,
    SpecialistSerializer,
    PaymentSerializer,
    SymptomSpecialtyMapSerializer,
    RegisterSerializer,
    UserSerializer
)

User = get_user_model()

#  Custom JWT Login with Role
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        print(data)

    

        if user.is_staff:
            role = "admin"
        elif hasattr(user, "doctor"):
            role = "doctor"
        elif hasattr(user, "patient"):
            role = "patient"
        else:
            role = "user"

        data["role"] = role
        data["username"] = user.username
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


#  User Registration View
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        # Create related profile based on role
        if self.request.data.get("is_patient"):
            Patient.objects.get_or_create(user=user)
        elif self.request.data.get("is_doctor"):
            Doctor.objects.get_or_create(user=user)


#  Check Logged-in User Role
class UserRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        role = (
            "admin" if user.is_staff else
            "doctor" if hasattr(user, "doctor") else
            "patient" if hasattr(user, "patient") else
            "user"
        )
        return Response({"username": user.username, "role": role})


#  Doctor ViewSet (CRUD - Admin only)
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = [permissions.AllowAny]


#  Doctor Listings by Specialty (Public)
class DoctorBySpecialtyView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        specialty = self.request.query_params.get('specialty')
        if specialty:
            return Doctor.objects.filter(specialty__iexact=specialty)
        return Doctor.objects.all()


#  Patient ViewSet
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]


#  Appointment ViewSet
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


#  Book Appointment (Quick Create)
class AppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


#  View My Bookings
class MyAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            patient = Patient.objects.get(user=self.request.user)
            return Appointment.objects.filter(patient=patient).order_by('-date')
        except Patient.DoesNotExist:
            return Appointment.objects.none()


#  Specialist ViewSet
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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No specialists found for the given symptom."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


#  Payment ViewSet
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
