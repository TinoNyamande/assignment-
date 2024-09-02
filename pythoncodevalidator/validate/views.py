# my_app/views.py

from django.shortcuts import render
from django.http import HttpResponse
from .scriptValidator import ScriptValidator

def validate(request):
    # This view should render a form for file upload
    return render(request, 'validate.html')



def analyze_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file and file.name.endswith('.txt'):
            scriptValidator = ScriptValidator();
            errors = scriptValidator.validate(file)

            return render(request, 'results.html', {
                'errors': errors,
                'word_count': 'N/A',
                'line_count': 'N/A',
                'character_count': 'N/A',
            })
        else:
            return HttpResponse("Please upload a valid .txt file.")
    return HttpResponse("Invalid request method.")
