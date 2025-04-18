from django.urls import path #type:ignore
from . import views #type:ignore
from django.conf import settings #type:ignore
from django.conf.urls.static import static #type:ignore
from django.contrib.auth import views as auth_views #type:ignore
from . import views

urlpatterns = [
    path('', views.restaurant_list, name='homepage'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('ziggy-cafe/', views.ziggy_cafe_menu, name='ziggy_cafe_menu'),

    # Only one login/logout path needed
    path('login/', views.login_view, name='login'),  # Use your custom login_view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('terms/', views.terms_and_conditions, name='terms_and_conditions'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('cart/', views.cart_view, name='cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('place_order/', views.place_order, name='place_order'),
    path('signup/', views.signup, name='signup'),
    path('menu/', views.menu_view, name='menu_view'),
    path('order-success/', views.order_success, name='order_success'),
    path('contact/', views.contact_view, name='contact2'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])


