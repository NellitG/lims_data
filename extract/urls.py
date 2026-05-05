"""
URL configuration for extract project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.samples.urls')),
    # path('api/', include('app.embu.urls')),
    # path('api/', include('app.kilifi.urls')),
    # path('api/', include('app.kajiado.urls')),
    # path('api/', include('app.kirinyaga.urls')),
    # path('api/', include('app.kitui.urls')),
    # path('api/', include('app.machakos.urls')),
    # path('api/', include('app.makueni.urls')),
    # path('api/', include('app.kwale.urls')),
    # path('api/', include('app.meru.urls')),
    # path('api/', include('app.makueni.urls')),
    # path('api/', include('app.muranga.urls')),
    # path('api/', include('app.tharaka.urls')),
    # path('api/', include('app.nyeri.urls')),
    # path('api/', include('app.transnzoia.urls')),
    # path('api/', include('app.uasingishu.urls')),
    
]
