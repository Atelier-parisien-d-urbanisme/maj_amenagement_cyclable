#coding:utf-8

import arcpy
import numpy as np

# Ce script permet de faire des statistiques sur les différents millésimes des aménagements cyclables en secteur NQPV... 

# Nom et chemin du dossier et de la nouvelle *.gdb :
cheminDossier = r'\\zsfa\ZSF-APUR\SIG\12_BDPPC\BDPPCDIF\Publications_temporaires'
nomDossier = 'STATS_AMENAGEMENT_CYCLABLE_NQPV_02_24'
nomGdb = "STATS_AMENAGEMENT_CYCLABLE_NQPV_02_24.gdb"

# Noms des variables :
pisteCyclable = "amenagement_cyclable"
commune = "commune"
nqpv = "secteurNqpv"

listeNomShp = [pisteCyclable,commune,nqpv]

# Localisation des shapefiles d'entrees :
listeCheminsShp = [r'P:\SIG\12_BDPPC\BDPPCDIF\Publications_temporaires\MAJ_AMENAGEMENT_CYCLABLE_02_24\MAJ_AMENAGEMENT_CYCLABLE_02_24.gdb\amenagement_cyclable_2024',
r'\\zsfa\ZSF-APUR\SIG\12_BDPPC\maj_pc\script\connexions_sde\utilisateur.sde\apur.diffusion.limite_administrative\apur.diffusion.commune',
r'\\zsfa\sig$\12_BDPPC\maj_pc\script\connexions_sde\utilisateur.sde\apur.diffusion.perimetre_politique_ville\apur.diffusion.geographie_prioritaire_2024']

### CREATION D'UNE GDB ET IMPORT DES DONNEES ###
def creationWorkspace(cheminDossier,nomDossier,nomGdb,listeNomShp,listeCheminsShp):
    arcpy.env.overwriteOutput = True
    arcpy.AddMessage("Creation d'un dossier...")
    arcpy.CreateFolder_management(cheminDossier,nomDossier)
    arcpy.AddMessage("Creation d'une nouvelle *.gdb...")
    cheminGdb = cheminDossier + "\\" + nomDossier
    arcpy.CreateFileGDB_management(cheminGdb,nomGdb)

    arcpy.AddMessage("Import/copie des differentes couches...")
    for i in range(0,np.size(listeNomShp),1):
        noms = listeNomShp[i]
        chemin = listeCheminsShp[i]
        print("Copie dans la *.gdb de ",noms)
        arcpy.Copy_management(chemin,cheminGdb+"\\"+nomGdb+"\\"+noms)

    arcpy.AddMessage("Fin de copie des donnees dans la nouvelle *.gdb...")

creationWorkspace(cheminDossier,nomDossier,nomGdb,listeNomShp,listeCheminsShp)

chemin = arcpy.env.workspace = cheminDossier + "\\" + nomDossier + "\\" + nomGdb # Localisation du workspace
arcpy.env.overwriteOutput = True # Attention permet d'écraser fichier du même nom

