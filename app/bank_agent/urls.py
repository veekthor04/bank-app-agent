from django.urls import path

from bank_agent.views import index


app_name = 'bank_agent'


urlpatterns = [
    path("", index, name="index")
]
