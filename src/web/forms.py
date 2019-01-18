from django import forms


# class ProcessTextForm(forms.Form):
#     text = forms.CharField(widget=forms.Textarea, required=False, initial='Type your text here')
#     ner = forms.BooleanField(required=False)
#     term_extraction = forms.BooleanField(required=False)
#     text_classification = forms.BooleanField(required=False)
#     readability = forms.BooleanField(required=False)
MODULE_CHOICES = (
    ('ner', 'Имена ученых'),
    ('topic', 'Тематика'),
    ('rb', 'Ридабилити'),
    ('term', 'Термины'),
)

class UploadFileForm(forms.Form):
    file = forms.FileField()
    modules = forms.MultipleChoiceField(required=False,
                                                widget=forms.CheckboxSelectMultiple,
                                                choices=MODULE_CHOICES)

class TypeInTextForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False, initial='Введите текст', max_length=6000)
    modules = forms.MultipleChoiceField(required=False,
                                        widget=forms.CheckboxSelectMultiple,
                                        choices=MODULE_CHOICES)
    # if detect(text) != 'ru':
    #     raise forms.ValidationError("Did not send for 'help' in "
    #                                 "the subject despite CC'ing yourself.")
# class FileFieldForm(forms.Form):
#     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))