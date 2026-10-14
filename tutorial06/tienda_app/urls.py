from django.urls import path
from .api.views import CompraAPIView, InventarioAPIView, ProductosAPIView
from .views import CompraView

urlpatterns = [
    # Vista HTML (CBV)
    path('compra/<int:libro_id>/', CompraView.as_view(), name='finalizar_compra'),

    # API REST v1 (Django - Monolito)
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),
    path('api/v1/inventario/', InventarioAPIView.as_view(), name='api_inventario'),
    path('api/v1/productos/', ProductosAPIView.as_view(), name='api_productos'),
]
