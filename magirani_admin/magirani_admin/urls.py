from django.contrib import admin
from django.urls import path


from club_bot.views import simple_payment, recurrent_payment

urlpatterns = [
    path('api/v1/payment', simple_payment),
    path('api/v1/recurrent', recurrent_payment),
    path('admin/', admin.site.urls),
    # path('admin/club_bot/user', dashboard_view, name='custom_dashboard')
]


