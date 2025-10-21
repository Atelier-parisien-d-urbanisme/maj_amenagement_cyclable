# #coding:utf-8

import arcpy

# Ce script permet de mettre à jour la base de données cyclable Normandie provenant de OSM...

def traitement_bdd_normandie(input):

    arcpy.env.workspace = r'P:\SIG\12_BDPPC\BDPPCDIF\Publications_temporaires\AMENAGEMENT_CYCLABLE_FRANCE\AM_OSM_FRANCE.gdb'


    arcpy.management.Project(
        in_dataset="AM_OSM_FRANCE_20240901",
        out_dataset="AM_OSM_FRANCE_20240901_proj",
        out_coor_system='PROJCS["RGF_1993_Lambert_93",GEOGCS["GCS_RGF_1993",DATUM["D_RGF_1993",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",700000.0],PARAMETER["False_Northing",6600000.0],PARAMETER["Central_Meridian",3.0],PARAMETER["Standard_Parallel_1",44.0],PARAMETER["Standard_Parallel_2",49.0],PARAMETER["Latitude_Of_Origin",46.5],UNIT["Meter",1.0]]',
        transform_method="RGF_1993_To_WGS_1984_1",
        in_coor_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]',
        preserve_shape="NO_PRESERVE_SHAPE",
        max_deviation=None,
        vertical="NO_VERTICAL"
    )

    arcpy.analysis.Intersect(
        in_features="AM_OSM_FRANCE_20240901_proj #;normandie #",
        out_feature_class="AM_OSM_2024_Normandie",
        join_attributes="ALL",
        cluster_tolerance=None,
        output_type="INPUT"
    )


    # Chemin vers votre table ou couche
    fc = "AM_OSM_2024_Normandie"  # Ou une table .dbf ou une classe d'entités

    # Spécifiez les deux champs à mettre en minuscules
    fields = ["ame_d", "ame_g"]  # Remplacez par vos champs spécifiques

    # Ouvrir un curseur de mise à jour (UpdateCursor)
    with arcpy.da.UpdateCursor(fc, fields) as cursor:
        for row in cursor:
            # Convertir en minuscules si la valeur n'est pas None
            if row[0] is not None:
                row[0] = row[0].lower()  # Met en minuscule le texte dans Field1
            if row[1] is not None:
                row[1] = row[1].lower()  # Met en minuscule le texte dans Field2
            
            # Mettre à jour la ligne
            cursor.updateRow(row)



    field = ["ame_g"]
    typo = []
    with arcpy.da.UpdateCursor(fc, field) as cursor:
        for row in cursor:
            if row in typo:
                next
            else:
                typo.append(row)

    print(typo)

    replacements = {
        "piste cyclable": "piste uni",
        "voie verte": "voie verte uni",
        "bande cyclable": "bande uni",
        "double sens cyclable bande":"DSC bande",
        "aucun":"",
        "autre":"",
        "couloir bus+velo":"voie bus uni",
        "amenagement mixte pieton velo hors voie verte":"autre chemin velo uni",
        "double sens cyclable piste":"DSC piste",
        "chaussee a voie centrale banalisee":"bande uni",
    }

    # Ouvrir un curseur de mise à jour (UpdateCursor)
    with arcpy.da.UpdateCursor(fc, fields) as cursor:
        for row in cursor:
            # Si la valeur du champ n'est pas None
            if row[0] is not None:
                # Remplacer les mots en fonction du dictionnaire
                for old_word, new_word in replacements.items():
                    row[0] = row[0].replace(old_word, new_word)
            
                # Si la valeur du champ n'est pas None
            if row[1] is not None:
                # Remplacer les mots en fonction du dictionnaire
                for old_word, new_word in replacements.items():
                    row[1] = row[1].replace(old_word, new_word)
            # Mettre à jour la ligne
            cursor.updateRow(row)


    codeblock_new ="""
    def updateField(ad,ag):

        if ad == 'piste uni' and ag == "":
            return 10
        elif ad == "" and ag == 'piste uni':
            return 10        
        elif ad == 'DSC piste' and ag == "":
            return 10
        elif ad == "" and ag == 'DSC piste':
            return 10
        elif ad == 'piste trottoir uni' and ag == "":
            return 10
        elif ad == "" and ag == 'piste trottoir uni':
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
        elif ad == "" and ag == 'piste bi':
            return 11
        elif ad == 'piste bi' and ag == "":
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
        elif ad == "" and ag == 'bande bi':
            return 12
        elif ad == 'bande bi' and ag == "":
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

        elif ad == 'bande uni' and ag == "":
            return 13
        elif ad == "" and ag == 'bande uni':
            return 13
        elif ad == 'DSC bande' and ag == "":
            return 13
        elif ad == "" and ag == 'DSC bande':
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

        elif ad == 'voie bus uni' and ag == "":
            return 17
        elif ad == "" and ag == 'voie bus uni':
            return 17
        elif ad == "" and ag == 'voie bus uni':
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

        elif ad == "" and ag == 'DSC':
            return 16
        elif ad == 'DSC' and ag == "":
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

        elif ad == 'goulotte' and ag == 'goulotte':
            return ""
        elif ad == "" and ag == 'goulotte':
            return ""
        elif ad == 'goulotte' and ag == "":
            return ""

        elif ad == 'cheminement uni' and ag == 'cheminement uni':
            return 19
        elif ad == 'cheminement uni' and ag == "":
            return 19
        elif ad == "" and ag == 'cheminement uni':
            return 19

        else: 
            return "" """

    arcpy.CalculateField_management("AM_OSM_2024_Normandie","c_acniv1","updateField(!ame_d!,!ame_g!)","PYTHON3",codeblock_new)


    arcpy.analysis.Statistics(
        in_table="AM_OSM_2024_Normandie",
        out_table="CAM_OSM_2024_Normandie_Statistics",
        statistics_fields="Shape_Length SUM",
        case_field="c_acniv1",
        concatenation_separator=""
    )

    arcpy.CalculateField_management("CAM_OSM_2024_Normandie_Statistics","km","!SUM_Shape_Length!/1000")

