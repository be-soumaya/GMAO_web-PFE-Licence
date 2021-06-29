from django.forms import fields
from .models import *
from django import forms
from django.forms.widgets import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class InterventionForm(forms.ModelForm):
    class Meta:
        model = intervention
        fields = '__all__'
        widgets = {
            'type_intervention': Select(attrs={'class': 'form-control'}),
            'date_declaration_defaillance': DateInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_intervention': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'debut_intervention': TimeInput(attrs={'name': 'debut_intervention', 'class': 'form-control', 'type': 'time'}),
            'fin_intervention': TimeInput(attrs={'name': 'fin_intervention', 'class': 'form-control', 'type': 'time'}),
            'cause_intervention': TextInput(attrs={'class': 'form-control'}),
            'declare_par_defaillance': TextInput(attrs={'class': 'form-control' }),
            'actions_intervention': Textarea(attrs={'class': 'form-control'}),
            'pieces_utilisees': SelectMultiple(attrs={ 'name': 'pieces_utilisees','class': 'selectpicker border border-secondary rounded','id': 'pieces_selected','data-live-search':'true'}),
            'observation_intervention': Textarea(attrs={'class': 'form-control'}),
            'resultat_intervention': TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['eq_inter'].queryset = equipement.objects.order_by(
            'type_equipement')





class EquipementForm(forms.ModelForm):
    class Meta:
        model = equipement
        fields = '__all__'
        widgets = {
            'ref_equipement': TextInput(attrs={'class': 'form-control'}),
            'serie_equipement': TextInput(attrs={'class': 'form-control'}),
            'type_equipement': Select(attrs={'class': 'form-control'}),
            'emplacement_equipement': TextInput(attrs={'class': 'form-control'}),
            'designation_equipement': TextInput(attrs={'class': 'form-control'}),
            'client_equipement': TextInput(attrs={'class': 'form-control'}),
            'date_debut_fonctionnement_equipement': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ref_equipement'].queryset = Type_equipement.objects.order_by(
            'name')


class TypeForm(forms.ModelForm):
    class Meta:
        model = Type_equipement
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
        }

class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']