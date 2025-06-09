from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Doctor, Patient, Appointment, Specialist, Payment, SymptomSpecialtyMap

User = get_user_model()

# ✅ User Serializer with full_name
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'is_staff']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


# ✅ Specialist Serializer
class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = ['id', 'name', 'description']


# ✅ Doctor Serializer
class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specialty = SpecialistSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialty', 'bio', 'is_available', 'available_times']


# ✅ Patient Serializer
class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user', 'age', 'gender', 'phone', 'address']


# ✅ Appointment Serializer
class AppointmentSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), write_only=True)
    doctor_detail = DoctorSerializer(source='doctor', read_only=True)
    patient_detail = PatientSerializer(source='patient', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'doctor_detail', 'patient_detail', 'date', 'time', 'status', 'notes']

    def create(self, validated_data):
        validated_data.pop('user', None)  # Just in case
        return super().create(validated_data)


# ✅ Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    appointment = serializers.PrimaryKeyRelatedField(queryset=Appointment.objects.all(), write_only=True)
    appointment_detail = AppointmentSerializer(source='appointment', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'appointment', 'appointment_detail', 'amount', 'method', 'transaction_id', 'status', 'created_at']


# ✅ Symptom Match Serializer
class SymptomSpecialtyMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymptomSpecialtyMap
        fields = ['id', 'symptom', 'specialty']


# ✅ Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    is_patient = serializers.BooleanField(required=False)
    is_doctor = serializers.BooleanField(required=False)

    # Patient-specific
    age = serializers.IntegerField(required=False)
    gender = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    address = serializers.CharField(required=False)

    # Doctor-specific
    bio = serializers.CharField(required=False)
    specialty = serializers.PrimaryKeyRelatedField(queryset=Specialist.objects.all(), required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password2',
            'is_patient', 'is_doctor',
            'age', 'gender', 'phone', 'address',
            'bio', 'specialty'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match."})
        if not attrs.get('is_patient') and not attrs.get('is_doctor'):
            raise serializers.ValidationError({"role": "You must choose either patient or doctor."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        is_patient = validated_data.pop('is_patient', False)
        is_doctor = validated_data.pop('is_doctor', False)

        age = validated_data.pop('age', None)
        gender = validated_data.pop('gender', '')
        phone = validated_data.pop('phone', '')
        address = validated_data.pop('address', '')

        bio = validated_data.pop('bio', '')
        specialty = validated_data.pop('specialty', None)

        user = User.objects.create_user(**validated_data)
        user.is_patient = is_patient
        user.is_doctor = is_doctor
        user.save()

        if is_patient:
            Patient.objects.create(user=user, age=age or 0, gender=gender, phone=phone, address=address)
        elif is_doctor:
            Doctor.objects.create(user=user, bio=bio, specialty=specialty)

        return user
