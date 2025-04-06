# multi_tab/views.py
import random
from django.shortcuts import render, redirect
from django.views import View
from .models import QuizResult

class HomeView(View):
    template_name = 'multi_tab/home.html'
    
    def get(self, request):
        return render(request, self.template_name)

class NameInputView(View):
    template_name = 'multi_tab/name_input.html'
    
    def get(self, request, test_type):
        return render(request, self.template_name, {'test_type': test_type})
    
    def post(self, request, test_type):
        username = request.POST.get('username', '').strip()
        if not username:
            return render(request, self.template_name, {
                'test_type': test_type,
                'error': 'Пожалуйста, введите ваше имя'
            })
        
        request.session['username'] = username
        return redirect(test_type)

class SquaresView(View):
    template_name = 'multi_tab/squares.html'
    
    def get(self, request):
        if 'username' not in request.session:
            return redirect('name_input', test_type='squares')
        
        numbers = random.sample(range(1, 16), 10)
        questions = [{
            'number': n,
            'question': f"{n}²",
            'answer': n * n
        } for n in numbers]
        
        request.session['questions'] = questions
        request.session['operation_type'] = 'squares'
        request.session['current_question'] = 0
        request.session['attempts_left'] = 2
        request.session['score'] = 0
        request.session['user_answers'] = []
        
        return render(request, self.template_name, {
            'question': questions[0],
            'question_number': 1,
            'total_questions': 10,
            'username': request.session['username']
        })

    def post(self, request):
        return self.handle_quiz_post(request)

class MultiplicationView(View):
    template_name = 'multi_tab/multiplication.html'
    
    def get(self, request):
        if 'username' not in request.session:
            return redirect('name_input', test_type='multiplication')
        
        questions = []
        for _ in range(10):
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            questions.append({
                'a': a,
                'b': b,
                'question': f"{a} × {b}",
                'answer': a * b
            })
        
        request.session['questions'] = questions
        request.session['operation_type'] = 'multiplication'
        request.session['current_question'] = 0
        request.session['attempts_left'] = 2
        request.session['score'] = 0
        request.session['user_answers'] = []
        
        return render(request, self.template_name, {
            'question': questions[0],
            'question_number': 1,
            'total_questions': 10,
            'username': request.session['username']
        })

    def post(self, request):
        return self.handle_quiz_post(request)

class DivisionView(View):
    template_name = 'multi_tab/division.html'
    
    def get(self, request):
        if 'username' not in request.session:
            return redirect('name_input', test_type='division')
        
        questions = []
        for _ in range(10):
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            product = a * b
            questions.append({
                'dividend': product,
                'divisor': a,
                'question': f"{product} ÷ {a}",
                'answer': b
            })
        
        request.session['questions'] = questions
        request.session['operation_type'] = 'division'
        request.session['current_question'] = 0
        request.session['attempts_left'] = 2
        request.session['score'] = 0
        request.session['user_answers'] = []
        
        return render(request, self.template_name, {
            'question': questions[0],
            'question_number': 1,
            'total_questions': 10,
            'username': request.session['username']
        })

    def post(self, request):
        return self.handle_quiz_post(request)

class QuizMixin:
    def handle_quiz_post(self, request):
        user_answer = int(request.POST.get('answer', 0))
        current_question_idx = request.session.get('current_question', 0)
        questions = request.session.get('questions', [])
        attempts_left = request.session.get('attempts_left', 2)
        
        if current_question_idx >= len(questions):
            return redirect('results')
        
        current_question = questions[current_question_idx]
        correct_answer = current_question['answer']
        is_correct = user_answer == correct_answer
        
        user_answers = request.session.get('user_answers', [])
        user_answers.append({
            'question': current_question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'attempts': 2 - attempts_left + 1
        })
        request.session['user_answers'] = user_answers
        
        QuizResult.objects.create(
            username=request.session.get('username', 'Anonymous'),
            operation_type=request.session.get('operation_type'),
            question=current_question['question'],
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            attempts=2 - attempts_left + 1
        )
        
        self.save_to_file(request, current_question, user_answer, correct_answer, is_correct)
        
        if is_correct or attempts_left <= 1:
            request.session['current_question'] = current_question_idx + 1
            request.session['attempts_left'] = 2
            
            if is_correct:
                request.session['score'] = request.session.get('score', 0) + 1
            
            if current_question_idx + 1 >= len(questions):
                return redirect('results')
            else:
                next_question = questions[current_question_idx + 1]
                return render(request, self.template_name, {
                    'question': next_question,
                    'question_number': current_question_idx + 2,
                    'total_questions': 10,
                    'username': request.session['username']
                })
        else:
            request.session['attempts_left'] = attempts_left - 1
            return render(request, self.template_name, {
                'question': current_question,
                'question_number': current_question_idx + 1,
                'total_questions': 10,
                'error': 'Неправильный ответ. Попробуйте еще раз.',
                'attempts_left': attempts_left - 1,
                'username': request.session['username']
            })
    
    def save_to_file(self, request, question, user_answer, correct_answer, is_correct):
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        operation = request.session.get('operation_type', 'unknown')
        username = request.session.get('username', 'Anonymous')
        result_line = (f"{timestamp} - {username} - {operation} - {question['question']} = {user_answer} "
                      f"(correct: {correct_answer}) - {'Correct' if is_correct else 'Incorrect'}\n")
        
        with open('quiz_results.txt', 'a', encoding='utf-8') as f:
            f.write(result_line)

class ResultsView(View):
    template_name = 'multi_tab/results.html'
    
    def get(self, request):
        user_answers = request.session.get('user_answers', [])
        score = request.session.get('score', 0)
        username = request.session.get('username', 'Гость')
        
        # Получаем общую статистику по всем пользователям
        all_results = QuizResult.objects.all().order_by('-created_at')[:50]
        
        # Если нет результатов вообще
        if not all_results and not user_answers:
            return render(request, self.template_name)
        
        # Получаем результаты текущего пользователя
        user_results = QuizResult.objects.filter(username=username).order_by('-created_at')
        
        # Читаем историю из файла
        try:
            with open('quiz_results.txt', 'r', encoding='utf-8') as f:
                history = f.readlines()
        except FileNotFoundError:
            history = []
        
        return render(request, self.template_name, {
            'user_answers': user_answers,
            'score': score,
            'total_questions': len(user_answers),
            'history': history,
            'all_results': all_results,
            'user_results': user_results,
            'username': username
        })
    
# Добавляем миксин к классам представлений
MultiplicationView.handle_quiz_post = QuizMixin.handle_quiz_post
MultiplicationView.save_to_file = QuizMixin.save_to_file
DivisionView.handle_quiz_post = QuizMixin.handle_quiz_post
DivisionView.save_to_file = QuizMixin.save_to_file
SquaresView.handle_quiz_post = QuizMixin.handle_quiz_post
SquaresView.save_to_file = QuizMixin.save_to_file