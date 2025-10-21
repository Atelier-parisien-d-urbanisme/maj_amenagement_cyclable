# #coding:utf-8

from os import access
import os
from re import A
import arcpy
import numpy as np
import requests,zipfile
from io import BytesIO

# Ce script permet de mettre à jour la base de données cyclable IDF provenant de Iles-de-France Mobilités...

# Nom et chemin du dossier et de la nouvelle *.gdb :
chemin_dossier = r'\\zsfa\ZSF-APUR\SIG\12_BDPPC\BDPPCDIF\Publications_temporaires'
nom_dossier = 'MAJ_AMENAGEMENT_CYCLABLE_07_25' # Nom du dossier
nom_gdb = "MAJ_AMENAGEMENT_CYCLABLE_07_25.gdb" # Nom de la *.gdb

# Lien url provenant d'IDFM
lien = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/amenagements-velo-en-ile-de-france/exports/geojson?lang=fr&timezone=Europe%2FBerlin"

date = 2025 # date de mise à jour de la bdd

# Noms des variables :
pisteCyclable = "amenagement_cyclable"
commune = "commmune"

liste_nom_shp = [pisteCyclable,commune]

# Localisation des shapefiles d'entrees :
liste_chemins_shp = [r'\\zsfa\sig$\12_BDPPC\maj_pc\script\connexions_sde\diffusion.sde\apur.diffusion.cyclable\apur.diffusion.amenagement_cyclable',
r'\\zsfa\sig$\12_BDPPC\maj_pc\script\connexions_sde\diffusion.sde\apur.diffusion.limite_administrative\apur.diffusion.commune']


### CREATION D'UNE GDB ET IMPORT DES DONNEES ###
def creation_workspace(chemin_dossier,nom_dossier,nom_gdb,liste_nom_shp,liste_chemins_shp):
    arcpy.env.overwriteOutput = True
    arcpy.AddMessage("Creation d'un dossier...")
    arcpy.CreateFolder_management(chemin_dossier,nom_dossier)
    arcpy.AddMessage("Creation d'une nouvelle *.gdb...")
    cheminGdb = chemin_dossier + "\\" + nom_dossier
    arcpy.CreateFileGDB_management(cheminGdb,nom_gdb)

    arcpy.AddMessage("Import/copie des differentes couches...")
    for i in range(0,np.size(liste_nom_shp),1):
        noms = liste_nom_shp[i]
        chemin = liste_chemins_shp[i]
        print("Copie dans la *.gdb de ",noms)
        arcpy.Copy_management(chemin,cheminGdb+"\\"+nom_gdb+"\\"+noms)

    arcpy.AddMessage("Fin de copie des donnees dans la nouvelle *.gdb...")

# creation_workspace(chemin_dossier,nom_dossier,nom_gdb,liste_nom_shp,liste_chemins_shp)

chemin = arcpy.env.workspace = chemin_dossier + "\\" + nom_dossier + "\\" + nom_gdb # Localisation du workspace
chemin1 = arcpy.env.workspace = chemin_dossier + "\\" + nom_dossier 
arcpy.env.overwriteOutput = True # Attention permet d'écraser fichier du même nom


