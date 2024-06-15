from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Expense
from django.db.models import Sum

@login_required(login_url='/login/')
def expenses(request):
    queryset = Expense.objects.all()
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    filter_type = request.GET.get('type')
    
    if start_date and end_date:
        queryset = queryset.filter(date__range=[start_date, end_date])
    elif start_date:
        queryset = queryset.filter(date__gte=start_date)
    elif end_date:
        queryset = queryset.filter(date__lte=end_date)
        
        
    if filter_type:
        queryset = queryset.filter(type=filter_type)
        
    expense_summary = queryset.filter(type='expense').values('category').annotate(total=Sum('price')).order_by('category')
    income_summary = queryset.filter(type='income').values('category').annotate(total=Sum('price')).order_by('category')
    
    expense_labels = [expense['category'] for expense in expense_summary]
    expense_values = [expense['total'] for expense in expense_summary]
    income_labels = [income['category'] for income in income_summary]
    income_values = [income['total'] for income in income_summary]
    
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        price = int(data.get('price', 0))
        type = data.get('type')
        category = data.get('category')
        date = data.get('date')
        
        Expense.objects.create(name=name, price=price, type=type, category=category, date=date)
        return redirect('/')

    if request.GET.get('search'):
        queryset = queryset.filter(name__icontains=request.GET.get('search'))
        
    total_sum = queryset.aggregate(Sum('price'))['price__sum'] or 0
    
    context = {
        'expenses': queryset, 
        'total_sum': total_sum,
        'start_date': start_date,
        'end_date': end_date,
        'filter_type': filter_type,
        'expense_labels': expense_labels,
        'expense_values': expense_values,
        'income_labels': income_labels,
        'income_values': income_values
    }
    return render(request, 'expense.html', context)

@login_required(login_url='/login/')
def update_expense(request, id):
    queryset = Expense.objects.get(id=id)
    
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        price = int(data.get('price', 0))
        type = data.get('type')
        category = data.get('category')
        date = data.get('date')
        
        queryset.name = name
        queryset.price = price
        queryset.type = type
        queryset.category = category
        queryset.date = date
        queryset.save()
        return redirect('/')
    
    context = {'expense': queryset}
    return render(request, 'update_expense.html', context)

@login_required(login_url='/login/')
def delete_expense(request, id):
    queryset = Expense.objects.get(id=id)
    queryset.delete()
    return redirect('/')

def login_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_obj = User.objects.filter(username=username).first()
            if not user_obj:
                messages.error(request, "Username not found")
                return redirect('/login/')
            user_auth = authenticate(username=username, password=password)
            if user_auth:
                login(request, user_auth)
                return redirect('expenses')
            messages.error(request, "Wrong Password")
            return redirect('/login/')
        except Exception as e:
            messages.error(request, "Something went Wrong")
            return redirect("/register/")
    return render(request, "login.html")
    
def register_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_obj = User.objects.filter(username=username)
            if user_obj.exists():
                messages.error(request, "Username is taken")
                return redirect('/register/')
            user_obj = User.objects.create(username=username)
            user_obj.set_password(password)
            user_obj.save()
            messages.success(request, "Account created")
            return redirect('/login')
        except Exception as e:
            messages.error(request, "Something went wrong")
            return redirect("/register")
    return render(request, "register.html")

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/login/')
def pdf(request):
    if request.method == 'POST':
        data = request.POST
        salary = int(data.get('salary'))
        name = data.get('name')
        price = int(data.get('price', 0))
        
        Expense.objects.create(salary=salary, name=name, price=price)
        return redirect('pdf')
    
    queryset = Expense.objects.all()
    if request.GET.get('search'):
        queryset = queryset.filter(name__icontains=request.GET.get('search'))
        
    total_sum = sum(expense.price for expense in queryset)
    
    username = request.user.username
    
    context = {'expenses': queryset, 'total_sum': total_sum, 'username': username}
    return render(request, 'pdf.html', context)