# #coding:utf-8

import os
import requests
import arcpy

# Ce script permet de mettre à jour la base de données des aménagemenrs cyclables d'IDF à partir des données provenant de la BNAC...
# Documentaion des champs des données BNAC: https://schema.data.gouv.fr/etalab/schema-amenagements-cyclables/0.3.5/documentation.html

# Nom et chemin du dossier et de la nouvelle *.gdb :
chemin_dossier = r'\\zsfa\ZSF-APUR\SIG\12_BDPPC\BDPPCDIF\Publications_temporaires'
nom_dossier = 'AMENAGEMENT_CYCLABLE_NORMANDIE_25_10' # Nom du dossier
nom_gdb = "AMENAGEMENT_CYCLABLE_NORMANDIE_25_10.gdb" # Nom de la *.gdb

# Lien url provenant d'IDFM
lien = "https://www.data.gouv.fr/api/1/datasets/r/6c0bd130-6ad9-49fe-a16d-5a96bb7b0c5c"

# date de mise à jour de la bdd
date = 2025_10_01 

# Noms des variables :
normandie = "normandie"

liste_nom_couche = [normandie]

# Localisation des shapefiles d'entrees :
liste_chemin_couche = [r'P:\SIG\12_BDPPC\BDPPCDIF\Publications_temporaires\AMENAGEMENT_CYCLABLE_FRANCE\AM_OSM_FRANCE.gdb\normandie']

chemin_gdb = arcpy.env.workspace = chemin_dossier + "\\" + nom_dossier + "\\" + nom_gdb # Localisation du workspace
chemin_dossier_gdb = arcpy.env.workspace = chemin_dossier + "\\" + nom_dossier 
arcpy.env.overwriteOutput = True # Attention permet d'écraser fichier du même nom

###---------------------------------------------------------------------------------------------------------------------------------------------###

def creation_workspace(chemin_dossier, nom_dossier, nom_gdb, liste_nom_couche, liste_chemin_couche):
    arcpy.env.overwriteOutput = True
    
    # Création du dossier
    arcpy.AddMessage("Création d'un dossier...")
    dossier_path = arcpy.CreateFolder_management(chemin_dossier, nom_dossier)
    
    # Création de la gdb
    arcpy.AddMessage("Création d'une nouvelle *.gdb...")
    gdb_path = str(dossier_path) + "\\" + nom_gdb
    arcpy.CreateFileGDB_management(str(dossier_path), nom_gdb)

    # Copie des données
    arcpy.AddMessage("Import/copie des différentes couches...")
    for i in range(len(liste_nom_couche)):
        noms = liste_nom_couche[i]
        chemin = liste_chemin_couche[i]
        print("Copie dans la *.gdb de", noms)

        # Utiliser FeatureClassToFeatureClass pour shapefile → GDB
        arcpy.FeatureClassToFeatureClass_conversion(chemin, gdb_path, noms)

    arcpy.AddMessage("Fin de copie des données dans la nouvelle *.gdb...")

def import_geojson(lien, chemin_dossier_gdb, chemin_gdb, date):
    arcpy.AddMessage("Lancement de la mise à jour de la base de données cyclable...")

    # Téléchargement
    arcpy.AddMessage("Téléchargement du GeoJSON...")
    response = requests.get(lien)

    if response.status_code == 200:
        geojson_path = os.path.join(chemin_dossier_gdb, f"am_cyclable_BNAC_{date}.geojson")
        with open(geojson_path, 'wb') as file:
            file.write(response.content)
        arcpy.AddMessage("Téléchargement terminé.")

        # Conversion GeoJSON → GDB
        out_features = os.path.join(chemin_gdb, f"am_cyclable_BNAC_{date}")
        arcpy.AddMessage(f"Conversion du GeoJSON vers {out_features} ...")
        
        arcpy.conversion.JSONToFeatures(geojson_path, out_features,geometry_type="POLYLINE")

        arcpy.AddMessage("Mise à jour terminée.")
    else:
        arcpy.AddError(f"Erreur lors du téléchargement : {response.status_code}")

