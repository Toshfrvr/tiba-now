from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    DoctorViewSet,
    PatientViewSet,
    AppointmentViewSet,
    SpecialistViewSet,
    PaymentViewSet,
    DoctorBySpecialtyView,
    AppointmentCreateView,
    MyAppointmentsView,
    SymptomMatchView,
    RegisterView,        #  Register endpoint
    UserRoleView,        #  Add role-checker view
)

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'specialists', SpecialistViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    #  Authentication Endpoints
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/role/', UserRoleView.as_view(), name='user_role'),  #  Identify user role (patient/doctor/admin)

    #  Custom Endpoints
    path('doctors/by-specialty/', DoctorBySpecialtyView.as_view(), name='doctors_by_specialty'), 
    path('appointments/book/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointments/my/', MyAppointmentsView.as_view(), name='my_appointments'),
    path('symptom-match/', SymptomMatchView.as_view(), name='symptom_match'),

    #  ViewSets
    path('', include(router.urls)),
    
]
