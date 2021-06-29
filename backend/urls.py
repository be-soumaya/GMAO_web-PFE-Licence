"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from gmaoApp.views import *  

from django.conf.urls.static import static  # newpdf
from django.conf import settings  # newpdf

urlpatterns = [
    path('home', home),
    path('', home , name='home'),
    path('about', about , name='about'),
    path('create', createView),
    path('Ajouter', Ajouter, name='Ajouter'),
    path('eq_index', index),
    path('delete/<int:pk>', delete, name='delete'),
    path('modifier/<int:pk>', modifier, name='modifier'),
    path('update/<int:pk>', update, name='update'),

    path('createPdr', createPdrView),
    path('AjouterPdr', AjouterPdr, name='AjouterPdr'),
    path('pdr_index', indexPdr),
    path('deletePdr/<int:pk>', deletePdr, name='deletePdr'),
    path('modifierPdr/<int:pk>', modifierPdr, name='modifierPdr'),
    path('updatePdr/<int:pk>', updatePdr, name='updatePdr'),
    path('updateQuaPdr/<int:pk>', updateQuaPdr, name='updateQuaPdr'),

    path('createInter', createInterView),
    path('inter_ajouter/', InterAjouter, name='InterAjouter'),
    path('getPDR/', getPDR, name='getPDR'),

    path('Rapport des équipements', EqdownloadPdf, name='Rapport des équipements'),  # newpdf
    path('Rapport des PDRs', PdrdownloadPdf, name='Rapport des PDRs'),  # newpdf
    path('Rapport des indicateurs', IndicdownloadPdf, name='Rapport des indicateurs'),  # newpdf
    path('Rapport de pareto', ParetodownloadPdf, name='Rapport de pareto'),  # newpdf

    path('planning_ajouter/', createPlanView, name='planning_ajouter'),  
    path('planning_save/', planning_ajouter, name='planning_save'),  
    path('type_json/', get_json_type_data, name='type_json'),  
    path('equipement_json/<str:type>/', get_json_equipement_data, name='get_json_equipement_data'),  
    path('intervalle_json/<str:eqId>/', get_json_intervalle_data, name='get_json_intervalle_data'),  
    path('planning_consulter/', PlanCalendar, name='planning_consulter'),  
    path('planning_calendar/', PlanningCalendar, name='planning_calendar'),  
    path('cell_position/', cell_position, name='cell_position'),  
    path('deletePlan/', deletePlan, name='deletePlan'),  
    path('index_plan/', indexPlan, name='index_plan'),  

    path('historique/', historiqueView, name='historique'),
    path('historique/deleteinter/<int:pk>', deleteinter, name='deleteinter'),
    path('pareto/', pareto, name='pareto'),
    path('intervention_json/<int:ref>/', get_json_intervention_data, name='get_json_intervention_data'),  
    path('intervention_mois_json/<str:mois>', get_json_intervention_mois_data, name='get_json_intervention_mois_data'),  
    path('intervention_filtre_json/<int:eqId>/<str:mois>', get_json_intervention_filtre_data, name='get_json_intervention_filtre_data'),  

    path('indicateurs/', indicateurs, name='indicateurs'),  

    # path('register/', registerPage, name="register"),
	path('login/', loginPage, name="login"),  
	path('logout/', logoutUser, name="logout"),
    path('admin/', admin.site.urls),
   


]  
 # newpdf
urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)