def projection_decoupage_couche(input,normandie,date):

    arcpy.AddMessage("Projection des nouvelles données cyclables...")
    arcpy.management.Project(
    in_dataset=input,
    out_dataset=f"amenagement_cyclable_france_{date}",
    out_coor_system='PROJCS["RGF_1993_Lambert_93",GEOGCS["GCS_RGF_1993",DATUM["D_RGF_1993",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",700000.0],PARAMETER["False_Northing",6600000.0],PARAMETER["Central_Meridian",3.0],PARAMETER["Standard_Parallel_1",44.0],PARAMETER["Standard_Parallel_2",49.0],PARAMETER["Latitude_Of_Origin",46.5],UNIT["Meter",1.0]]',
    transform_method="RGF_1993_To_WGS_1984_1",
    in_coor_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]',
    preserve_shape="NO_PRESERVE_SHAPE",
    max_deviation=None,
    vertical="NO_VERTICAL")

    # Intersection avec la limite normandie
    arcpy.analysis.Intersect(
        in_features=f"amenagement_cyclable_france_{date} #;{normandie} #",
        out_feature_class=f"amenagement_cyclable_{date}",
        join_attributes="ALL",
        cluster_tolerance=None,
        output_type="INPUT")

def orgnisation_champs(input):
    
    arcpy.AddMessage("Réorganisation des champs...")

    amenagement_cyclable = "amenagement_cyclable"
    arcpy.CopyFeatures_management(input,"amenagement_cyclable")
    
    arcpy.AlterField_management(amenagement_cyclable,"id_osm","id_osm","ID de l'objet dans OSM")
    arcpy.AlterField_management(amenagement_cyclable,"ame_d","ame_d","Aménagement cyclable côté droit")
    arcpy.AlterField_management(amenagement_cyclable,"ame_g","ame_g","Aménagement cyclable côté gauche")
    arcpy.AlterField_management(amenagement_cyclable,"revet_d","revet_d","Type de revêtement de la voie droite")
    arcpy.AlterField_management(amenagement_cyclable,"revet_g","revet_g","Type de revêtement de la voie gauche")
    arcpy.AlterField_management(amenagement_cyclable,"sens_d","sens_d","Sens de la voie droite")
    arcpy.AlterField_management(amenagement_cyclable,"sens_g","sens_g","Sens de la voie gauche")
    arcpy.AlterField_management(amenagement_cyclable,"statut_d","statut_d","Statut de la voie droite")
    arcpy.AlterField_management(amenagement_cyclable,"statut_g","statut_g","Statut de la voie gauche")
    arcpy.AlterField_management(amenagement_cyclable,"local_d","local_d","Emplacement de l’aménagement droit")
    arcpy.AlterField_management(amenagement_cyclable,"local_g","local_g","Emplacement de l’aménagement gauche")
    arcpy.AlterField_management(amenagement_cyclable,"largeur_d","largeur_d","Largeur de l’aménagement droit")
    arcpy.AlterField_management(amenagement_cyclable,"largeur_g","largeur_g","Largeur de l’aménagement gauche")
    arcpy.AlterField_management(amenagement_cyclable,"regime_d","regime_d","Nature de la voie droite")
    arcpy.AlterField_management(amenagement_cyclable,"regime_g","regime_g","Nature de la voie gauche")
    arcpy.AlterField_management(amenagement_cyclable,"trafic_vit","trafic_vit","Vitesse du trafic adjacent")
    arcpy.AlterField_management(amenagement_cyclable,"lumiere","lumiere","Aménagement éclairé")
    arcpy.AlterField_management(amenagement_cyclable,"d_service","d_service","Date de mise en oeuvre de l’aménagement")
    arcpy.AlterField_management(amenagement_cyclable,"access_ame","access_ame","Accessibilité des aménagements")
    arcpy.AlterField_management(amenagement_cyclable,"code_com_g","code_com_g","Code INSEE de la commune gauche")
    arcpy.AlterField_management(amenagement_cyclable,"code_com_d","code_com_d","Code INSEE de la commune droite")
    arcpy.AlterField_management(amenagement_cyclable,"date_maj","date_maj","Date de dernière mise à jour")
    # arcpy.AlterField_management(amenagement_cyclable,"reseau_loc","reseau_loc","Type de réseau structurant local")

    arcpy.management.DeleteField(
    in_table=amenagement_cyclable,
    drop_field="id_osm;code_com_d;ame_d;regime_d;sens_d;statut_d;revet_d;code_com_g;ame_g;regime_g;sens_g;statut_g;revet_g;access_ame;date_maj;trafic_vit;lumiere;local_d;local_g;largeur_d;largeur_g;d_service",
    method="KEEP_FIELDS")

    arcpy.AddMessage("Réorganisation des champs terminée...")

