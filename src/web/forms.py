from django import forms


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
    text = forms.CharField(widget=forms.Textarea(attrs={'rows':10, 'cols':60, 'placeholder':'Введите текст', 'class':'form-control'}), required=False, max_length=6000)
    modules = forms.MultipleChoiceField(required=False,
                                        widget=forms.CheckboxSelectMultiple,
                                        choices=MODULE_CHOICES)