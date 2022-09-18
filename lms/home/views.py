from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import auth
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from django.template.response import TemplateResponse
from django.contrib.auth import authenticate
from django.conf import settings
from django.middleware import csrf
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from .authenticate import CustomAuthentication 
from django.contrib.auth import logout as django_logout

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from .serializers import MyTokenObtainPairSerializer





def index(request):
    if request.user.is_authenticated:
        if user_type.objects.get(user=request.user).is_librarian == True:
            return render(request,'librarian/index.html')
        elif user_type.objects.get(user=request.user).is_member == True:
            return render(request,'member/index.html')
        else:
            return HttpResponse("Need Membership....For more info try to contact librarian !")
    else:
        return redirect('/login')


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class LoginView(APIView):
    permission_classes = ([AllowAny])
    authentication_classes = ([JWTAuthentication])
    template_name = 'auth/login.html'
    def post(self, request, format=None):
        data = request.data
        response = Response()        
        username = data.get('username', None)
        password = data.get('password', None)
        user = authenticate(username=username, password=password)
        auth.login(request, user)
        if user is not None:
            if user.is_active:
                data = get_tokens_for_user(user)
                response.set_cookie(
                    key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
                    value = data["access"],
                    expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )
                csrf.get_token(request)
                response.data = {"Success" : "Login successfully... Please go to home page on next tab","data":data}
                # return HttpResponseRedirect('/')
                return response
            else:
                return Response({"No active" : "This account is not active!!"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"Invalid" : "Invalid username or password!!"}, status=status.HTTP_404_NOT_FOUND)
 
    def get(self,request):
        response = TemplateResponse(request, self.template_name)
        return response

def logout(request):
    django_logout(request)
    response = HttpResponseRedirect('/login')
    response.delete_cookie('access_token')
    return response


def is_librarian(crnt_user):
    if crnt_user.is_authenticated:
       return user_type.objects.filter(user=crnt_user).exists() and user_type.objects.get(user=crnt_user).is_librarian
       
# Libraian views (Related to book)
# VIEW BOOKS
@api_view(['GET'])
def ViewBooks(request):
    template_name = 'librarian/books.html'
    if is_librarian(request.user) == True:
        items = Book.objects.all()
        if items:
            data = BookSerializer(items,many =True)
            return render(request, template_name, {'data': items})
        else:
            return render(request, template_name, {'data': items})
    return HttpResponse('Only librarian can access this url ')