### TRAITEMENT STATISTIQUE DE LA BDD CYCLABLE DANS LES NQPV ###
def calculStatistiqueCyclableSimpleNqpv(pisteCyclable,commune,nqpv,champ):

    arcpy.AddMessage("Selections de l'ensemble pistes cyclables...")
    arcpy.MakeFeatureLayer_management(pisteCyclable, "pisteCyclable_lyr")
    arcpy.management.SelectLayerByAttribute("pisteCyclable_lyr", "NEW_SELECTION", "c_acniv1 IS NOT NULL", None)
    arcpy.CopyFeatures_management("pisteCyclable_lyr","pisteCyclable_sel_simple")

    arcpy.AddMessage("Récupération des identitées des secteurs NQPV...")
    arcpy.analysis.Identity("pisteCyclable_sel_simple", nqpv, "amenagement_cyclable_nqpv", "ONLY_FID", None, "NO_RELATIONSHIPS")
    
    arcpy.AddMessage("Récupération des nature de secteur par jointure...")
    arcpy.management.JoinField("amenagement_cyclable_nqpv", "FID_secteurNqpv", nqpv, "objectid", champ, "NOT_USE_FM", None)
   
    arcpy.AddMessage("Récupération des identitées des communes...")
    arcpy.analysis.Identity("amenagement_cyclable_nqpv", commune, "amenagement_cyclable_nqpv_commune", "ONLY_FID", None, "NO_RELATIONSHIPS")
    
    arcpy.AddMessage("Récupération des noms des communes par jointure...")
    arcpy.management.JoinField("amenagement_cyclable_nqpv_commune", "FID_commune", commune, "objectid", "l_co", "NOT_USE_FM", None)
    
    arcpy.AddMessage("Fusion sur l_co, c_type_pgp et somme des distances des tronçcons...")
    arcpy.management.Dissolve("amenagement_cyclable_nqpv_commune", "amenagement_cyclable_nqpv_commune_diss", f"l_co;{champ}", "shape_Length SUM", "MULTI_PART", "DISSOLVE_LINES", '')
    
    arcpy.AddMessage("Selections des NQPV sur Paris...")
    arcpy.MakeFeatureLayer_management("amenagement_cyclable_nqpv_commune_diss", "amenagement_cyclable_nqpv_commune_diss_lyr")
    arcpy.management.SelectLayerByAttribute("amenagement_cyclable_nqpv_commune_diss_lyr", "NEW_SELECTION", f"{champ} IS NOT NULL And l_co = 'Paris'", None)
    arcpy.CopyFeatures_management("amenagement_cyclable_nqpv_commune_diss_lyr","stats_amenagement_cyclable_nqpv_paris")
    
    arcpy.AddMessage("Fusion sur les communes afin d'avoir distance total...")
    arcpy.management.Dissolve("amenagement_cyclable_nqpv_commune_diss", "amenagement_cyclable_nqpv_commune_diss_somme", "l_co", "shape_Length SUM", "MULTI_PART", "DISSOLVE_LINES", '')
    
    arcpy.AddMessage("Selections des pistes sur Paris...")
    arcpy.MakeFeatureLayer_management("amenagement_cyclable_nqpv_commune_diss_somme", "amenagement_cyclable_nqpv_commune_diss_somme_lyr")
    arcpy.management.SelectLayerByAttribute("amenagement_cyclable_nqpv_commune_diss_somme_lyr", "NEW_SELECTION", "l_co = 'Paris'", None)
    arcpy.CopyFeatures_management("amenagement_cyclable_nqpv_commune_diss_somme_lyr","stats_amenagement_cyclable_total_paris")
    
    arcpy.AddMessage("Modfication des champs...")
    arcpy.AlterField_management("stats_amenagement_cyclable_total_paris","SUM_shape_Length","dist_t_cycl","Distance cyclable total (m)")
    arcpy.AlterField_management("stats_amenagement_cyclable_nqpv_paris","SUM_shape_Length","dist_nqpv_cycl","Distance cyclable nqpv (m)")
    
    arcpy.AddMessage("Traitement statistique de la base de données cyclable terminée...")

calculStatistiqueCyclableSimpleNqpv(pisteCyclable,commune,nqpv,champ = 'c_type_pgp')

