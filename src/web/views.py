from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from .forms import UploadFileForm
from .forms import TypeInTextForm
from django.views.decorators.csrf import csrf_protect
# from .forms import FileFieldForm
# from django.views.generic.edit import FormView

import requests
import logging

logger = logging.getLogger(__name__)



HSE_API_ROOT = "http://hse-api-web/"


# def save_user_text(text):
#     # with open( HSE_API_ROOT + 'user_text.txt', 'w') as fo:
#     with open('/opt/code/tmp/user_text.txt', 'w') as fo:
#         fo.write(text)
def web_index(request):
    return render(request, 'index.html',
                  context={})
# def web_index(request):
#     form = ProcessTextForm()
#     if request.method == 'POST':
#         form = ProcessTextForm(request.POST)
#         if form.is_valid():
#             # save_user_text(form.cleaned_data['text'])
#             ner = form.cleaned_data['ner']
#             term_extraction = form.cleaned_data['term_extraction']
#             text_classification = form.cleaned_data['text_classification']
#             readability = form.cleaned_data['readability']
#             methods = select_methods_string(ner, term_extraction,
#                                             text_classification, readability)
#
#             post_form_data(methods)
#     return render(request, 'index.html',
#             context={'form':form})



# def post_form_data(methods):
#     return requests.post(url=HSE_API_ROOT + 'process', data=methods)

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


def handle_uploaded_file(f, modules):

    files = {'file': f}
    url = HSE_API_ROOT + "upload"
    content = requests.post(url, files=files)
    file_id = content.json().get("file_id")

    if file_id:
        file_id = file_id[7:]
        url = HSE_API_ROOT + "process/" + file_id
        content = requests.post(url, data=modules)


    else:
        raise Exception(content.json())
    response = list(content.json().values())

    return response

# def web_process_file(request):

@csrf_protect
def web_upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            modules = list(filter(lambda t: t[0] in form.cleaned_data['modules'], form.fields['modules'].choices))
            modules = [f[0] for f in modules]
            modules = ','.join(modules)
            task_ids = handle_uploaded_file(request.FILES['file'], modules)
            task_ids = '&'.join(task_ids)
            return HttpResponseRedirect('main?task_id=' + str(task_ids))
    else:
        form = UploadFileForm()
    return render(request, 'main.html', {'form_upload': form})

def web_type_in(request):
    if request.method == 'POST':
        form = TypeInTextForm(request.POST, request.FILES)
        if form.is_valid():
            modules = list(filter(lambda t: t[0] in form.cleaned_data['modules'], form.fields['modules'].choices))
            modules = [f[0] for f in modules]
            modules = ','.join(modules)
            file = open('test.txt', 'rb+')
            subject = form.cleaned_data['text']
            subject = bytes(subject, encoding='utf-8')
            file.write(subject)
            # file.close()
            task_ids = handle_uploaded_file(file, modules)
            file.close()

            return HttpResponseRedirect('main?task_id=' + str(task_ids))
    else:
        form = TypeInTextForm()
    return render(request, 'main.html', {'form_text': form})