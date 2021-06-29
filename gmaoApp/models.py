from django.db import models
# Create your models here.
from datetime import datetime, timedelta
from django.contrib.postgres.fields import ArrayField

class Type_equipement(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True)
    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'type_equipements'

class equipement(models.Model):
    ref_equipement = models.CharField(max_length=50 ,unique=True)
    type_equipement= models.ForeignKey(Type_equipement, on_delete=models.CASCADE, null=True, blank=True)
    serie_equipement = models.CharField(max_length=30, blank=True, null=True)
    emplacement_equipement = models.CharField(
        max_length=50, blank=True, null=True)
    designation_equipement = models.CharField(
        max_length=500, blank=True, null=True)
    client_equipement = models.CharField(max_length=150, blank=True, null=True)
    date_debut_fonctionnement_equipement = models.DateField( blank=True, null=True)

    def __str__(self):
      return str(self.ref_equipement)


    class Meta:
        db_table = 'equipements'


        


class Pdr(models.Model):
    ref_pdr = models.CharField(max_length=50 ,unique=True , blank=True, null=True)
    designation_pdr = models.CharField(max_length=200, blank=True)
    categorie_pdr = models.CharField(max_length=100, blank=True, null=True)
    quantite_pdr = models.IntegerField(blank=True, null=True)
    min_pdr = models.IntegerField(blank=True, null=True)
    prix_pdr = models.DecimalField(max_digits=6, decimal_places=2,blank=True, null=True)
    emplacement_pdr = models.CharField(max_length=100,  blank=True)
    fournisseur_pdr = models.CharField(max_length=200, blank=True)
    contact_fournisseur_pdr = models.CharField(max_length=200, blank=True)

    
    def __str__(self):
      return str(self.ref_pdr)

    class Meta:
        db_table = 'Pdrs'



TYPE_INTERVENTION = (
    ('P', 'Préventive'),
    ('C', 'Corrective'),
)

class intervention(models.Model):
  
    type_intervention = models.CharField(max_length=1, choices=TYPE_INTERVENTION, null=True, blank=True)
    eq_inter = models.ForeignKey(equipement, on_delete=models.CASCADE, null=True, blank=True)
    type_inter = models.ForeignKey(Type_equipement, on_delete=models.CASCADE, null=True, blank=True)
    date_declaration_defaillance = models.DateTimeField(null=True, blank=True)
    date_intervention = models.DateField(null=True, blank=True)
    debut_intervention = models.TimeField(null=True, blank=True)
    fin_intervention = models.TimeField(null=True, blank=True)
    duree_intervention = models.IntegerField(null=True, blank=True)
    declare_par_defaillance = models.CharField(max_length=100, null=True, blank=True)
    cause_intervention= models.CharField(max_length=500, null=True, blank=True)
    actions_intervention = models.CharField(max_length=400, null=True, blank=True)
    pieces_utilisees = models.ManyToManyField(Pdr, blank=True)
    observation_intervention = models.CharField(max_length=500, null=True, blank=True)
    resultat_intervention = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'interventions'


ETAT_PLANNING = (
    ('P', 'Planifié'),
    ('R', 'Réalisé'),
)



class PlanPreventive(models.Model):
    eq_inter = models.ForeignKey(equipement, on_delete=models.CASCADE, null=True, blank=True)
    type_eq = models.ForeignKey(Type_equipement, on_delete=models.CASCADE, null=True, blank=True)
    intervalle_maintenance = models.CharField(max_length=50,  null=True, blank=True)
    semaine_maintenance = models.CharField(max_length=50,null=True, blank=True)
    premiere_mois_maintenance = models.CharField(max_length=30,null=True, blank=True)
    etat_planning = models.CharField(max_length=1, choices=ETAT_PLANNING, null=True, blank=True)
    cell_position = ArrayField(ArrayField(models.IntegerField(null=True, blank=True),null=True, blank=True),null=True, blank=True)
    class Meta:
        db_table = 'plans'
    


