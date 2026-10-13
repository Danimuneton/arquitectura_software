from django.urls import path
from .api.views import CompraAPIView, InventarioAPIView
from .views import CompraView

urlpatterns = [
    # Vista HTML (CBV) — "puerta 1" hacia la lógica de negocio
    path('compra/<int:libro_id>/', CompraView.as_view(), name='finalizar_compra'),

    # API REST (DRF) — "puerta 2" hacia la MISMA lógica de negocio
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),
    path('api/v1/inventario/', InventarioAPIView.as_view(), name='api_inventario'),
]
