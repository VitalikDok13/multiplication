from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('multi/', include('multi_tab.urls')),
    path('', RedirectView.as_view(url='/multi/multiplication/', permanent=True)),
]