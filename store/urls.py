
from django.urls import path 
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('register/',views.register_user,name='register'),
    path('product/<int:pk>',views.product,name='product'),
    path('category/<str:foo>',views.category,name='category'),
    path('category_summary/',views.category_summary,name='category_summary'),
    path('update_user/',views.update_user,name='update_user'),
    path('update_password/',views.update_password,name='update_password'),
    path('update_info/',views.update_info,name='update_info'),
    path('search/',views.search,name='search'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-category/', views.add_category, name='add_category'),
    path('update-product/<int:product_id>/', views.update_product, name='update_product'),

    path('delete-product/', views.delete_product, name='delete_product'),
    path('update-product-list/', views.update_product_list, name='update_product_list'),

    path('custom-admin/', views.admin_panel, name='custom_admin'),
    path('login_admin', views.login_admin, name='login_admin'),

]