def categorisation_cyclable_c_acniv1_2(input):

    arcpy.AddMessage("Caclul sur le champ c_acniv1 à partir des champs ame_d, ame_g, sens_d et sens_g...")

    arcpy.AddMessage("Ajout des champs c_acniv1 et c_acniv2 ...")
    arcpy.AddField_management(input,"c_acniv1","TEXT",50,"","","Code cyclable APUR")
    arcpy.AddField_management(input,"c_acniv2","TEXT",50,"","","Code cyclable simplifié APUR")
        
    codeblock = """

def updateField(ame_d, ame_g, regime_d, regime_g, sens_d, sens_g):

    # ---- Niveau 10 ---- [Piste cyclable unidirectionnelle]
    if ame_g == "PISTE CYCLABLE" and sens_g == "UNIDIRECTIONNEL" and ame_d == "AUCUN":
        return 10
    if ame_g == "PISTE CYCLABLE" and sens_g == "UNIDIRECTIONNEL" and ame_d == "AUTRE":
        return 10
    if ame_d == "PISTE CYCLABLE" and sens_d == "UNIDIRECTIONNEL" and ame_g == "AUCUN":
        return 10
    if ame_d == "PISTE CYCLABLE" and sens_d == "UNIDIRECTIONNEL" and ame_g == "AUTRE":
        return 10     

    if ame_d == "PISTE CYCLABLE" and sens_d == "UNIDIRECTIONNEL" and ame_g == "BANDE CYCLABLE":
        return 10        
    if ame_d == "BANDE CYCLABLE" and sens_d == "UNIDIRECTIONNEL" and ame_g == "PISTE CYCLABLE":
        return 10
    if ame_d == "PISTE CYCLABLE" and sens_d == "UNIDIRECTIONNEL" and ame_g == "COULOIR BUS+VELO":
        return 10          
    if ame_d == "COULOIR BUS+VELO" and sens_d == "UNIDIRECTIONNEL" and ame_g == "PISTE CYCLABLE":
        return 10          

    # ---- Niveau 11 ---- [Piste cyclable bidirectionnelle]
    if ("PISTE CYCLABLE", "BIDIRECTIONNEL") in [(ame_g, sens_g), (ame_d, sens_d)]:
        return 11
    if ame_d == "PISTE CYCLABLE" and sens_d == "UNIDIRECTIONNEL" and ame_g == "PISTE CYCLABLE" and sens_g == "UNIDIRECTIONNEL":
        return 11
        
    # ---- Niveau 12 ---- [Bande cyclable bidirectionnelle]
    if ("BANDE CYCLABLE", "BIDIRECTIONNEL") in [(ame_g, sens_g), (ame_d, sens_d)]:
        return 12
    if ame_d == "BANDE CYCLABLE" and sens_d == "UNIDIRECTIONNEL" and ame_g == "BANDE CYCLABLE" and sens_g == "UNIDIRECTIONNEL":
        return 12
        
    # ---- Niveau 13 ---- [Bande cyclable unidirectionnelle]
    if ame_g == "BANDE CYCLABLE" and sens_g == "UNIDIRECTIONNEL" and ame_d in ("AUCUN","AUTRE","ACCOTEMENT REVETU HORS CVCB"):
        return 13
    if ame_d == "BANDE CYCLABLE" and sens_d == "UNIDIRECTIONNEL" and ame_g in ("AUCUN","AUTRE","ACCOTEMENT REVETU HORS CVCB"):
        return 13

    # ---- Niveau 14 ---- [Bande cyclable et voie de bus partagée]
    if ame_g == "BANDE CYCLABLE" and sens_g == "UNIDIRECTIONNEL" and ame_d == "COULOIR BUS+VELO" and sens_d == "UNIDIRECTIONNEL":
        return 14
    if ame_g == "COULOIR BUS+VELO" and sens_g == "UNIDIRECTIONNEL" and ame_d == "BANDE CYCLABLE" and sens_d == "UNIDIRECTIONNEL":
        return 14

    # ---- Niveau 16 ---- [Double sens cyclable]
    if ame_g in ("DOUBLE SENS CYCLABLE BANDE", "DOUBLE SENS CYCLABLE NON MATERIALISE", "DOUBLE SENS CYCLABLE PISTE") or ame_d in ("DOUBLE SENS CYCLABLE BANDE", "DOUBLE SENS CYCLABLE NON MATERIALISE", "DOUBLE SENS CYCLABLE PISTE"):
        return 16

    # ---- Niveau 15 ---- [Double sens cyclable et voie de bus partagée}
    if ame_g in ("DOUBLE SENS CYCLABLE BANDE", "DOUBLE SENS CYCLABLE NON MATERIALISE", "DOUBLE SENS CYCLABLE PISTE") and ame_d in ("COULOIR BUS+VELO"):
        return 15
    if ame_d in ("DOUBLE SENS CYCLABLE BANDE", "DOUBLE SENS CYCLABLE NON MATERIALISE", "DOUBLE SENS CYCLABLE PISTE") and ame_g in ("COULOIR BUS+VELO"):
        return 15

    # ---- Niveau 17 ---- [Voie de bus partagée unidirectionnelle]
    if ame_g == "COULOIR BUS+VELO" and sens_g == "UNIDIRECTIONNEL" and ame_d in ("AUCUN","AUTRE"):
        return 17
    if ame_d == "COULOIR BUS+VELO" and sens_d == "UNIDIRECTIONNEL" and ame_g in ("AUCUN","AUTRE"):
        return 17

    # ---- Niveau 18 ---- [Voie de bus partagée bidirectionnelle]
    if ame_g == "COULOIR BUS+VELO" and sens_g == "UNIDIRECTIONNEL" and ame_d == "COULOIR BUS+VELO" and sens_d == "UNIDIRECTIONNEL":
        return 18
    if ame_g == "COULOIR BUS+VELO" and sens_g == "BIDIRECTIONNEL" and ame_d == "AUCUN":
        return 18
    if ame_d == "COULOIR BUS+VELO" and sens_d == "BIDIRECTIONNEL" and ame_g == "AUCUN":
        return 18

    # ---- Niveau 19 ---- [Autre aménagement cyclable partagé]
    if ame_g == "AUTRE" and ame_d == "AUTRE":
        return 19
    if ame_g == "AUCUN" and ame_d == "AUTRE":
        return 19
    if ame_g == "AUTRE" and ame_d == "AUCUN":
        return 19
    if ame_g == "AMENAGEMENT MIXTE PIETON VELO HORS VOIE VERTE" and ame_d == "AMENAGEMENT MIXTE PIETON VELO HORS VOIE VERTE":
        return 19
    if ame_g == "AMENAGEMENT MIXTE PIETON VELO HORS VOIE VERTE" and ame_d == "AUCUN":
        return 19
    if ame_g == "AUCUN" and ame_d == "AMENAGEMENT MIXTE PIETON VELO HORS VOIE VERTE":
        return 19
    if ame_g == "GOULOTTE" and ame_d == "GOULOTTE":
        return 19
    if ame_g == "AUCUN" and ame_d == "GOULOTTE":
        return 19
    if ame_g == "GOULOTTE" and ame_d == "AUCUN":
        return 19

    if ame_g == "VELO RUE" and ame_d == "AUCUN":
        return 19
    if ame_g == "AUCUN" and ame_d == "VELO RUE":
        return 19
    if ame_g == "VELO RUE" and ame_d == "VELO RUE":
        return 19

    if ame_g == "CHAUSSEE A VOIE CENTRALE BANALISEE" and ame_d == "CHAUSSEE A VOIE CENTRALE BANALISEE":
        return 19

    if ame_g == "ACCOTEMENT REVETU HORS CVCB" and ame_d == "ACCOTEMENT REVETU HORS CVCB":
        return 19

    # ---- Niveau 20 ---- [Voie verte]
    if ame_g == "VOIE VERTE" or ame_d == "VOIE VERTE":
        return 20

    # Default value
    return 0

    """

    arcpy.CalculateField_management(input,"c_acniv1","updateField(!ame_d!, !ame_g!, !regime_d!, !regime_g!, !sens_d!, !sens_g!)","PYTHON3",codeblock)

    arcpy.AddMessage("Calcul sur le champ c_acniv2...")
    codeblock ="""
liste_1 = ['10','11','20']
liste_2 = ['12','13','14','17','18']
def updateField(c_acniv1):
    if c_acniv1 in liste_1 :
        return 1
    elif c_acniv1 in liste_2:
        return 2
    else:
        return None """
    arcpy.CalculateField_management(input,"c_acniv2","updateField(!c_acniv1!)","PYTHON3",codeblock)

    arcpy.AddMessage("Catégorisation terminée des champs c_acniv1 et c_acniv2...")

