from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from .forms import UploadFileForm
from .forms import TypeInTextForm
from django.views.decorators.csrf import csrf_protect
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO
# from .forms import FileFieldForm
# from django.views.generic.edit import FormView
from templatesite import settings
import requests
import logging
import re
import json
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger(__name__)



HSE_API_ROOT = "http://hse-api-web/"


def web_index(request):
    return render(request, 'index.html',
                  context={})


def web_about(request):
    return render(request, 'about.html',
                  context={})

def web_research(request):
    return render(request, 'research.html',
                  context={})

def web_documentation(request):
    return render(request, 'documentation.html',
                  context={})

def web_contact(request):
    return render(request, 'contact.html',
                  context={})


def web_main(request):
    return render(request, 'main.html',
                  context={})


def generate_template_objects(data):
    modules = [''.join(list(data[i].keys())) for i in range(len(data))]
    preresult = []
    for i in range(len(data)):
        preresult.append(list(data[i][''.join(list(data[i].keys()))].items()))

    final = []
    for i, l in zip(modules, preresult):
        for j in l:
            final.append(('file', j[0]))
            final.append((i, j[1]))
    headers = ['ner', 'topic', 'rb', 'term']
    return stack_structure(final, headers)


def stack_structure(final, keys):
    objects = []
    file_task_pairs = [[final[2*i], final[2*i+1]] for i in range(int(len(final)/2))]
    files = list(set([pair[0][1] for pair in file_task_pairs]))
    for file in files:
        obj = {}
        obj['file'] = file
        for key in keys:
            obj[key] = '\t'
        file_tasks = [pair[1] for pair in file_task_pairs if pair[0][1] == file]
        for task in file_tasks:
            obj[task[0]] = task[1]
        objects.append(obj)
    return objects

def find_module(obj): # чтобы найти названия модулей
    regex = re.compile(r'(?<=processed\/)([a-z]+)(?=_)')
    return re.search(regex, obj.get('result', [""])[0])[0]


def parse_json(obj): # чтобы собрать словарь из названий файлов и самих строк
    result_str = obj.get('raw')
    result_strs = result_str.split('\n')
    pattern_name = re.compile(r'\w+\.\w+(?=\t)')
    pattern_str = re.compile(r'(?<=\t).+')
    file_names = [re.search(pattern_name, raw)[0] for raw in result_strs]  # здесь все имена файлов
    results_only = [re.search(pattern_str, raw)[0] for raw in result_strs]  # здесь результаты-строки
    return dict(zip(file_names, results_only))

# это функция, принимающая список джейсонов с js и создающая новый с нужными объектами
@csrf_exempt
def web_parser(request):
    if request.method == 'POST' and request.is_ajax():
        # body_unicode = request.body
        # logger.debug(body_unicode)
        body_unicode = request.body.decode('utf-8') # можно без декода
        logger.debug(body_unicode)
        body = json.loads(body_unicode)
        logger.debug(body)
        lst_of_jsons = body["all_data"]
        logger.debug(lst_of_jsons)
        raw_names = lst_of_jsons[0].get('raw')  #нам нужно получить все имена файлов
        lst_names = raw_names.split('\n')
        pattern = re.compile(r'\w+\.\w+(?=\t)')  # берем начало строк
        file_names = [re.match(pattern, name)[0] for name in lst_names]  # здесь все имена файлов

        full_lst = []
        for obj in lst_of_jsons:
            if find_module(obj) == 'ner':
                ner = parse_json(obj)
                header_ner = {'ner': ner}
                full_lst.append(header_ner)
            elif find_module(obj) == 'topic':
                topic = parse_json(obj)
                header_topic = {'topic': topic}
                full_lst.append(header_topic)
            elif find_module(obj) == 'rb':
                rb = parse_json(obj)
                header_rb = {'rb': rb}
                full_lst.append(header_rb)
            else:
                term = parse_json(obj)
                header_term = {'term': term}
                full_lst.append(header_term)

        final_list = generate_template_objects(full_lst)
        return JsonResponse({'api_result': final_list})
    else:
        return JsonResponse({"error": "No data"})



# context={"status": request.GET.get('status')}

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
    url = HSE_API_ROOT + "upload"
    content = requests.post(url, files=f)
    find_file_id = content.json()
    file_ids = list()
    for num in range(len(find_file_id)):
        file_id = find_file_id[str(num)]['file_id']
        file_ids.append(file_id)

    if file_ids:
        file_ids = [file_id[7:] for file_id in file_ids]
        file_ids = ",".join(file_ids)
        url = HSE_API_ROOT + "process/" + file_ids
        content = requests.post(url, data=modules)


    else:
        raise Exception(content.json())
    response = list(content.json().values())

    return response


def delete_temp_files(path_lst):
    '''fuction to clean data storage after sending files to api'''

    for path in path_lst:
        if default_storage.exists(path):
            default_storage.delete(path)


def handle_text(modules):
    files = {'file[]': open(settings.MEDIA_ROOT + 'temporary.txt', 'rb')}
    url = HSE_API_ROOT + "upload"
    content = requests.post(url, files=files)
    find_file_id = content.json()
    file_id = find_file_id['0']['file_id']

    if file_id:
        file_id = file_id[7:]
        url = HSE_API_ROOT + "process/" + file_id
        content = requests.post(url, data=modules)


    else:
        raise Exception(content.json())
    response = list(content.json().values())

    return response

@csrf_protect
def web_upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            modules = list(filter(lambda t: t[0] in form.cleaned_data['modules'], form.fields['modules'].choices))
            modules = [f[0] for f in modules]
            modules = ','.join(modules)
            files = request.FILES.getlist('file')
            filenames = [file.name for file in files]
            [default_storage.save(file.name, ContentFile(file.read())) for file in files]
            multiple_files = [('file[]', open(settings.MEDIA_ROOT +
                                              filename, 'rb')) for filename in filenames]
            task_ids = handle_uploaded_file(multiple_files, modules)
            path_lst_temp_files = [str(settings.MEDIA_ROOT + filename) for filename in filenames]
            delete_temp_files(path_lst_temp_files)
            task_ids = ','.join(task_ids)
            return HttpResponseRedirect('main?task_id=' + str(task_ids))
    else:
        form = UploadFileForm()
    return render(request, 'main.html', {'form_upload': form})

@csrf_protect
def web_type_in(request):
    if request.method == 'POST':
        form = TypeInTextForm(request.POST, request.FILES)
        if form.is_valid():
            modules = list(filter(lambda t: t[0] in form.cleaned_data['modules'], form.fields['modules'].choices))
            modules = [f[0] for f in modules]
            modules = ','.join(modules)
            file = open(settings.MEDIA_ROOT + 'temporary.txt', 'wb')
            myfile = File(file)
            subject = form.cleaned_data['text']
            subject = bytes(subject, encoding='utf-8')
            myfile.write(subject)
            myfile.close()
            file.close()
            task_ids = handle_text(modules)
            task_ids = ','.join(task_ids)
            return HttpResponseRedirect('main?task_id=' + str(task_ids))
    else:
        form = TypeInTextForm()
    return render(request, 'type_in.html', {'form_text': form})