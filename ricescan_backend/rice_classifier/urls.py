from django.urls import path
from . import views
from rice_classifier.views import classify_rice

urlpatterns = [
    path('classify-rice/', views.classify_rice, name='classify_rice'),
]