traitement_bdd_normandie(input)





# import osmnx as ox
# import pandas as pd

# chemin1 = chemin_dossier + "\\" + nom_dossier 

# # Définir la zone géographique (par exemple, "Normandie, France")
# place = "Paris, France"

# # Télécharger le réseau routier et cyclable pour Paris
# G = ox.graph_from_place(place, network_type='all', retain_all=True)
# G1 = ox.graph_from_place(place, network_type='bike')

# # Extraire les edges (liens entre les nœuds du réseau)
# edges = ox.graph_to_gdfs(G, nodes=False)
# print(edges)

# bike = ox.graph_to_gdfs(G1, nodes=False)

# print(bike)

# # Vérifier si la colonne 'highway' existe
# if 'highway' in edges.columns:
#     # Aplatir les listes de la colonne 'highway' et extraire les valeurs uniques
#     # Utilisation d'une liste compréhensive pour aplatir les valeurs
#     all_highways = edges['highway'].dropna().tolist()  # Supprimer les valeurs NaN
#     flattened_highways = [item for sublist in all_highways for item in (sublist if isinstance(sublist, list) else [sublist])]
    
#     # Extraire les valeurs uniques
#     unique_highways = set(flattened_highways)

# print("Valeurs uniques du champ 'highway' :", unique_highways)


# # Définir une liste plus complète des tags cyclables
# cycle_tags = [
#     'cycleway',       # Piste cyclable dédiée
#     'cycleway:left',  # Bande cyclable à gauche
#     'cycleway:right', # Bande cyclable à droite
#     'cycleway:both',  # Bande cyclable des deux côtés
#     'bicycle',        # Routes autorisées aux vélos
#     'path',           # Sentier partagé
#     'track',          # Voie verte
#     'route',          # Routes désignées pour les vélos
# ]

# # Filtrer les pistes cyclables en fonction des tags
# pistes_cyclables = edges[edges['highway'].isin(cycle_tags)]


# # Sauvegarder les pistes cyclables dans un fichier shapefile
# pistes_cyclables.to_file(chemin1 + "\\"+ "pistes_cyclables_paris.shp")

# "highway IN ('[''cycleway'', ''path'']', '[''cycleway'', ''service'']', 'cycleway', '[''service'', ''cycleway'']', '[''pedestrian'', ''cycleway'']')"
# "highway IN ('[''cycleway'', ''path'']', '[''cycleway'', ''service'']', 'cycleway', '[''service'', ''cycleway'']', '[''pedestrian'', ''cycleway'']', '[''cycleway'', ''pedestrian'']', '[''cycleway'', ''steps'', ''footway'']', '[''cycleway'', ''steps'', ''path'']', '[''cycleway'', ''footway'']')"