def stats_cyclable_normandie(input,date):

    arcpy.AddMessage("Import couche, normandie et accès vélo...")

    normandie_chemin = r"P:\SIG\12_BDPPC\BDPPCDIF\Publications_temporaires\AMENAGEMENT_CYCLABLE_FRANCE\AM_OSM_FRANCE.gdb\normandie"

    arcpy.conversion.FeatureClassToFeatureClass(normandie_chemin, chemin_gdb, "normandie")

   
    arcpy.env.workspace = chemin_gdb

    def remplacer_null(table,prefixe):

        # Récupérer tous les champs de la table
        fields = [f.name for f in arcpy.ListFields(table) if f.name.startswith(prefixe)]

        # Remplacer les NULL par 0 pour chaque champ
        for field in fields:
            expression = "Reclass(!{}!)".format(field)
            code_block = """
def Reclass(val):
    if val is None:
        return 0
    return val
"""
            arcpy.management.CalculateField(table, field, expression, "PYTHON3", code_block)

        print("Remplacement des NULL terminé !")


    arcpy.AddMessage("Statistique cyclable normandie...")

    arcpy.analysis.Intersect(
        in_features=f"{input} #;normandie #",
        out_feature_class=f"amenagement_cyclable_{date}_normandie",
        join_attributes="ALL",
        cluster_tolerance=None,
        output_type="INPUT")

    arcpy.analysis.Statistics(
        in_table=f"amenagement_cyclable_{date}_normandie",
        out_table="stats_normandie",
        statistics_fields="shape_Length SUM",
        case_field="l_nor;c_acniv1",
        concatenation_separator="")
    
    arcpy.management.PivotTable(
        in_table="stats_normandie",
        fields="l_nor",
        pivot_field="c_acniv1",
        value_field="SUM_shape_Length",
        out_table="stats_normandie_pivot")
    
    arcpy.management.CalculateField("stats_normandie_pivot", "voies_vertes", "(!F20!*2)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_normandie_pivot", "pistes_cyclables", "((!F11!*2)+!F10!)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_normandie_pivot", "amenagemens_cyclables_secu", "!voies_vertes!+!pistes_cyclables!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_normandie_pivot", "bandes_cyclables", "((!F12!*2)+!F13!)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_normandie_pivot", "double_sens_cyclable", "!F16!/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_normandie_pivot", "voie_bus_cyclables", "(!F14!+!F17!+(2*!F18!))/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_normandie_pivot", "amenagements_cyclables_partag", "!bandes_cyclables!+!double_sens_cyclable!+!voie_bus_cyclables!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_normandie_pivot", "total_amenagements_exi", "!amenagements_cyclables_partag!+!amenagemens_cyclables_secu!", "PYTHON3", "", "DOUBLE")