def calculStatistiqueCyclableDoubleNqpv(pisteCyclable,commune,nqpv,champ):

    arcpy.AddMessage("Selections des pistes cyclables double sens...")
    arcpy.MakeFeatureLayer_management(pisteCyclable, "pisteCyclable_lyr")
    arcpy.management.SelectLayerByAttribute("pisteCyclable_lyr", "NEW_SELECTION", "c_acniv1 IN ('11','20','12','16','18')", None)
    arcpy.CopyFeatures_management("pisteCyclable_lyr","pisteCyclable_sel_double")

    arcpy.AddMessage("Récupération des identitées des secteurs NQPV...")
    arcpy.analysis.Identity("pisteCyclable_sel_double", nqpv, "amenagement_cyclable_nqpv_double", "ONLY_FID", None, "NO_RELATIONSHIPS")
    
    arcpy.AddMessage("Récupération des nature de secteur par jointure...")
    arcpy.management.JoinField("amenagement_cyclable_nqpv_double", "FID_secteurNqpv", nqpv, "objectid", champ, "NOT_USE_FM", None)
   
    arcpy.AddMessage("Récupération des identitées des communes...")
    arcpy.analysis.Identity("amenagement_cyclable_nqpv_double", commune, "amenagement_cyclable_nqpv_double_commune", "ONLY_FID", None, "NO_RELATIONSHIPS")
  
    arcpy.AddMessage("Récupération des noms des communes par jointure...")
    arcpy.management.JoinField("amenagement_cyclable_nqpv_double_commune", "FID_commune", commune, "objectid", "l_co", "NOT_USE_FM", None)
    
    arcpy.AddMessage("Fusion sur l_co, c_type_pgp et somme des distances des tronçcons...")
    arcpy.management.Dissolve("amenagement_cyclable_nqpv_double_commune", "amenagement_cyclable_nqpv_double_commune_diss", f"l_co;{champ}", "shape_Length SUM", "MULTI_PART", "DISSOLVE_LINES", '')
    
    arcpy.AddMessage("Selections des NQPV sur Paris...")
    arcpy.MakeFeatureLayer_management("amenagement_cyclable_nqpv_double_commune_diss", "amenagement_cyclable_nqpv_double_commune_diss_lyr")
    arcpy.management.SelectLayerByAttribute("amenagement_cyclable_nqpv_double_commune_diss_lyr", "NEW_SELECTION", f"{champ} IS NOT NULL And l_co = 'Paris'", None)
    arcpy.CopyFeatures_management("amenagement_cyclable_nqpv_double_commune_diss_lyr","stats_amenagement_cyclable_nqpv_double_paris")
    
    arcpy.AddMessage("Fusion sur les communes afin d'avoir distance total...")
    arcpy.management.Dissolve("amenagement_cyclable_nqpv_double_commune_diss", "amenagement_cyclable_nqpv_double_commune_diss_somme", "l_co", "shape_Length SUM", "MULTI_PART", "DISSOLVE_LINES", '')
    
    arcpy.AddMessage("Selections des pistes sur Paris...")
    arcpy.MakeFeatureLayer_management("amenagement_cyclable_nqpv_double_commune_diss_somme", "amenagement_cyclable_nqpv_double_commune_diss_somme_lyr")
    arcpy.management.SelectLayerByAttribute("amenagement_cyclable_nqpv_double_commune_diss_somme_lyr", "NEW_SELECTION", "l_co = 'Paris'", None)
    arcpy.CopyFeatures_management("amenagement_cyclable_nqpv_double_commune_diss_somme_lyr","stats_amenagement_cyclable_double_total_paris")
    
    arcpy.AddMessage("Modfication des champs...")
    arcpy.AlterField_management("stats_amenagement_cyclable_double_total_paris","SUM_shape_Length","dist_t_cycl","Distance cyclable total (m)")
    arcpy.AlterField_management("stats_amenagement_cyclable_nqpv_double_paris","SUM_shape_Length","dist_nqpv_cycl","Distance cyclable nqpv (m)")
    
    arcpy.AddMessage("Traitement statistique de la base de données cyclable terminée...")

calculStatistiqueCyclableDoubleNqpv(pisteCyclable,commune,nqpv,champ = 'c_type_pgp')


arcpy.CopyFeatures_management("stats_amenagement_cyclable_nqpv_double_paris","stats_amenagement_cyclable_nqpv_ds_paris")
arcpy.management.Append("stats_amenagement_cyclable_nqpv_paris", "stats_amenagement_cyclable_nqpv_ds_paris", "TEST", None, '', '')
arcpy.management.Dissolve("stats_amenagement_cyclable_nqpv_ds_paris", "stats_amenagement_cyclable_nqpv_ds_paris_diss", ";l_co", "dist_nqpv_cycl SUM", "MULTI_PART", "DISSOLVE_LINES", '')





# arcpy.AddMessage("Selections commune Paris...")
# arcpy.MakeFeatureLayer_management(commune, "commune_lyr")
# arcpy.management.SelectLayerByAttribute("commune_lyr", "NEW_SELECTION", "l_co = 'Paris'", None)
# arcpy.CopyFeatures_management("commune_lyr","paris")

# arcpy.analysis.Intersect(
# in_features="amenagement_cyclable_nqpv_double #;paris #",
# out_feature_class="amenagement_cyclable_nqpv_double_commune",
# join_attributes="ALL",
# cluster_tolerance=None,
# output_type="INPUT")