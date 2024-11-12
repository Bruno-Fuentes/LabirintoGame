from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Score
from .serializers import ScoreSerializer

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all().order_by('-points', 'time_spent')[:10]  # Top 10
    serializer_class = ScoreSerializer