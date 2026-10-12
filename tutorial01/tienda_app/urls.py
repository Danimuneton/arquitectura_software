from django.urls import path
from .api.views import CompraAPIView
from .views import CompraView, CompraRapidaView, compra_rapida_fbv

urlpatterns = [
    # Vista final (CBV + Service Layer) - arquitectura de grado empresarial
    path('compra/<int:libro_id>/', CompraView.as_view(), name='finalizar_compra'),

    # Etapas de la evolución del tutorial (evidencia didáctica):
    # Paso 1: FBV Spaghetti
    path('compra-rapida-fbv/<int:libro_id>/', compra_rapida_fbv, name='compra_rapida_fbv'),
    # Paso 2: Class-Based View intermedia
    path('compra-rapida-cbv/<int:libro_id>/', CompraRapidaView.as_view(), name='compra_rapida_cbv'),

    # API JSON
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),
]
