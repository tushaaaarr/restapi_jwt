from django.contrib import admin
from django.urls import path,include
from home import views
from home.views import BookViews ,MyObtainTokenPairView,LoginView

from rest_framework_simplejwt.views import (
   TokenObtainPairView,
   TokenRefreshView,
)

urlpatterns = [
    path('',views.index,name='index'),
    # path('login',views.login, name='login'),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', views.logout, name="logout"),

    # Libraian (Related to book)
    path('view-all_books',views.ViewBooks,name='view-all_books'),
    path('librarian/add-book',views.AddBook,name='add-book'),
    path('librarian/view-book/<int:isbn>', BookViews.as_view()),
    path('librarian/view-book', BookViews.as_view()),
    path('librarian/update-book/<int:isbn>',views.update_book,name='update_book'),
    path('librarian/delete-book/<int:isbn>',views.delete_book,name='delete_book'),


    # Libraian (Related to Member)
    path('librarian/view-all_members',views.ViewMembers,name='view-all_books'),
    path('librarian/add-member',views.AddMember,name='add-book'),
    path('librarian/update-member/<int:id>',views.update_member,name='update_book'),
    path('librarian/delete-member/<int:id>',views.delete_member,name='delete_book'),

    
    # Member (Related to Book)
    path('member/view-all_books',views.M_ViewBooks,name='view-all_books'),
    path('member/borrow-book',views.M_BorrowBook,name='borrow-book'),
    path('member/return-book/<int:id>',views.M_ReturnBook,name='return_book'),
    path('member/view-issued_books',views.M_IssuedBooks,name='view-issued_books'),



    # Jwt auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),name='token_refresh'),
    path('token/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),

]   
