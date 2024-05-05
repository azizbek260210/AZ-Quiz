from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from main import models

from random import sample


@login_required(login_url='dashboard:login')
def index(request):
    quizzes = models.Quiz.objects.filter(author=request.user.id)
    return render(request, 'index.html', {'quizzes':quizzes})


@login_required(login_url='dashboard:login')
def quiz_list(request):
    quizzes = models.Quiz.objects.all()
    return render(request, 'quiz/list.html', {'quizzes':quizzes})


@login_required(login_url='dashboard:login')
def quiz_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        quiz = models.Quiz.objects.create(name=name, author=request.user)
        return redirect('quiz_detail', quiz.code)
    
    return render(request, 'quiz/create.html')


@login_required(login_url='dashboard:login')
def quiz_detail(request, code):
    quiz = models.Quiz.objects.get(code=code)
    questions = models.Question.objects.filter(quiz=quiz).order_by('?')
    context = {
        'quiz':quiz,
        'questions':questions
    }
    return render(request, 'quiz/detail.html', context)


@login_required(login_url='dashboard:login')
def question_create(request, code):
    quiz = models.Quiz.objects.get(code=code)
    if request.method == 'POST':
        question = models.Question.objects.create(
            name=request.POST['question'],
            quiz=quiz
            )
        models.Option.objects.create(
            name = request.POST['correct_option'],
            question = question,
            is_correct = True
        )
        for option in request.POST.getlist('options'):
            models.Option.objects.create(
            name = option,
            question = question,
            is_correct = False
            )
        return redirect('question_detail',question.code)
    return render(request,'question/create.html', {'quiz':quiz})


@login_required(login_url='login')
def question_detail(request, code):
    question = models.Question.objects.get(code=code)
    options = models.Option.objects.filter(question=question)
    context = {
        'question':question,
        'options':options
    }
    return render(request, 'question/detail.html', context)


@login_required(login_url='login')
def question_delete(request, code):
    question = models.Question.objects.get(code=code)
    question.delete()
    return redirect('quiz_detail', question.quiz.code)


@login_required(login_url='login')
def question_update(request, code):
    question = models.Question.objects.get(code=code)
    print(request.POST)
    if request.method == 'POST':
        question.name = request.POST['name']
        question.save()
        return redirect('question_detail', question.code)


def answer_list(request, code):
    answers = models.Answer.objects.filter(quiz__code = code)
    context = {'answers':answers}
    return render(request, 'answer/list.html', context)


def answer_detail(request, code):
    answer = models.Answer.objects.get(code=code)
    details = models.AnswerDetail.objects.filter(answer=answer)
    correct = 0
    
    in_correct = 0
    for detatil in details:
        if detatil.is_correct:
            correct +=1
        else:
            in_correct +=1
    correct_percentage = int(correct * 100 / details.count())
    in_correct_percentage = 100 - correct_percentage

    context = {
        'answer':answer,
        'details':details,
        'correct':correct,
        'in_correct':in_correct,
        'total':details.count(),
        'correct_percentage':int(correct_percentage),
        'in_correct_percentage':in_correct_percentage,
    }

    return render(request, 'answer/detail.html', context)


def log_in(request):

    if request.method == 'POST':  
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('dashboard:index')
        else:
            messages.info(request, f'account done not exit plz sign in')
    return render(request, 'auth/login.html')


def register(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirmPassword')
            if password == confirm_password:
                models.User.objects.create_user(
                    username=username, 
                    password=password,
                    )
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('dashboard:index')
        except:
            return redirect('front:register')
    return render(request, 'auth/register.html')


def log_out(request):
    logout(request)
    messages.success(request, 'logout success')
    return redirect('dashboard:index')
