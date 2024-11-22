from django.urls import path
from .views import classify_rice

urlpatterns = [
    path('classify/', classify_rice, name='classify_rice'),
]
