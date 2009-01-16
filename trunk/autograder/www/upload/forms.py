"""
<Program Name>
  forms.py

<Started>
  October, 2008

<Author>
  ivan@cs.washington.edu
  Ivan Beschastnikh

<Purpose>

<Usage>
  For more information on forms in django see:
  http://docs.djangoproject.com/en/dev/topics/forms/
"""
import django.forms as forms

class UploadAssignmentForm(forms.Form):
    """
    <Purpose>
    Generates a form to acquire vessels by the user
    <Side Effects>
    None
    <Example Use>
    GetVesselsForm()
    to generate a blank form
    GetVesselsForm(post_request)
    to generate a form from an existing POST request
    """
    # email
    email = forms.EmailField()
    # classcode
    class_code = forms.CharField(max_length=32,min_length=3,error_messages={'required': 'Please enter a class code'})

