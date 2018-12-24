from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django import forms

import requests
import logging

logger = logging.getLogger(__name__)



HSE_API_ROOT = "http://hse-api-web/"

def select_methods_string(ner, term_extraction, text_classification, readability):
    methods = []
    if ner == True:
        methods.append('ner')
    if term_extraction == True:
        methods.append('term')
    if text_classification == True:
        methods.append('topic')
    if readability == True:
        methods.append('rb')
    
    return ', '.join(methods)

def save_user_text(text):
    with open('/opt/code/web/tmp/user_text.txt', 'w') as fo:
        fo.write(text)

def web_index(request):
    form = ProcessTextForm()
    if request.method == 'POST':
        form = ProcessTextForm(request.POST)
        if form.is_valid():
            save_user_text(form.cleaned_data['text'])
            ner = form.cleaned_data['ner']
            term_extraction = form.cleaned_data['term_extraction']
            text_classification = form.cleaned_data['text_classification']
            readability = form.cleaned_data['readability']
            methods = select_methods_string(ner, term_extraction, 
                                            text_classification, readability)
            post_form_data(methods)
    return render(request, 'index.html', 
            context={'form':form})

def post_form_data(methods):
    return requests.post(url=HSE_API_ROOT + 'process', data=methods)

def web_about(request):
    return render(request, 'about.html',
                  context={})

def web_documentation(request):
    return render(request, 'documentation.html',
                  context={})

def web_contact(request):
    return render(request, 'contact.html',
                  context={})


def web_main(request):
    return render(request, 'main.html',
                  context={"status": request.GET.get('status')})


def web_status(request):
    task_id = request.GET.get('task_id')
    if task_id:
        url = HSE_API_ROOT + "status/" + task_id
        content = requests.get(url)
        result = content.json()
        if result.get('status') == 'SUCCESS':
            content = requests.get(HSE_API_ROOT + 'files/' + result.get('result', [""])[0])
            result['raw'] = content.content.decode('utf-8')
        return JsonResponse(result)
    return JsonResponse({"error": "No task id"})

class ProcessTextForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False)
    ner = forms.BooleanField(required=False)
    term_extraction = forms.BooleanField(required=False)
    text_classification = forms.BooleanField(required=False)
    readability = forms.BooleanField(required=False)

def handle_uploaded_file(f):
    files = {'file': f}
    url = HSE_API_ROOT + "upload"
    content = requests.post(url, files=files)
    file_id = content.json().get("file_id")

    if file_id:
        file_id = file_id[7:]
        url = HSE_API_ROOT + "process/" + file_id
        content = requests.get(url)

    else:
        return content.json().get('task_id')


class UploadFileForm(forms.Form):
    file = forms.FileField()



def web_upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            task_id = handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('main?task_id=' + task_id)
    else:
        form = UploadFileForm()
    return render(request, 'main.html', {'form': form})
