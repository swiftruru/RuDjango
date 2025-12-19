from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def hello(request):
    return HttpResponse('hello, world')

def hello2(request):
    return HttpResponse('hello, world2')

def about(request):
    return render(request, 'blog/about.html')

def home(request):
    person1 = {
        'name': '大頭綠',
        'age': 17,
        'slogan': ['唯天唯大', '如日方中', '英姿煥發']
    }
    person2 = {
        'name': '大頭藍',
        'age': 18,
        'slogan': ['志在四方', '勇往直前', '心懷天下']
    }
    person3 = {
        'name': '大頭紅',
        'age': 19,
        'slogan': ['才華洋溢', '氣宇軒昂', '光芒萬丈']
    }
    context = {
        'people':[person1, person2, person3],
        'version': 1.0,
        'date': '2025-12-19',
        'last_update': '2025-12-19'
    }
    return render(request, 'blog/home.html', context)