###---------------------------------------------------------------------------------------------------------------------------------------------###
arcpy.env.workspace = chemin_gdb

activation_creation_workspace = False
activation_import_geojson = False
activation_projection_decoupage_couche = False
activation_orgnisation_champs = False
activation_categorisation_cyclable_c_acniv1_2 = True
activation_stats_cyclable_normandie = True


# Création d'une *.gdb et import des données
if activation_creation_workspace:
    
    creation_workspace(chemin_dossier, nom_dossier, nom_gdb, liste_nom_couche, liste_chemin_couche)


# Import des nouvelles données cyclables en geojson
if activation_import_geojson:

    import_geojson(lien, chemin_dossier_gdb, chemin_gdb, date)


# Projection et découpage sur IDF des nouvelles données cyclables
if activation_projection_decoupage_couche:

    input = f"am_cyclable_BNAC_{date}"
    projection_decoupage_couche(input,normandie,date)


# Réorganisation des champs
if activation_orgnisation_champs:

    input = f"amenagement_cyclable_{date}"
    orgnisation_champs(input)


# Catégorisation des nouvelles données cyclables à partir des champs ame_d, ame_g, sens_d et sens_g
if activation_categorisation_cyclable_c_acniv1_2:

    input = f"amenagement_cyclable"
    categorisation_cyclable_c_acniv1_2(input)


# Calcul statistique sur les nouvelles données cyclables
if activation_stats_cyclable_normandie:

    input = "amenagement_cyclable"
    stats_cyclable_normandie(input,date)