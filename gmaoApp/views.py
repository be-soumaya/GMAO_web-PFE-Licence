import json
from django.shortcuts import render, redirect
from django.urls.base import reverse_lazy
from .models import *
from .forms import *
from .filters import *
from .decorators import *
from django.contrib import messages
# Create your views here.
from django.contrib.auth.decorators import login_required  # new
from django.views.decorators.csrf import csrf_protect
from datetime import date, datetime, time, timedelta
from django.db.models import Sum  # new
from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic.list import ListView
# newpdf
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa


@csrf_protect
@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')

@login_required()
def about(request):
    return render(request, 'about2.html')

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('/home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.is_superuser = True
                instance.is_staff = True
                instance.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('login')

        context = {'form': form}
        return render(request, 'registration/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/home')
            else:
                messages.info(request, 'Le nom d\'utilisateur ou le mot de passe est incorrect')

        context = {}
        return render(request, 'registration/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')

# -----EQUIPEMENT VIEWS-----


@login_required
@allowed_users(allowed_roles=['admin'])
def createView(request):
    form = EquipementForm()

    return render(request, 'eq_ajouter.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['admin'])
def Ajouter(request):
    form = EquipementForm()
    if request.method == 'POST':
        form = EquipementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "un nouvel équipement a été ajouté avec succés")
    return redirect('/eq_index')


@login_required
@allowed_users(allowed_roles=['admin'])
def index(request):
    eq = equipement.objects.order_by('type_equipement')
    eqr = equipement.objects.all()
    Nbreq = equipement.objects.all().count()
    form = TypeForm()
    if request.method == 'POST':
        form = TypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "un nouvel type d'équipement a été ajouté avec succés")

    myFilter = EqFilter(request.GET, queryset=eq)
    eq = myFilter.qs
    Nbreq = myFilter.qs.count()

    context = {
        'eq': eq,
        'Nbreq': Nbreq,
        'form': form,
        'myFilter': myFilter,

    }
    return render(request, 'eq_index.html', context)
    return render(request, 'EqPdfReport.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def delete(request, pk):
    eq = equipement.objects.get(id=pk)
    eq.delete()
    messages.success(request, "L'équipement " +
                     eq.ref_equipement + " a été supprimé avec succés")
    return redirect('/eq_index')


@login_required
@allowed_users(allowed_roles=['admin'])
def modifier(request, pk):
    eq = equipement.objects.get(id=pk)
    ty = list(Type_equipement.objects.values())
    context = {
        'eq': eq,
        'ty': ty
    }
    return render(request, 'eq_modifier.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def update(request, pk):
    eq = equipement.objects.get(id=pk)
    eq.ref_equipement = request.POST.get('ref_equipement')
    eq.serie_equipement = request.POST.get('serie_equipement')
    eq.emplacement_equipement = request.POST.get('emplacement_equipement')
    eq.designation_equipement = request.POST.get('designation_equipement')
    eq.client_equipement = request.POST.get('client_equipement')
    eq.date_debut_fonctionnement_equipement = request.POST.get(
        'date_debut_fonctionnement_equipement')
    eq.save()
    messages.success(request, "L'équipement " +
                     eq.ref_equipement + " a été modifié avec succés")
    return redirect('/eq_index')
# -----FIN EQUIPEMENTS VIEWS------


# -----INTERVENTION VIEWS------
@login_required
@allowed_users(allowed_roles=['admin','techniciens'])
def createInterView(request):
    return render(request, 'inter_ajouter.html')


@login_required
@allowed_users(allowed_roles=['admin','techniciens'])
def getPDR(request):
    dict = json.loads(request.GET.get('dict', None)) 
    for i in dict :
        pdr = Pdr.objects.get(id=i)
        if  Pdr.objects.get(id=i).quantite_pdr > 0 :
            pdr.quantite_pdr=F('quantite_pdr') - int(dict[i])
            pdr.save(update_fields=['quantite_pdr'])
        else :
            pdr.quantite_pdr = 0
            pdr.save(update_fields=['quantite_pdr'])
        
    data = {}
    return JsonResponse(data)

@login_required
@allowed_users(allowed_roles=['admin','techniciens'])
def InterAjouter(request):
    form = InterventionForm()
    pdrData = {}
    pdr = Pdr.objects.all().values()
    for i in pdr  :
        pdrData[i['id']]=i['ref_pdr']
    if request.method == 'POST':
        form = InterventionForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            ref_equipement = request.POST.get('ref_equipement')
            type_eq = request.POST.get('type_eq')
            instance.eq_inter_id = equipement.objects.get(
                ref_equipement=ref_equipement).id
            fin = request.POST.get('fin_intervention')
            debut = request.POST.get('debut_intervention')
            FMT = '%H:%M'
            if datetime.strptime(fin, FMT) < datetime.strptime(debut, FMT) :
                res = int((datetime.strptime(fin, FMT) -
                      datetime.strptime(debut, FMT)).total_seconds()/60)+1440

            else : 
                res = int((datetime.strptime(fin, FMT) -
                      datetime.strptime(debut, FMT)).total_seconds()/60)
            instance.duree_intervention = res
            instance.type_inter = Type_equipement.objects.get(name=type_eq)
            instance.save()
 
            pieces = request.POST.getlist('pieces_utilisees')

            for i in pieces :
                instance.pieces_utilisees.add(i) 

                # pdr = Pdr.objects.get(id=i)
                # pdrQu=pdr.quantite_pdr
                # print(pdrQu)
                # if pdrQu > 0 :
                #     pdr.quantite_pdr=pdrQu-1 
                # else :
                #     pdr.quantite_pdr = 0
                # pdr.save()
            messages.success(
                request, "une intervention a été ajouté avec succés")
            
            return redirect('/inter_ajouter')
            
    return render(request, 'inter_ajouter.html', {'form': form,'pdrData':pdrData})


# -----FIN INTERVENTION VIEWS------


# -----PDR VIEWS-----
@login_required
@allowed_users(allowed_roles=['admin'])
def createPdrView(request):
    return render(request, 'pdr_ajouter.html')


@login_required
@allowed_users(allowed_roles=['admin'])
def AjouterPdr(request):
    pdr = Pdr()
    pdr.prix_pdr = 0
    pdr.article_pdr = request.POST.get('article_pdr')
    pdr.ref_pdr = request.POST.get('ref_pdr')
    pdr.designation_pdr = request.POST.get('designation_pdr')
    pdr.categorie_pdr = request.POST.get('categorie_pdr')
    pdr.quantite_pdr = request.POST.get('quantite_pdr')
    pdr.min_pdr = request.POST.get('min_pdr')
    if request.POST.get('prix_pdr') :
        pdr.prix_pdr = request.POST.get('prix_pdr')
    else :
        pdr.prix_pdr = 0

    pdr.emplacement_pdr = request.POST.get(
        'emplacement_pdr')
    pdr.fournisseur_pdr = request.POST.get(
        'fournisseur_pdr')
    pdr.contact_fournisseur_pdr = request.POST.get(
        'contact_fournisseur_pdr')
    pdr.save()
    messages.success(request, "une nouvelle pdr a été ajouté avec succés")
    return redirect('/pdr_index')


@login_required
@allowed_users(allowed_roles=['admin','techniciens'])
def indexPdr(request):
    pdrs = Pdr.objects.all()
    pdr = Pdr.objects.all().order_by('categorie_pdr')
    Nbrpdr = Pdr.objects.all().count()
    total = Pdr.objects.aggregate(total=Sum('prix_pdr'))['total']

    myFilter = PdrFilter(request.GET, queryset=pdr)
    pdr = myFilter.qs
    Nbrpdr = myFilter.qs.count()
    total = myFilter.qs.aggregate(total=Sum('prix_pdr'))['total']

    context = {
        'pdr': pdr,
        'Nbrpdr': Nbrpdr,
        'total': total,
        'myFilter': myFilter,
    }

    return render(request, 'pdr_index.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def deletePdr(request, pk):
    pdr = Pdr.objects.get(id=pk)
    pdr.delete()
    messages.success(request, "La PDR " +
                     pdr.ref_pdr + " a été supprimé avec succés")
    return redirect('/pdr_index')


@login_required
@allowed_users(allowed_roles=['admin'])
def modifierPdr(request, pk):
    pdr = Pdr.objects.get(id=pk)
    return render(request, 'pdr_modifier.html', {'pdr': pdr})


@login_required
@allowed_users(allowed_roles=['admin'])
def updatePdr(request, pk):
    pdr = Pdr.objects.get(id=pk)
    pdr.article_pdr = request.POST.get('article_pdr')
    pdr.ref_pdr = request.POST.get('ref_pdr')
    pdr.designation_pdr = request.POST.get('designation_pdr')
    pdr.categorie_pdr = request.POST.get('categorie_pdr')
    pdr.quantite_pdr = request.POST.get('quantite_pdr')
    pdr.min_pdr = request.POST.get('min_pdr')
    pdr.prix_pdr = request.POST.get('prix_pdr')
    pdr.emplacement_pdr = request.POST.get(
        'emplacement_pdr')
    pdr.fournisseur_pdr = request.POST.get(
        'fournisseur_pdr')
    pdr.contact_fournisseur_pdr = request.POST.get(
        'contact_fournisseur_pdr')
    pdr.save()
    messages.success(request, "La PDR  " +
                     pdr.ref_pdr + "a été modifié avec succés")
    return redirect('/pdr_index')


@login_required
@allowed_users(allowed_roles=['admin'])
def updateQuaPdr(request, pk):
    pdr = Pdr.objects.get(id=pk)
    pdr.quantite_pdr = request.POST.get('quantite_pdr')
    pdr.save()
    return redirect('/pdr_index')
# -----FIN PDR VIEWS------


# -----PDF VIEWS-----
@login_required
@allowed_users(allowed_roles=['admin'])
def EqdownloadPdf(request):
    eq = equipement.objects.order_by('type_equipement')
    eqr = equipement.objects.all()
    Nbreq = equipement.objects.all().count()
    template_path = 'EqPdfReport.html'
    context = {
        'eq': eq,
        'eqr': eqr,
        'Nbreq': Nbreq, }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="rapprt_equipements.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
@allowed_users(allowed_roles=['admin'])
def PdrdownloadPdf(request):
    pdr = Pdr.objects.order_by('categorie_pdr')
    Nbrpdr = Pdr.objects.all().count()
    pdrs = Pdr.objects.all()
    total = Pdr.objects.aggregate(total=Sum('prix_pdr'))['total']
    template_path = 'PdrPdfReport.html'
    context = {
        'pdr': pdr,
        'Nbrpdr': Nbrpdr,
        'pdrs': pdrs,
        'total': total,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="rapprt_des_PDRs.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
@allowed_users(allowed_roles=['admin'])
def IndicdownloadPdf(request):
    indicateur = intervention.objects.all().order_by('-duree_intervention')
    myFilter = IndicateurFilter(request.GET, queryset=indicateur)
    indicateur = myFilter.qs
    corr = myFilter.qs.filter(
        type_intervention='C').values('duree_intervention')
    prev = myFilter.qs.filter(
        type_intervention='P').values('duree_intervention')
    nbreq = equipement.objects.all().count()
    if not corr:
        totalcorr = 0
    else:
        totalcorr = corr.aggregate(totalcorr=Sum(
            'duree_intervention'))['totalcorr']/60
    if not prev:
        totalprev = 0
    else:
        totalprev = prev.aggregate(totalprev=Sum(
            'duree_intervention'))['totalprev']/60
    total = totalcorr + totalprev
    if total == 0 :
        temps_maintenance = 0
    else :
        temps_maintenance = (totalcorr/total) * 100
    nbrArretCorr = myFilter.qs.filter(type_intervention='C').count()
    if nbrArretCorr == 0 :
        mttr = 0 
    else :
        mttr = total/nbrArretCorr
    nbrFonc = nbreq * 24 * 26
    if nbrFonc == 0 :
        mtbf = 0
    else :
        mtbf = (1-(total/nbrFonc))*100
    template_path = 'IndicPdfReport.html'
    context = {
        'myFilter': myFilter,
        'totalcorr': totalcorr,
        'totalprev': totalprev,
        'total': total,
        'nbrArretCorr': nbrArretCorr,
        'nbrFonc': nbrFonc,
        'temps_maintenance': temps_maintenance,
        'mttr': mttr,
        'mtbf': mtbf,
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="rapprt_des_indicateurs.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
@allowed_users(allowed_roles=['admin'])
def ParetodownloadPdf(request):
    pdr = Pdr.objects.order_by('categorie_pdr')
    Nbrpdr = Pdr.objects.all().count()
    pdrs = Pdr.objects.all()
    total = Pdr.objects.aggregate(total=Sum('prix_pdr'))['total']
    template_path = 'ParetoPdfReport.html'
    context = {
        'pdr': pdr,
        'Nbrpdr': Nbrpdr,
        'pdrs': pdrs,
        'total': total,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="rapprt_des_PDRs.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
# -----FIN PDF VIEWS------


# -----PLANNING VIEWS------
@login_required
@allowed_users(allowed_roles=['admin'])
def createPlanView(request):
    qs = Type_equipement.objects.all()
    pl = PlanPreventive.objects.all()
    return render(request, 'planning_ajouter.html', {'qs': qs, 'pl': pl})


@login_required
@allowed_users(allowed_roles=['admin'])
def indexPlan(request):
    context = {}
    return render(request, 'index.html', context)


@login_required
def get_json_type_data(request):
    qs_val = list(Type_equipement.objects.values())
    return JsonResponse({'data': qs_val})


@login_required
def get_json_equipement_data(request, *args, **kwargs):
    selected_type = kwargs.get('type')
    obj_eqs = list(equipement.objects.filter(
        type_equipement__name=selected_type).values())
    return JsonResponse({'data': obj_eqs})


@login_required
def get_json_intervalle_data(request, *args, **kwargs):
    selected_eqId = kwargs.get('eqId')
    obj_eqs = list(PlanPreventive.objects.filter(
        intervalle_maintenance=selected_eqId).values())
    return JsonResponse({'data': obj_eqs})


@login_required
@allowed_users(allowed_roles=['admin'])
def planning_ajouter(request):
    plan = PlanPreventive()
    plan.intervalle_maintenance = request.POST.get('intervalle_maintenance')
    if request.POST.get('intervalle_maintenance') == 'Annuelle':
        plan.semaine_maintenance = request.POST.get(
            'semaine_maintenance_mensuel')
    elif request.POST.get('intervalle_maintenance') == 'Mensuelle':
        plan.semaine_maintenance = request.POST.get(
            'semaine_maintenance_mensuelM')
    elif request.POST.get('intervalle_maintenance') == 'Trimestrielle' or request.POST.get('intervalle_maintenance') == 'Semestrielle':
        plan.semaine_maintenance = request.POST.get(
            'semaine_maintenance_triETseme')

    if request.POST.get('intervalle_maintenance') == 'Trimestrielle' or request.POST.get('intervalle_maintenance') == 'Semestrielle':
        plan.premiere_mois_maintenance = request.POST.get(
            'premiere_mois_maintenance')
    elif request.POST.get('intervalle_maintenance') == 'Annuelle':
        plan.premiere_mois_maintenance = request.POST.get(
            'premiere_mois_maintenanceA')
    ref_equipement = request.POST.get('ref_equipement')
    plan.eq_inter_id = equipement.objects.get(ref_equipement=ref_equipement).id
    type_eq = request.POST.get('type_eq')
    plan.type_eq_id = Type_equipement.objects.get(name=type_eq).id
    plan.save()

    messages.success(request, "Le planning annuel a été crée avec succés")
    return redirect('/planning_ajouter')


@login_required
@allowed_users(allowed_roles=['admin'])
def cell_position(request):
    OneNumberWeeks = ['1','2','3','4','5','6','7','8','9']
    row = request.GET.get('row', None)
    col = request.GET.get('col', None)
    ids = request.GET.get('ids', None)
    yyyy = request.GET.get('yyyy', None)
    intervalle = request.GET.get('intervalle', None)
    etat_planning = request.GET.get('etat_planning', None)
    type_ids = equipement.objects.filter(id=ids).values('type_equipement_id')[0]['type_equipement_id']
    plan = PlanPreventive()
    
    plan.cell_position = [row,col]
    plan.eq_inter_id = ids
    plan.type_eq_id = type_ids
    plan.intervalle_maintenance = intervalle
    plan.etat_planning = etat_planning

    if col in OneNumberWeeks :
        plan.semaine_maintenance = yyyy+'-W0'+col
    else :
        plan.semaine_maintenance = yyyy+'-W'+col
    

    plan.save()

    data = {
    }
    return JsonResponse(data)

@login_required
@allowed_users(allowed_roles=['admin'])
def deletePlan(request):
    ids = request.GET.get('ids', None)
    row = request.GET.get('row', None)
    col = request.GET.get('col', None)
    plan = PlanPreventive.objects.filter(eq_inter_id = ids , cell_position=[row,col])
    if plan :
        plan.delete()
    return redirect('/planning_calendar')

@login_required
@allowed_users(allowed_roles=['admin','techniciens'])
def PlanningCalendar(request):
    pl = PlanPreventive.objects.all()
    qs = ""
    plan = PlanPreventive()
    cellsArray = []
    intervallessArray = []
    a=""
    year = datetime.now().year
    if request.method == "POST":
        if request.POST.get('forms') == 'formType':
            a = request.POST.get('type')
            qs = equipement.objects.filter(
                    type_equipement__name=a).values('id', 'ref_equipement')  
    cells = PlanPreventive.objects.filter(type_eq__name=a).values('cell_position')
    intervalles = PlanPreventive.objects.filter(type_eq__name=a).values('intervalle_maintenance')
    for i in cells:
        if i['cell_position'] :
            cellsArray.append(i['cell_position'])
        else :
            cellsArray.append([0,0])
    for i in intervalles:
        if i['intervalle_maintenance'] :
            intervallessArray.append(i['intervalle_maintenance'])
        else :
            intervallessArray.append('')
    context = {
        'pl': pl,
        'qs': qs,
        'a':a,
        'year':year,
        'cellsArray' : cellsArray,
        'intervallessArray' : intervallessArray,
    }
    return render(request, 'planning_calendar.html', context)


@login_required
@allowed_users(allowed_roles=['admin','techniciens'])
def PlanCalendar(request):
    context = {}
    plandic = []
    b = ''
    a = ""
    if request.method == "POST":
        a = request.POST['type']
        b = request.POST.get('semaine')

        qs = equipement.objects.filter(
            type_equipement__name=a).values('id', 'ref_equipement')
        u = 0
        for i in qs:
            plan = PlanPreventive.objects.filter(eq_inter_id=i['id'], semaine_maintenance=b).values()
            u += 1
            plandic.append(plan)

        for x in range(u):
            context[qs[x]['ref_equipement']] = plandic[x]

    else:
        context = {}

    return render(request, 'planning_index.html', {'context': context, 'plandic': plandic, 'b':b, 'a':a})


# -----FIN PLANNING VIEWS------


# ----- HISTORIQUE VIEWS------
@login_required
@allowed_users(allowed_roles=['admin','techniciens'])
def historiqueView(request):
    eq = equipement.objects.all()
    context = {
        'eq': eq
    }
    return render(request, 'historique.html', context)


@login_required
def get_json_intervention_data(request, *args, **kwargs):
    selected_ref = kwargs.get('ref')
    obj_ref = list(intervention.objects.filter(eq_inter__id=selected_ref).values().order_by(
        'duree_intervention', 'date_intervention__month', 'date_intervention__year'))
    pdr_inter_dict = {}

    for i in obj_ref :
        if intervention.pieces_utilisees.through.objects.filter(intervention_id=i['id']).exists() :
            pdr_inter = intervention.pieces_utilisees.through.objects.filter(intervention_id=i['id']).values('pdr_id')

            pdr_array = []
            for j in pdr_inter :
                Pdr_refs = Pdr.objects.filter(id=j['pdr_id']).values('ref_pdr')
                for k in Pdr_refs :
                    pdr_array.append(k['ref_pdr'])
                    pdr_inter_dict[i['id']]=pdr_array

    return JsonResponse({'data': obj_ref,'pdr_inter_dict':pdr_inter_dict})


@login_required
def get_json_intervention_mois_data(request, *args, **kwargs):
    selected_mois = kwargs.get('mois')
    obj_mois = list(intervention.objects.filter(date_intervention__month=selected_mois).values(
    ).order_by('-duree_intervention', 'date_intervention__month', 'date_intervention__year'))
    return JsonResponse({'data': obj_mois})


@login_required
def get_json_intervention_filtre_data(request, *args, **kwargs):
    selected_eqId = kwargs.get('eqId')
    selected_mois = kwargs.get('mois')

    ob = list(intervention.objects.filter(eq_inter__id=selected_eqId, date_intervention__month=selected_mois).values(
    ).distinct().order_by('-duree_intervention', 'date_intervention__month', 'date_intervention__year'))
    return JsonResponse({'ob': ob})


@login_required
@allowed_users(allowed_roles=['admin'])
def pareto(request):
    pareto = intervention.objects.all().order_by('-duree_intervention')
    myFilter = ParetoFilter(request.GET, queryset=pareto)
    pareto = myFilter.qs
    total = myFilter.qs.aggregate(total=Sum('duree_intervention'))['total']
    dur = myFilter.qs.values('duree_intervention')
    cause = myFilter.qs.values('cause_intervention')

    pourarray = []
    causearray = []
    dureearray = []
    for i in dur:
        pourc = (i['duree_intervention']/total)*100
        pourarray.append(pourc)
    for i in cause:
        if i['cause_intervention'] is None :
            causearray.append('')
        else :
            causearray.append(i)
    for i in dur:
        dureearray.append(i)

    context = {
        'myFilter': myFilter,
        'pareto': pareto,
        'total': total,
        'pourarray': pourarray,
        'dureearray': dureearray,
        'causearray': causearray,


    }
    return render(request, 'pareto2.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
def deleteinter(request, pk):
    inte = intervention.objects.get(id=pk)
    inte.delete()
    return redirect('/historique')
# -----FIN HISTORIQUE VIEWS------


# -----INDICATEURS VIEWS------
@login_required
@allowed_users(allowed_roles=['admin'])
def indicateurs(request):
    indicateur = intervention.objects.all().order_by('-duree_intervention')
    months = ['01', '02', '03', '04', '05',
              '06', '07', '08', '09', '10', '11', '12']
    totaltempsMoule = []
    totalcorrectiveMoule = []
    totalpreventiveMoule = []
    totaltempsMachine = []
    totalcorrectiveMachine = []
    totalpreventiveMachine = []
    tempsmaintenancemoule = []
    tempsmaintenancemachine = []

    mtbfmoule = []
    mtbfmachine = []

    mttrmooule = []
    mttrmachine = []
    nbrarretcorrmouleArray = []
    nbrarretcorrmachineArray = []
    year = datetime.now().year
    if request.method == "POST":
        year=request.POST.get('year_courbe')
    # TEMPS DE MAINTENANCE
    for i in months:
        CorrMoule = intervention.objects.filter(type_inter_id='1', type_intervention='C',
                                                date_intervention__month=i, date_intervention__year=year).values('duree_intervention')
        if not CorrMoule:
            totcormoule = 0
            totalcorrectiveMoule.append(0)
        else:
            totcormoule = CorrMoule.aggregate(totcormoule=Sum('duree_intervention'))[
                'totcormoule']/60
            totalcorrectiveMoule.append(totcormoule)

        PrevMoule = intervention.objects.filter(type_inter_id='1', type_intervention='P',
                                                date_intervention__month=i, date_intervention__year=year).values('duree_intervention')
 
        if not PrevMoule:
            totprevmoule = 0
            totalpreventiveMoule.append(0)

        else:
            totprevmoule = PrevMoule.aggregate(totprevmoule=Sum('duree_intervention'))[
                'totprevmoule']/60
            totalpreventiveMoule.append(totprevmoule)

        CorrMachine = intervention.objects.filter(
            type_inter_id='2', type_intervention='C', date_intervention__month=i, date_intervention__year=year).values('duree_intervention')
        if not CorrMachine:
            totcormachine = 0
            totalcorrectiveMachine.append(0)

        else:
            totcormachine = CorrMachine.aggregate(totcormachine=Sum('duree_intervention'))[
                'totcormachine']/60
            totalcorrectiveMachine.append(totcormachine)

        PrevMachine = intervention.objects.filter(
            type_inter_id='2', type_intervention='P', date_intervention__month=i, date_intervention__year=year).values('duree_intervention')
        if not PrevMachine:
            totprevmachine = 0
            totalpreventiveMachine.append(0)

        else:
            totprevmachine = PrevMachine.aggregate(
                totprevmachine=Sum('duree_intervention'))['totprevmachine']/60
            totalpreventiveMachine.append(totprevmachine)

    for i in range(12):
        tottemMoul = totalcorrectiveMoule[i] + totalpreventiveMoule[i]
        totaltempsMoule.append(tottemMoul)
        tottemMach = totalcorrectiveMachine[i] + totalpreventiveMachine[i]
        totaltempsMachine.append(tottemMach)

    for i in range(12):
        if totaltempsMoule[i] == 0:
            ttmmo = 0
            tempsmaintenancemoule.append(ttmmo)
        else:
            ttmmo = (totalcorrectiveMoule[i] / totaltempsMoule[i]) * 100
            tempsmaintenancemoule.append(ttmmo)
        if totaltempsMachine[i] == 0:
            ttmma = 0
            tempsmaintenancemachine.append(ttmma)

        else:
            ttmma = (totalcorrectiveMachine[i] / totaltempsMachine[i]) * 100
            tempsmaintenancemachine.append(ttmma)

    # MTTR
    
    for i in months:
        nbrarretcorrmoule = intervention.objects.filter(
            type_intervention='C', type_inter_id='1', date_intervention__month=i, date_intervention__year=year)
        nbrarretcorrmachine = intervention.objects.filter(
            type_intervention='C', type_inter_id='2', date_intervention__month=i, date_intervention__year=year)
        if not nbrarretcorrmoule:
            arretmoule = 0
            nbrarretcorrmouleArray.append(arretmoule)
        else:
            arretmoule = nbrarretcorrmoule.count()
            nbrarretcorrmouleArray.append(arretmoule)
        if not nbrarretcorrmachine:
            arretmachine = 0
            nbrarretcorrmachineArray.append(arretmachine)
        else:
            arretmachine = nbrarretcorrmachine.count()
            nbrarretcorrmachineArray.append(arretmachine)

    for i in range(12):
        if nbrarretcorrmouleArray[i] == 0:
            mttrmoule = 0
            mttrmooule.append(mttrmoule)
        else:
            mttrmoule = totalcorrectiveMoule[i]/nbrarretcorrmouleArray[i]
            mttrmooule.append(mttrmoule)

        if nbrarretcorrmachineArray[i] == 0:
            mttrmaachine = 0
            mttrmachine.append(mttrmaachine)
        else:
            mttrmaachine = totalcorrectiveMachine[i] / \
                nbrarretcorrmachineArray[i]
            mttrmachine.append(mttrmaachine)


    # MTBF
    
    nbreqmoule = equipement.objects.filter(type_equipement_id=1).count()
    nbreqmachine = equipement.objects.filter(type_equipement_id=2).count()
    nbrFoncmoule = nbreqmoule * 24 * 26
    nbrFoncmachine = nbreqmachine * 24 * 26
    for i in range(12):
        if totaltempsMoule[i] == 0:
            mtbfmoul = 0
            mtbfmoule.append(mtbfmoul)
        else:
            mtbfmoul = (1-(totaltempsMoule[i]/nbrFoncmoule))*100
            mtbfmoule.append(mtbfmoul)
        if totaltempsMachine[i] == 0:
            mtbfmach = 0
            mtbfmachine.append(mtbfmach)
        else:
            mtbfmach = (1-(totaltempsMachine[i]/nbrFoncmachine))*100
            mtbfmachine.append(mtbfmach)



    # Tableau
    myFilter = IndicateurFilter(request.GET, queryset=indicateur)
    indicateur = myFilter.qs
    corr = myFilter.qs.filter(
        type_intervention='C').values('duree_intervention')

    prev = myFilter.qs.filter(
        type_intervention='P').values('duree_intervention')

    if not corr:
        totalcorr = 0
    else:
        totalcorr = corr.aggregate(totalcorr=Sum(
            'duree_intervention'))['totalcorr']/60
    if not prev:
        totalprev = 0
    else:
        totalprev = prev.aggregate(totalprev=Sum(
            'duree_intervention'))['totalprev']/60

    total = totalcorr + totalprev

    if total == 0:
        temps_maintenance = 0
    else:
        temps_maintenance = (totalcorr/total) * 100

    nbrArretCorr = myFilter.qs.filter(type_intervention='C').count()

    if nbrArretCorr == 0:
        mttr = 0
    else:
        mttr = totalcorr/nbrArretCorr

    selectType = request.GET.get('type_inter', '')
    if selectType == '1':
        nbreq = equipement.objects.filter(type_equipement_id=1).count()
        objmttr = '< 8h'
        objtemps = '< 20%'
    elif selectType == '2':
        nbreq = equipement.objects.filter(type_equipement_id=2).count()
        objmttr = '< 4h'
        objtemps = '< 15%'
    else:
        nbreq = equipement.objects.all().count()
        objmttr = ''
        objtemps = ''
    nbrFonc = nbreq * 24 * 26
    if nbrFonc == 0 :
        mtbf = 0
    else :
        mtbf = (1-(total/nbrFonc))*100
    context = {
        'myFilter': myFilter,
        'totalcorr': totalcorr,
        'totalprev': totalprev,
        'nbrArretCorr': nbrArretCorr,
        'total': total,
        'objmttr': objmttr,
        'objtemps': objtemps,
        'nbreq': nbreq,
        'nbrFonc': nbrFonc,
        'temps_maintenance': temps_maintenance,
        'mttr': mttr,
        'mtbf': mtbf,
        'year': year,
        'tempsmaintenancemachine': tempsmaintenancemachine,
        'tempsmaintenancemoule': tempsmaintenancemoule,
        'mttrmooule': mttrmooule,
        'mttrmachine': mttrmachine,
        'mtbfmoule': mtbfmoule,
        'mtbfmachine': mtbfmachine,

    }
    return render(request, 'indicateur.html', context)


# -----FIN INDICATEURS VIEWS------