# ADD BOOK
@api_view(['POST','GET'])
def AddBook(request):
    if is_librarian(request.user) == True:
        if request.method == 'POST':
            serializer = BookSerializer(data = request.data)
            if serializer.is_valid():
                isbn = serializer.validated_data['isbn']
                if Book.objects.filter(isbn=isbn).exists():
                    return Response({"Book already exists !!"})
                else:
                    serializer.save()
                    return redirect('/librarian/view-book')
            else:
                return Response({"status": "error" ,"data":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        else:
            return render(request,'librarian/add_book.html')

    return HttpResponse('Only librarian can access this url ')


def update_book(request,isbn):
    try:
        book = Book.objects.get(isbn=isbn)
    except:
        return redirect('/librarian/view-book')
    
    return render(request,'librarian/update_book.html',{'book':book})

@api_view(['POST'])
def delete_book(request,isbn):
    if is_librarian(request.user) == True:
        item = get_object_or_404(Book, isbn=isbn)
        item.delete()
        return HttpResponseRedirect("/librarian/view-book")

    return HttpResponse('Only librarian can access this url ')
class BookViews(APIView):   
    template_name = 'librarian/books.html'
    # permission_classes = [AllowAny]
    authentication_classes = [CustomAuthentication]
    # view one book 
    def get(self, request,isbn=None):
        if isbn:
            item = Book.objects.get(isbn=isbn)
            serializer = BookSerializer(item)
        else:
            item = Book.objects.all()
            serializer = BookSerializer(item,many =True)
            # response = TemplateResponse(request,self.template_name,item)

        return render(request, self.template_name, {'data': item})
        # return response

    # Update book
    def post(self, request, isbn = None):
        if is_librarian(request.user) == True:
            item = Book.objects.get(isbn=isbn)  
            data = BookSerializer(instance=item, data=request.data)
            if data.is_valid():
                data.save()
                return HttpResponseRedirect("/librarian/view-book")
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return HttpResponse('Only librarian can access this url ')
# Libraian views (Related to Member)

# VIEW MEMBERS
@api_view(['GET'])
def ViewMembers(request):
    template_name = 'librarian/members.html'
    if is_librarian(request.user) == True:
        items = Member.objects.all()
        if items:
            data = MemberSerializer(items,many =True)
            return render(request, template_name, {'data': items})
        else:
            return render(request, template_name, {'data': items})
    return HttpResponse('Only librarian can access this url ')
# ADD Member
@api_view(['POST','GET'])
def AddMember(request):
    if is_librarian(request.user) == True:
        if request.method == 'POST':
            username = request.data['user']
            get_user = User.objects.get(id=username) 
            if Member.objects.filter(user = get_user).exists():
                return Response({"Member already exists !!"})
            else:
                serializer = MemberSerializer(data = request.data)
                if serializer.is_valid():
                    print(serializer.validated_data)
                    serializer.save()
                    return redirect('/librarian/view-all_members')
                else:
                    return Response({"status": "error" ,"data":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        else:
            data = User.objects.all()
            return render(request,'librarian/add_member.html',{'data':data})
    return HttpResponse('Only librarian can access this url ')

# UPDATE MEMBER
@api_view(['POST','GET'])
def update_member(request,id):
    template_name= 'librarian/update_member.html'
    if is_librarian(request.user) == True:
        if request.method == 'POST':
            item = Member.objects.get(id=id)  
            data = MemberSerializer(instance=item, data=request.data)
            if data.is_valid():
                data.save()
                return HttpResponseRedirect("/librarian/view-all_members")
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            member = Member.objects.get(id=id)
            return render(request, template_name,{'member':member})
    return HttpResponse('Only librarian can access this url ')
# DELETE MEMBER
@api_view(['POST'])
def delete_member(request,id):
    if is_librarian(request.user) == True:
        item = get_object_or_404(Member, id=id)
        item.delete()
        return HttpResponseRedirect("/librarian/view-all_members")
    return HttpResponse('Only librarian can access this url ')

# Member views (Related to Book)
# VIEW Books
@api_view(['GET'])
def M_ViewBooks(request):
    if request.user.is_authenticated:
        if user_type.objects.filter(user=request.user).exists() and user_type.objects.get(user=request.user).is_member == True:
            template_name = 'member/books.html'
            items = Book.objects.all()
            me = Member.objects.get(user=request.user)
            books_list = list()
            borrowed_books = []
            if Borrower.objects.filter(member=me).exists():
                borrowed_books = Borrower.objects.filter(member=me).values_list('book__id',flat=True)
            for book in items:
                if book.id in borrowed_books:
                    status = 'borrowed'
                    borrowed_id = Borrower.objects.filter(member=me).filter(book__id=book.id)[0].id
                else:
                    status = 'available'
                    borrowed_id = ''
                
                books_dict = {
                    'id':book.id,
                    'isbn':book.isbn,
                    'title':book.title,
                    'title':book.title,
                    'author':book.author,
                    'quantity':book.quantity,
                    'status':status,
                    'member_id':me.id,
                    'borrowed_id':borrowed_id,
                }
                books_list.append(books_dict)
           
            return render(request, template_name, {'data': books_list})
        else:
            return HttpResponse('You have a not membership for library....Contact with Librarian!')
    else:
        return HttpResponse("Login needed.!")

# Issued Books
@api_view(['GET'])
def M_IssuedBooks(request):
    if request.user.is_authenticated:
        if user_type.objects.filter(user=request.user).exists() and user_type.objects.get(user=request.user).is_member == True:
            template_name = 'member/issued_books.html'
            items = Book.objects.all()
            me = Member.objects.get(user=request.user)
            if Borrower.objects.filter(member=me).exists():
                borrowers = Borrower.objects.filter(member=me)  
                return render(request, template_name, {'data': borrowers})              
            else:
                return HttpResponse('No Issued book yet')
        else:
            return HttpResponse('You have a not membership for library....Contact with Librarian!')
    else:
        return HttpResponse("Login needed.!")

# Borrow Book
@api_view(['POST'])
def M_BorrowBook(request,):
    if request.method == 'POST':
        username = request.data['member']
        if Borrower.objects.filter(book = request.data['book']).exists():
            return Response({"Book already taken !!"})
        else:
            serializer = BorrowerSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                new_qty = int(Book.objects.get(id=request.data['book']).quantity) - 1
                Book.objects.filter(id=request.data['book']).update(quantity= new_qty) 
                return redirect('/member/view-all_books')
            else:
                return Response({"status": "error" ,"data":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
   
# DELETE MEMBER
@api_view(['POST','GET'])
def M_ReturnBook(request,id):
    book_nm= Borrower.objects.filter(id=id)[0].book
    book_id = Book.objects.get(title = book_nm).id
    new_qty = int(Book.objects.get(id = book_id).quantity) + 1
    Book.objects.filter(id=book_id).update(quantity= new_qty) 

    item = get_object_or_404(Borrower, id=id)
    item.delete()
    return HttpResponseRedirect("/member/view-all_books")



class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer