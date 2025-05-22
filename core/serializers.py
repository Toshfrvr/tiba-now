from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Doctor, Patient, Appointment, Specialist, Payment, SymptomSpecialtyMap

User = get_user_model()

# 🔐 User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff']

# ✨ Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

# 💼 Specialist Serializer
class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = ['id', 'name', 'description']

# 🩺 Doctor Serializer
class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specialty = SpecialistSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialty', 'bio', 'is_available', 'available_times']

# 🧍 Patient Serializer
class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user', 'age', 'gender', 'phone', 'address']

# 📅 Appointment Serializer
class AppointmentSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), write_only=True)
    doctor_detail = DoctorSerializer(source='doctor', read_only=True)
    patient_detail = PatientSerializer(source='patient', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'doctor_detail', 'patient_detail', 'date', 'time', 'status', 'notes']

# 💳 Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    appointment = serializers.PrimaryKeyRelatedField(queryset=Appointment.objects.all(), write_only=True)
    appointment_detail = AppointmentSerializer(source='appointment', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'appointment', 'appointment_detail', 'amount', 'method', 'transaction_id', 'status', 'created_at']

# 🧠 Symptom Match Serializer
class SymptomSpecialtyMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymptomSpecialtyMap
        fields = ['id', 'symptom', 'specialty']
