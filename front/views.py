import xlsxwriter
from django.http import HttpResponse
from django.shortcuts import render, redirect
from main import models


def index(request):
    quizzes = models.Quiz.objects.all()
    context = {
        'quizzes':quizzes
    }
    return render(request, 'front/index.html', context)



def quiz_detail(request, code):
  quiz = models.Quiz.objects.get(code=code)
  questions = models.Question.objects.filter(quiz=quiz)
  if request.method == 'POST':
    answer = models.Answer.objects.create(
        quiz=quiz,
        user_name=request.POST['user_name'],
        phone=request.POST.get('phone'),
        email=request.POST.get('email')
    )
    for key, value in request.POST.items():
      if key.startswith('question'):
        question_id = int(key[len('question['):-len(']')])
       
        models.AnswerDetail.objects.create(
            answer=answer,
            question_id=question_id,
            user_answer_id=int(value)
        )
  context = {
    'quiz': quiz,
    'questions': questions
  }
  return render(request, 'front/quiz-detail.html', context)



def quiz_results_to_excel(quiz, answers, filename):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    headers = ['Ism Familiya', 'Telefon raqam', 'Email', 'Jami savollar', 'To`g`ri javoblar', 'Noto`g`ri javoblar']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    for row, answer in enumerate(answers, start=1):
        worksheet.write(row, 0, answer.user_name)
        worksheet.write(row, 1, answer.phone)
        worksheet.write(row, 2, answer.email)
        total_questions = answer.answerdetail_set.count()
        worksheet.write(row, 3, total_questions)
        correct_answers = answer.answerdetail_set.filter(user_answer__is_correct=True).count()
        worksheet.write(row, 4, correct_answers)
        incorrect_answers = total_questions - correct_answers
        worksheet.write(row, 5, incorrect_answers)

    workbook.close()

    return filename


def quiz_result(request, code):
    quiz = models.Quiz.objects.get(code=code)
    answers = models.Answer.objects.filter(quiz=quiz)

    filename = 'quiz_results.xlsx'
    excel_file = quiz_results_to_excel(quiz, answers, filename)

    with open(excel_file, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