### TRAITEMENT ET MAJ DE LA BDD CYCLABLE ###
def maj_amenagement_cyclable(lien,chemin1,chemin,date):

    arcpy.AddMessage("Lancement de la mise à jour de la base de données cyclable...")

    arcpy.AddMessage("Telechargement de l'url...")
    response = requests.get(lien)

    # Vérifier si le téléchargement est réussi
    if response.status_code == 200:
         # Chemin complet pour sauvegarder le fichier
        output_path = os.path.join(chemin1, "am_geojson_idfm.geojson")

        # Sauvegarder le fichier GeoJSON
        with open(output_path, 'wb') as file:
            file.write(response.content)
    
    geojson_path = chemin1 + "\\" + "am_geojson_idfm.geojson"
    out_features = chemin + "\\" + "am_geojson_idfm"

    print(geojson_path)
    print(out_features)
    
    arcpy.conversion.JSONToFeatures(in_json_file=geojson_path,out_features=out_features,geometry_type="POLYLINE")

    arcpy.env.workspace = chemin
    listeBbddCyclable = arcpy.ListFeatureClasses()
    print(listeBbddCyclable)
    NouvelleBddCyclable = listeBbddCyclable[2]
    VieilleBddCyclable = listeBbddCyclable[0]
    print(NouvelleBddCyclable)
    print(VieilleBddCyclable)

    arcpy.AddMessage("Visulaliser les differents champs des tables avant traitement...")
    nomChampNouveau = [f.name for f in arcpy.ListFields(NouvelleBddCyclable)]
    print("Champs BDD Aménagements vélo en Île-de-France :")
    print(nomChampNouveau)
    print("Nombre de champs BDD Aménagements vélo en Île-de-France :",np.size(nomChampNouveau))

    osmId = []
    with arcpy.da.SearchCursor(NouvelleBddCyclable, "osm_id") as cursor:
        for row in cursor:
            osmId.append(row[0])
    print("Taille de la BDD Aménagements vélo en Île-de-France :",np.size(osmId))

    nomChampVieux = [f.name for f in arcpy.ListFields(VieilleBddCyclable)]
    print("Champs BDD APUR :")
    print(nomChampVieux)
    print("Nombre de champs BDD Aménagements vélo en Île-de-France :",np.size(nomChampVieux))

    osmId = []
    with arcpy.da.SearchCursor(VieilleBddCyclable, "osm_id") as cursor:
        for row in cursor:
            osmId.append(row[0])
    print("Taille de la BDD APUR :",np.size(osmId))

    arcpy.AddMessage("Troncature de la table APUR (vider les lignes)...")
    bddTruncate = "amenagement_cyclable_test_{}".format(date)
    arcpy.Copy_management(VieilleBddCyclable,bddTruncate)
    arcpy.TruncateTable_management(bddTruncate)

    VieilleBddCyclable1 = "amenagement_cyclable_test"
    arcpy.Copy_management(VieilleBddCyclable,VieilleBddCyclable1)

    arcpy.AddMessage("Reorganisation des champs (ajout, renomment) de la bdd Ile de France mobilites...")
    arcpy.AlterField_management(NouvelleBddCyclable,"OBJECTID","objectid","objectid")
    
    arcpy.AlterField_management(NouvelleBddCyclable,"nom_com","nom_com","Nom de la commune")
    arcpy.AlterField_management(NouvelleBddCyclable,"nom_voie","nom_voie","Nom de la voie")
    arcpy.AlterField_management(NouvelleBddCyclable,"insee_com","insee_com_orig")
    arcpy.AlterField_management(NouvelleBddCyclable,"osm_id","osm_id","ID de l'objet dans OSM")
    arcpy.AlterField_management(NouvelleBddCyclable,"ad","ad","Aménagement cyclable côté droit")
    arcpy.AlterField_management(NouvelleBddCyclable,"ag","ag","Aménagement cyclable côté gauche")
    arcpy.AlterField_management(NouvelleBddCyclable,"highway","highway","Type de voie")
    arcpy.AlterField_management(NouvelleBddCyclable,"longueur","longueur_1")
    arcpy.AlterField_management(NouvelleBddCyclable,"revetement","revetement","Type de revêtement de la voie")
    arcpy.AlterField_management(NouvelleBddCyclable,"panneaux","panneaux","Type de panneau présent sur l’aménagement")
    
    
    arcpy.management.AddField(NouvelleBddCyclable, "longueur", "LONG", None, None, None, "Longueur de la voie", "NULLABLE", "NON_REQUIRED", '')
    arcpy.CalculateField_management(NouvelleBddCyclable,"longueur","!longueur_1!","PYTHON3")
    
    arcpy.management.AddField(NouvelleBddCyclable, "insee_com", "LONG", None, None, None, "Code INSEE de la commune", "NULLABLE", "NON_REQUIRED", '')
    arcpy.CalculateField_management(NouvelleBddCyclable,"insee_com","!insee_com_orig!","PYTHON3")
    
    arcpy.AddField_management(NouvelleBddCyclable,"c_acniv1","TEXT",50,"","","Code cyclable APUR")
    arcpy.AddField_management(NouvelleBddCyclable,"c_acniv2","TEXT",50,"","","Code cyclable simplifié APUR")

    arcpy.AlterField_management(NouvelleBddCyclable,"petite_ech","petite_ech","Représentation petite échelle IDFM")
    arcpy.AlterField_management(NouvelleBddCyclable,"moyenn_ech","moyenn_ech","Représentation moyenne échelle IDFM")
    arcpy.DeleteField_management(NouvelleBddCyclable,"longueur_1")
    arcpy.DeleteField_management(NouvelleBddCyclable,"date_modif")
    arcpy.DeleteField_management(NouvelleBddCyclable,"insee_com_orig")
    arcpy.DeleteField_management(NouvelleBddCyclable,"notes")
    arcpy.management.DeleteField(NouvelleBddCyclable,drop_field="geo_point_2d;geo_shape",method="DELETE_FIELDS")
    
    arcpy.AddMessage("Append de la table APUR...")
    arcpy.Append_management(NouvelleBddCyclable, bddTruncate, schema_type="TEST", field_mapping="", subtype="") # Attention les champs des deux tables doivent etre les memes

    arcpy.AddMessage("Statistique sur les champs ad et ag de VieilleBddCyclable...")
    arcpy.Statistics_analysis(VieilleBddCyclable1, "stats_ac_niv1_old", statistics_fields="c_acniv1 FIRST;c_acniv1 LAST", case_field="ad;ag")

    arcpy.AddMessage("Caclul sur le champ c_acniv1 à partir de ag, ad et nv de l'ancienne bdd...")
    ## A MODIFIER TANT QUE c_acniv1_compare != c_acniv1 ###
    codeblock_old ="""
def updateField(ad,ag,nv):

    if ad == 'piste uni' and ag == '':
        return 10
    elif ad == '' and ag == 'piste uni':
        return 10        
    elif ad == 'DSC piste' and ag == '':
        return 10
    elif ad == '' and ag == 'DSC piste':
        return 10
    elif ad == 'piste trottoir uni' and ag == '':
        return 10
    elif ad == '' and ag == 'piste trottoir uni':
        return 10
    elif ad == 'piste uni' and ag == 'DSC':
        return 10
    elif ad == 'DSC' and ag == 'piste uni':
        return 10

    elif ad == 'piste uni' and ag == 'piste uni':
        return 11
    elif ad == '' and ag == 'piste bi':
        return 11
    elif ad == 'piste bi' and ag == '':
        return 11
    elif ad == 'bande uni' and ag == 'DSC piste':
        return 11
    elif ad == 'bande uni' and ag == 'piste uni':
        return 11
    elif ad == 'piste trottoir uni' and ag == 'piste trottoir uni':
        return 11
    elif ad == 'piste uni' and ag == 'bande uni':
        return 11
    elif ad == 'piste uni' and ag == 'DSC bande':
        return 11
    elif ad == 'piste uni' and ag == 'DSC piste':
        return 11
    elif ad == 'bande uni' and ag == 'piste uni':
        return 11
    elif ad == 'DSC bande' and ag == 'piste uni':
        return 11
    elif ad == 'DSC piste' and ag == 'piste uni':
        return 11

    elif ad == 'bande uni' and ag == 'DSC bande':
        return 12
    elif ad == 'DSC bande' and ag == 'bande uni':
        return 12
    elif ad == '' and ag == 'bande bi':
        return 12
    elif ad == 'bande bi' and ag == '':
        return 12        
    elif ad == 'DSC' and ag == 'bande bi':
        return 12
    elif ad == 'bande bi' and ag == 'DSC':
        return 12

    elif ad == 'bande uni' and ag == '':
        return 13
    elif ad == '' and ag == 'bande uni':
        return 13
    elif ad == 'DSC bande' and ag == '':
        return 13
    elif ad == '' and ag == 'DSC bande':
        return 13
    elif ad == 'bande uni' and ag == 'bande uni':
        return 13
    elif ad == 'bande uni' and ag == 'DSC':
        return 13
    elif ad == 'DSC' and ag == 'bande uni':
        return 13

    elif ad == 'voie bus uni' and ag == '':
        return 17
    elif ad == '' and ag == 'voie bus uni':
        return 17
    elif ad == '' and ag == 'voie bus uni':
        return 17
    elif ad == 'DSC' and ag == 'voie bus uni':
        return 17
    elif ad == 'voie bus uni' and ag == 'DSC':
        return 17

    elif ad == 'voie bus uni' and ag == 'bande uni':
        return 14
    elif ad == 'bande uni' and ag == 'voie bus uni':
        return 14
    elif ad == 'voie bus uni' and ag == 'piste uni':
        return 14
    elif ad == 'piste uni' and ag == 'voie bus uni':
        return 14
    elif ad == 'DSC bande' and ag == 'voie bus uni':
        return 14
    elif ad == 'voie bus uni' and ag == 'DSC bande':
        return 14
    elif ad == 'voie bus uni' and ag == 'DSC piste':
        return 14
    elif ad == 'DSC piste' and ag == 'voie bus uni':
        return 14

    elif ad == '' and ag == 'DSC':
        return 16
    elif ad == 'DSC' and ag == '':
        return 16
    elif ad == 'piste bi' and ag == 'DSC':
        return 16
    elif ad == 'DSC' and ag == 'piste bi':
        return 16
    elif ad == 'DSC bande' and ag == 'DSC':
        return 16
    elif ad == 'DSC' and ag == 'DSC bande':
        return 16

    elif ad == 'voie bus uni' and ag == 'voie bus uni':
        return 18

    elif ad == 'cheminement trottoir uni' or ag == 'cheminement trottoir uni':
        return 19
    elif ad == 'chemin service site propre uni' or ag == 'chemin service site propre uni':
        return 19
    elif ad == 'autre chemin velo uni' or ag == 'autre chemin velo uni':
        return 19
    elif ad == 'chemin dedie uni' or ag == 'chemin dedie uni':
        return 19

    elif ad == 'voie verte uni' or ag == 'voie verte uni':
        return 20

    elif nv == 'z30':
        return 16

    else: 
        return None """

    arcpy.AddMessage("Ajout de champ c_acniv1_compare et calcul sur l'ancienne bdd (faire verification de l'expression)...")
    arcpy.CalculateField_management(VieilleBddCyclable1,"c_acniv1_compare","updateField(!ad!,!ag!,!nv!)","PYTHON3",codeblock_old)
    arcpy.AssignDomainToField_management(VieilleBddCyclable1, "c_acniv1_compare", "c_acniv1")

    arcpy.AddMessage("Calcul du champ c_acniv1 sur la nouvelle bdd...")
    arcpy.CalculateField_management(bddTruncate,"c_acniv1","updateField(!ad!,!ag!,!nv!)","PYTHON3",codeblock_old)

    arcpy.AddMessage("Statistique sur les champs ad et ag de la nouvelle bdd cyclable...")
    arcpy.Statistics_analysis(bddTruncate, "stats_ac_niv1_new", statistics_fields="c_acniv1 FIRST;c_acniv1 LAST", case_field="ad;ag")

    arcpy.AddMessage("Regarder dans la table ac_niv1_new si il y a des nouvelles typologies dans les champs ad et ag de la nouvelle bdd cyclable...")

    ### A MODIFIER SI NOUVELLE TYPOLOGIES ###
    # Attention espace quand champ vide dans ag/ad
    codeblock_new ="""
def updateField(ad,ag,nv):

    if ad == 'piste uni' and ag == None:
        return 10
    elif ad == None and ag == 'piste uni':
        return 10        
    elif ad == 'DSC piste' and ag == None:
        return 10
    elif ad == None and ag == 'DSC piste':
        return 10
    elif ad == 'piste trottoir uni' and ag == None:
        return 10
    elif ad == None and ag == 'piste trottoir uni':
        return 10
    elif ad == 'piste uni' and ag == 'DSC':
        return 10
    elif ad == 'DSC' and ag == 'piste uni':
        return 10
        
    elif ad == 'piste uni' and ag == 'cheminement uni':
        return 10
    elif ad == 'cheminement uni' and ag == 'piste uni':
        return 10
    elif ad == 'cheminement uni' and ag == 'DSC piste':
        return 10
    elif ad == 'DSC piste' and ag == 'cheminement uni':
        return 10
    elif ad == 'DSC' and ag == 'cheminement uni':
        return 10
    elif ad == 'cheminement uni' and ag == 'DSC':
        return 10

    elif ad == 'piste uni' and ag == 'piste uni':
        return 11
    elif ad == None and ag == 'piste bi':
        return 11
    elif ad == 'piste bi' and ag == None:
        return 11
    elif ad == 'bande uni' and ag == 'DSC piste':
        return 11
    elif ad == 'bande uni' and ag == 'piste uni':
        return 11
    elif ad == 'piste trottoir uni' and ag == 'piste trottoir uni':
        return 11
    elif ad == 'piste uni' and ag == 'bande uni':
        return 11
    elif ad == 'piste uni' and ag == 'DSC bande':
        return 11
    elif ad == 'piste uni' and ag == 'DSC piste':
        return 11
    elif ad == 'bande uni' and ag == 'piste uni':
        return 11
    elif ad == 'DSC bande' and ag == 'piste uni':
        return 11
    elif ad == 'DSC piste' and ag == 'piste uni':
        return 11

    elif ad == 'bande uni' and ag == 'DSC bande':
        return 12
    elif ad == 'DSC bande' and ag == 'bande uni':
        return 12
    elif ad == None and ag == 'bande bi':
        return 12
    elif ad == 'bande bi' and ag == None:
        return 12        
    elif ad == 'DSC' and ag == 'bande bi':
        return 12
    elif ad == 'bande bi' and ag == 'DSC':
        return 12

    elif ad == 'chaucidou' and ag == 'chaucidou':
        return 12
    elif ad == 'bande uni' and ag == 'piste bi':
        return 12
    elif ad == 'piste bi' and ag == 'bande uni':
        return 12

    elif ad == 'bande uni' and ag == None:
        return 13
    elif ad == None and ag == 'bande uni':
        return 13
    elif ad == 'DSC bande' and ag == None:
        return 13
    elif ad == None and ag == 'DSC bande':
        return 13
    elif ad == 'bande uni' and ag == 'bande uni':
        return 13
    elif ad == 'bande uni' and ag == 'DSC':
        return 13
    elif ad == 'DSC' and ag == 'bande uni':
        return 13

    elif ad == 'bande uni' and ag == 'cheminement uni':
        return 13
    elif ad == 'cheminement uni' and ag == 'bande uni':
        return 13
    elif ad == 'DSC bande' and ag == 'cheminement uni':
        return 13
    elif ad == 'cheminement uni' and ag == 'DSC bande':
        return 13

    elif ad == 'voie bus uni' and ag == None:
        return 17
    elif ad == None and ag == 'voie bus uni':
        return 17
    elif ad == None and ag == 'voie bus uni':
        return 17
    elif ad == 'DSC' and ag == 'voie bus uni':
        return 17
    elif ad == 'voie bus uni' and ag == 'DSC':
        return 17

    elif ad == 'voie bus uni' and ag == 'cheminement uni':
        return 17
    elif ad == 'cheminement uni' and ag == 'voie bus uni':
        return 17

    elif ad == 'voie bus uni' and ag == 'bande uni':
        return 14
    elif ad == 'bande uni' and ag == 'voie bus uni':
        return 14
    elif ad == 'voie bus uni' and ag == 'piste uni':
        return 14
    elif ad == 'piste uni' and ag == 'voie bus uni':
        return 14
    elif ad == 'DSC bande' and ag == 'voie bus uni':
        return 14
    elif ad == 'voie bus uni' and ag == 'DSC bande':
        return 14
    elif ad == 'voie bus uni' and ag == 'DSC piste':
        return 14
    elif ad == 'DSC piste' and ag == 'voie bus uni':
        return 14

    elif ad == None and ag == 'DSC':
        return 16
    elif ad == 'DSC' and ag == None:
        return 16
    elif ad == 'piste bi' and ag == 'DSC':
        return 16
    elif ad == 'DSC' and ag == 'piste bi':
        return 16
    elif ad == 'DSC bande' and ag == 'DSC':
        return 16
    elif ad == 'DSC' and ag == 'DSC bande':
        return 16

    elif ad == 'voie bus uni' and ag == 'voie bus uni':
        return 18

    elif ad == 'cheminement trottoir uni' or ag == 'cheminement trottoir uni':
        return 19
    elif ad == 'chemin service site propre uni' or ag == 'chemin service site propre uni':
        return 19
    elif ad == 'autre chemin velo uni' or ag == 'autre chemin velo uni':
        return 19
    elif ad == 'chemin dedie uni' or ag == 'chemin dedie uni':
        return 19

    elif ad == 'voie verte uni' or ag == 'voie verte uni':
        return 20

    elif nv == 'z30':
        return 16
    
    elif nv == 'z20':
        return 19
    
    elif nv == 'rue pietonne':
        return 19
                    
    elif ad == 'goulotte' and ag == 'goulotte':
        return None
    elif ad == None and ag == 'goulotte':
        return None
    elif ad == 'goulotte' and ag == None:
        return None

    elif ad == 'cheminement uni' and ag == 'cheminement uni':
        return 19
    elif ad == 'cheminement uni' and ag == None:
        return 19
    elif ad == None and ag == 'cheminement uni':
        return 19

    else: 
        return None """

    bddCyclableMajTemp = "amenagement_cyclable_temp_{}".format(date)
    arcpy.Copy_management(bddTruncate,bddCyclableMajTemp)
    arcpy.AddMessage("Calcul et validation du champ c_acniv1 sur la nouvelle bdd avec nouvelle typologies...")
    arcpy.CalculateField_management(bddCyclableMajTemp,"c_acniv1","updateField(!ad!,!ag!,!nv!)","PYTHON3",codeblock_new)

    arcpy.AddMessage("Statistique sur les champs ad et ag de la nouvelle bdd cyclable modifier...")
    arcpy.Statistics_analysis(bddCyclableMajTemp, "stats_ac_niv1_new_2", statistics_fields="c_acniv1 FIRST;c_acniv1 LAST", case_field="ad;ag")

    arcpy.AddMessage("Calcul sur le champ nom_com...")
    arcpy.JoinField_management(bddCyclableMajTemp, "insee_com", commune, "c_coinsee", ["l_co"])
    arcpy.CalculateField_management(bddCyclableMajTemp,"nom_com","!l_co!","PYTHON3")
    arcpy.DeleteField_management(bddCyclableMajTemp,"l_co")
    arcpy.MakeFeatureLayer_management(bddCyclableMajTemp, "bdd_final_lyr")
    arcpy.management.CalculateField("bdd_final_lyr", "nom_com", "'Paris'", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    
    arcpy.AddMessage("Nettoyage des nulls sur le code apur cyclable...")
    arcpy.MakeFeatureLayer_management(bddCyclableMajTemp, "bdd_final_lyr")
    arcpy.SelectLayerByAttribute_management("bdd_final_lyr","NEW_SELECTION","c_acniv1 IS NOT NULL")
    bddCyclableMaj = "amenagement_cyclable_{}".format(date)
    arcpy.CopyFeatures_management("bdd_final_lyr",bddCyclableMaj)
    
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
    arcpy.CalculateField_management(bddCyclableMaj,"c_acniv2","updateField(!c_acniv1!)","PYTHON3",codeblock)
    
    arcpy.AddMessage("Asignation du domaine c_acniv2_s...")
    arcpy.AssignDomainToField_management(bddCyclableMaj, "c_acniv2", "c_acniv2_s")

    arcpy.AddMessage("Asignation du domaine c_acniv1...")
    arcpy.AssignDomainToField_management(bddCyclableMaj, "c_acniv1", "c_acniv1")
    
    arcpy.AddMessage("Traitement de la base de données cyclable terminée dans amenagement_cyclable_{}...".format(date))

    arcpy.AddMessage("Mise à jour de la base de données cyclable terminée dans amenagement_cyclable_{}...".format(date))

# maj_amenagement_cyclable(lien,chemin1,chemin,date)


### LISTER LES VALEURS D'UN CHAMP ET VOIR LES DIFFERENCES ###
def comparaison_bdd(VieilleBddCyclable,bddCyclableMaj):

    arcpy.AddMessage("Comparaison des donnees...")
    arcpy.env.workspace = chemin

    inputTable = [VieilleBddCyclable,bddCyclableMaj]
    field = ["ag","ad","nv"]

    # Return list all permutations of field in input feature class or table
    def getValueList (inputTable, field):

        valueList = [] # array to hold list of values collected
        valueSet = set() # set to hold values to test against to get list
        rows = arcpy.SearchCursor(inputTable) # create search cursor

        # iterate through table and collect unique values
        for row in rows:
            value = row.getValue(field)

            # add value if not already added and not current year
            if value not in valueSet:
                valueList.append(value)

            # add value to valueset for checking against in next iteration
            valueSet.add(value)

        # return value list
        # valueList.sort()
        return valueList

    ag = getValueList(inputTable[0],field[0])

    ad = getValueList(inputTable[0],field[1])

    print(ad)
    print(ag)

    diff = list(set(ad) - set(ag))
    print("Differences entre les deux tables old:",diff)

    ag_2022 = getValueList(inputTable[1],field[0])

    ad_2022 = getValueList(inputTable[1],field[1])

    print(ad_2022)
    print(ag_2022)

    diff_2022 = list(set(ag_2022) - set(ad_2022))
    print("Differences entre les deux tables new:",diff_2022)

    diff_table = list(set(ag_2022) - set(ag))
    print("Differences entre les deux tables odl/new",diff_table)

VieilleBddCyclable = "amenagement_cyclable"
bddCyclableMaj = "amenagement_cyclable_{}".format(date)
# comparaison_bdd(VieilleBddCyclable,bddCyclableMaj)


def stats_cyclable_mgp_epci(input):

    arcpy.AddMessage("Import couche mgp, epci et accès vélo...")
    
    arcpy.env.workspace = chemin

    mgp_chemin = r'\\zsfa\sig$\12_BDPPC\maj_pc\script\connexions_sde\utilisateur.sde\apur.diffusion.limite_administrative\apur.diffusion.mgp'
    epci_chemin = r'\\zsfa\sig$\12_BDPPC\maj_pc\script\connexions_sde\utilisateur.sde\apur.diffusion.limite_administrative\apur.diffusion.epci'
    acces_velo_chemin = r'\\zsfa\zsf-apur\PROJETS\AMENAGEMENTS_CYCLABLES_METROPOLE\0_DONNEES\Accessibilite_garesGPE\Accessibilite_garesGPE.gdb\Accessibilite_velo_800m_3km_surf'

    arcpy.conversion.FeatureClassToFeatureClass(mgp_chemin, chemin, "mgp")
    arcpy.conversion.FeatureClassToFeatureClass(epci_chemin, chemin, "epci")
    arcpy.conversion.FeatureClassToFeatureClass(acces_velo_chemin, chemin, "acces_velo")

    arcpy.AddMessage("Statistique cyclable acces_velo...")

    arcpy.analysis.Intersect(
        in_features=f"{input} #;acces_velo #",
        out_feature_class="amenagement_cyclable_2025_acces_velo",
        join_attributes="ALL",
        cluster_tolerance=None,
        output_type="INPUT")

    arcpy.analysis.Statistics(
        in_table="amenagement_cyclable_2025_acces_velo",
        out_table="stats_acces_velo",
        statistics_fields="shape_Length SUM",
        case_field="n_sq_st__tobreak;c_acniv1",
        concatenation_separator="")
    
    arcpy.management.PivotTable(
        in_table="stats_acces_velo",
        fields="n_sq_st__tobreak",
        pivot_field="c_acniv1",
        value_field="SUM_shape_Length",
        out_table="stats_acces_velo_pivot")
    
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

    table = "stats_acces_velo_pivot"
    prefixe = "F"  # Champs commençant par
    remplacer_null(table,prefixe)

    arcpy.management.CalculateField("stats_acces_velo_pivot", "voies_vertes", "(!F20!*2)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_acces_velo_pivot", "pistes_cyclables", "((!F11!*2)+!F10!)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_acces_velo_pivot", "amenagemens_cyclables_secu", "!voies_vertes!+!pistes_cyclables!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_acces_velo_pivot", "bandes_cyclables", "((!F12!*2)+!F13!)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_acces_velo_pivot", "double_sens_cyclable", "!F16!/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_acces_velo_pivot", "voie_bus_cyclables", "(!F14!+!F17!+(2*!F18!))/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_acces_velo_pivot", "amenagements_cyclables_partag", "!bandes_cyclables!+!double_sens_cyclable!+!voie_bus_cyclables!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_acces_velo_pivot", "total_amenagements_exi", "!amenagements_cyclables_partag!+!amenagemens_cyclables_secu!", "PYTHON3", "", "DOUBLE")

    arcpy.AddMessage("Statistique cyclable mgp...")

    arcpy.analysis.Intersect(
        in_features=f"{input} #;mgp #",
        out_feature_class="amenagement_cyclable_2025_mgp",
        join_attributes="ALL",
        cluster_tolerance=None,
        output_type="INPUT")

    arcpy.analysis.Statistics(
        in_table="amenagement_cyclable_2025_mgp",
        out_table="stats_mgp",
        statistics_fields="shape_Length SUM",
        case_field="lib;c_acniv1",
        concatenation_separator="")
    
    arcpy.management.PivotTable(
        in_table="stats_mgp",
        fields="lib",
        pivot_field="c_acniv1",
        value_field="SUM_shape_Length",
        out_table="stats_mgp_pivot")
    
    arcpy.management.CalculateField("stats_mgp_pivot", "voies_vertes", "(!F20!*2)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_mgp_pivot", "pistes_cyclables", "((!F11!*2)+!F10!)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_mgp_pivot", "amenagemens_cyclables_secu", "!voies_vertes!+!pistes_cyclables!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_mgp_pivot", "bandes_cyclables", "((!F12!*2)+!F13!)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_mgp_pivot", "double_sens_cyclable", "!F16!/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_mgp_pivot", "voie_bus_cyclables", "(!F14!+!F17!+(2*!F18!))/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_mgp_pivot", "amenagements_cyclables_partag", "!bandes_cyclables!+!double_sens_cyclable!+!voie_bus_cyclables!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_mgp_pivot", "total_amenagements_exi", "!amenagements_cyclables_partag!+!amenagemens_cyclables_secu!", "PYTHON3", "", "DOUBLE")

    arcpy.AddMessage("Statistique cyclable epci...")

    arcpy.analysis.Intersect(
        in_features=f"{input} #;epci #",
        out_feature_class="amenagement_cyclable_2025_epci",
        join_attributes="ALL",
        cluster_tolerance=None,
        output_type="INPUT")

    arcpy.analysis.Statistics(
        in_table="amenagement_cyclable_2025_epci",
        out_table="stats_epci",
        statistics_fields="shape_Length SUM",
        case_field="l_epci;c_acniv1",
        concatenation_separator="")
    
    arcpy.management.PivotTable(
        in_table="stats_epci",
        fields="l_epci",
        pivot_field="c_acniv1",
        value_field="SUM_shape_Length",
        out_table="stats_epci_pivot")

    table = "stats_epci_pivot"
    prefixe = "F"  # Champs commençant par
    remplacer_null(table,prefixe)

    arcpy.management.CalculateField("stats_epci_pivot", "voies_vertes", "(!F20!*2)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_epci_pivot", "pistes_cyclables", "((!F11!*2)+!F10!)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_epci_pivot", "amenagemens_cyclables_secu", "!voies_vertes!+!pistes_cyclables!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_epci_pivot", "bandes_cyclables", "((!F12!*2)+!F13!)/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_epci_pivot", "double_sens_cyclable", "!F16!/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_epci_pivot", "voie_bus_cyclables", "(!F14!+!F17!+(2*!F18!))/1000", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_epci_pivot", "amenagements_cyclables_partag", "!bandes_cyclables!+!double_sens_cyclable!+!voie_bus_cyclables!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("stats_epci_pivot", "total_amenagements_exi", "!amenagements_cyclables_partag!+!amenagemens_cyclables_secu!", "PYTHON3", "", "DOUBLE")

input = "amenagement_cyclable_{}".format(date)
stats_cyclable_mgp_epci(input)


### MAJ DE LA BDD CYCLABLE DANS DIFFUSION ###
def maj_bdd_diffusion(sde_diffusion,chemin):
    arcpy.AddMessage("Mise à jour de amenagement_cyclable dans diffusion...")
    arcpy.env.workspace = chemin
    bddCyclableMaj = "amenagement_cyclable_{}".format(date)
    bddCyclableDiffusionChemin = sde_diffusion + '/apur.diffusion.cyclable'
    bddCyclableDiffusion = sde_diffusion + '/apur.diffusion.cyclable/apur.diffusion.amenagement_cyclable'
    
    arcpy.UnregisterAsVersioned_management(bddCyclableDiffusionChemin,"NO_KEEP_EDIT","COMPRESS_DEFAULT")
    arcpy.AddMessage("Tronquer la table...")
    arcpy.TruncateTable_management(bddCyclableDiffusion)
    arcpy.AddMessage("Charger la table avec les nouvelles données...")
    arcpy.Append_management(bddCyclableMaj, bddCyclableDiffusion, "NO_TEST")
    arcpy.AddMessage("Versioner la table...")
    arcpy.RegisterAsVersioned_management(bddCyclableDiffusionChemin, "NO_EDITS_TO_BASE")

sde_diffusion = r'//zsfa/ZSF-APUR/SIG/12_BDPPC/maj_pc/script/connexions_sde/diffusion.sde'
# maj_bdd_diffusion(sde_diffusion,chemin)

