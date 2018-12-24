from django import forms

class ProcessTextForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False)
    ner = forms.BooleanField(required=False)
    term_extraction = forms.BooleanField(required=False)
    text_classification = forms.BooleanField(required=False)
    readability = forms.BooleanField(required=False)


class UploadFileForm(forms.Form):
    file = forms.FileField()