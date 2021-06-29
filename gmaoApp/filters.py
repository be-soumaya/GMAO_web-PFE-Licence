from django.db.models import fields
import django_filters
from django_filters import DateFilter
from .models import *
from django.forms.widgets import *
from django.db.models import F

class PdrFilter(django_filters.FilterSet):
    
    category = (
    ('', ''),
    ('machine', 'machine'),
    ('moule', 'moule'),
    ('peripherique', 'peripherique'),
    )
    quantity = (
    ('', ''),
    ('inf', 'stock actuel < stock minimal'),
    ('sup', 'stock actuel > stock minimal'),
    ('equal', 'stock actuel = stock minimal'),
    ('empty', 'stock actuel = 0'),
    )

    ref_pdr = django_filters.CharFilter(lookup_expr='icontains',widget=TextInput(attrs={'class': 'form-control'}))
    categorie_pdr = django_filters.CharFilter(widget=Select(attrs={'class': 'form-control'},choices=category))
    emplacement_pdr = django_filters.CharFilter(lookup_expr='icontains',widget=TextInput(attrs={'class': 'form-control'}))
    quantite_pdr = django_filters.CharFilter(widget=NumberInput(attrs={'class': 'form-control'}))
    quantite_select = django_filters.CharFilter(widget=Select(attrs={'class': 'form-control'},choices=quantity ),method='filtre_quantity')
    fournisseur_pdr = django_filters.CharFilter(lookup_expr='icontains',widget=TextInput(attrs={'class': 'form-control'}))
    
    def filtre_quantity(self,queryset ,name, value):
        if value == 'inf' :
            return queryset.filter(quantite_pdr__lt=F('min_pdr'))
        elif value == 'sup':
            return queryset.filter(quantite_pdr__gt=F('min_pdr'))
        elif value == 'equal' :
            return queryset.filter(quantite_pdr__exact=F('min_pdr'))
        elif value == 'empty' :
            return queryset.filter(quantite_pdr__exact=0)



    class Meta:
        model = Pdr
        fields = '__all__'
 


class EqFilter(django_filters.FilterSet):
    

    ref_equipement = django_filters.CharFilter(lookup_expr='icontains',widget=TextInput(attrs={'class': 'form-control'}))
    type_equipement = django_filters.ModelChoiceFilter(queryset=Type_equipement.objects.all(),widget=Select(attrs={'class': 'form-control'}))
    emplacement_equipement = django_filters.CharFilter(lookup_expr='icontains',widget=TextInput(attrs={'class': 'form-control'}))
    


    class Meta:
        model = equipement
        fields = '__all__'
 


class ParetoFilter(django_filters.FilterSet):
    
    type_inter = django_filters.ModelChoiceFilter(queryset=Type_equipement.objects.all(),widget=Select(attrs={'class': 'form-control'}))
    date_intervention = django_filters.CharFilter(lookup_expr='icontains',widget=DateInput(attrs={'class': 'form-control', 'type': 'month'}))
    


    class Meta:
        model = intervention
        fields = '__all__'
 
 

class IndicateurFilter(django_filters.FilterSet):
    
    type_inter = django_filters.ModelChoiceFilter(queryset=Type_equipement.objects.exclude(name='Périphérique'),widget=Select(attrs={'class': 'form-control','name':'selctType'}))
    date_intervention = django_filters.CharFilter(lookup_expr='icontains',widget=DateInput(attrs={'class': 'form-control', 'type': 'month'}))
    
    class Meta:
        model = intervention
        fields = '__all__'
 