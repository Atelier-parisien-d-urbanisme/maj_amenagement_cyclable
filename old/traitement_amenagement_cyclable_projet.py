#coding:utf-8

import arcpy
import numpy as np

path = arcpy.env.workspace = r'\\zsfa\ZSF-APUR\SIG\12_BDPPC\BDPPCDIF\Publications_temporaires\MAJ_AMENAGEMENT_CYCLABLE\MAJ_AMENAGEMENT_CYCLABLE.gdb' # Localisation du workspace
arcpy.env.overwriteOutput = True # Attention permet d'écraser fichier du même nom

### Localisation des entrées / noms des variables ###
RERV = "RER_V_APUR_OSM_2022"
PVM = "PVM_APUR_OSM_2022"
BCO = "BCO_APUR_OSM_2022"
PVP ="PVP_APUR_OSM_2022"
CD92 = "CD92_APUR_OSM_2022"
CD93 = "CD93_APUR_OSM_Merge_2022"
CD94 = "CD94_APUR_OSM_Merge_2022"
amenagement_cyclable = "cyclable_osm_apur_2022_id_not_null"

arcpy.AddMessage("Lancement du traitement des données cyclable projet...")

# arcpy.CopyFeatures_management("amenagement_cyclable_projet_merge_diss_2022","CYCLABLE_PROJET")
# CP = "CYCLABLE_PROJET"

# # arcpy.AddMessage("Ajout des champs...")
# # # arcpy.AddField_management(CP,"PV75","TEXT")
# # # arcpy.AddField_management(CP,"PV75_TYPE","TEXT")
# # # arcpy.AddField_management(CP,"SDIC92","TEXT")
# # # arcpy.AddField_management(CP,"SDIC92_TYPE","TEXT")
# # # arcpy.AddField_management(CP,"SDIC93","TEXT")
# # # arcpy.AddField_management(CP,"SDIC93_TYPE","TEXT")
# # # arcpy.AddField_management(CP,"SDIC94","TEXT")
# # # arcpy.AddField_management(CP,"SDIC94_TYPE","TEXT")
# # # arcpy.AddField_management(CP,"RERV","TEXT")
# # # arcpy.AddField_management(CP,"RERV_NOM","TEXT")
# # # arcpy.AddField_management(CP,"PVP","TEXT")
# # # arcpy.AddField_management(CP,"PVP_TYPE","TEXT")
# # # arcpy.AddField_management(CP,"PVM","TEXT")
# # # arcpy.AddField_management(CP,"PVM_NUMERO","TEXT")
# # # arcpy.AddField_management(CP,"BCO","TEXT")
# # # arcpy.AddField_management(CP,"SOURCE","TEXT")
# # # arcpy.AddField_management(CP,"REALISE","TEXT")
# # # arcpy.AddField_management(CP,"ANNEE_ACHEVEMENT","LONG")

# ######### RERV #########
# arcpy.AddMessage("Traitement RERV...")
# arcpy.JoinField_management(CP,"osm_id",RERV,"osm_id",["RERV","RERV_NOM","REALISE","SOURCE","ANNEE_ACHEVEMENT"])

# ######### PVM #########
# arcpy.AddMessage("Traitement PVM...")
# arcpy.JoinField_management(CP,"osm_id",PVM,"osm_id",["PVM","PVM_NUMERO","SOURCE"])
# codeblock ="""
# def updateField(SOURCE,SOURCE_1):
#     if SOURCE == None:
#         return SOURCE_1
#     else: 
#         return SOURCE"""
# arcpy.CalculateField_management(CP,"SOURCE","updateField(!SOURCE!,!SOURCE_1!)","PYTHON_9.3",codeblock)
# arcpy.DeleteField_management(CP, "SOURCE_1")

# ######### BCO #########
# arcpy.AddMessage("Traitement BCO...")
# arcpy.JoinField_management(CP,"osm_id",BCO,"osm_id",["BCO","REALISE","SOURCE","ANNEE_ACHEVEMENT"])

# liste_fields = ["REALISE_1","SOURCE_1","ANNEE_ACHEVEMENT_1"]
# liste_fields_origin = ["REALISE","SOURCE","ANNEE_ACHEVEMENT"]

# codeblock ="""
# def updateField(value,value_1):
#     if value == None:
#         return value_1
#     else: 
#         return value"""

# for i in range(0,np.size(liste_fields),1):
#     data = liste_fields[i]
#     data_1 = liste_fields_origin[i]
#     arcpy.CalculateField_management(CP,data_1,"updateField(!{}!,!{}!)".format(data_1,data),"PYTHON_9.3",codeblock)

# for i in range(0,np.size(liste_fields),1):
#     data = liste_fields[i]
#     arcpy.DeleteField_management(CP, data)

# ######### PVP #########
# arcpy.AddMessage("Traitement PVP...")
# arcpy.JoinField_management(CP,"osm_id",PVP,"osm_id",["PVP","PVP_TYPE","REALISE","SOURCE","ANNEE_ACHEVEMENT"])

# for i in range(0,np.size(liste_fields),1):
#     data = liste_fields[i]
#     data_1 = liste_fields_origin[i]
#     arcpy.CalculateField_management(CP,data_1,"updateField(!{}!,!{}!)".format(data_1,data),"PYTHON_9.3",codeblock)

# for i in range(0,np.size(liste_fields),1):
#     data = liste_fields[i]
#     arcpy.DeleteField_management(CP, data)   

# ######### CD92 #########
# arcpy.AddMessage("Traitement CD92...")
# arcpy.JoinField_management(CP,"osm_id",CD92,"osm_id",["SDIC92","SDIC92_TYPE","REALISE","SOURCE"])

# liste_fields = ["REALISE_1","SOURCE_1"]
# liste_fields_origin = ["REALISE","SOURCE"]

# for i in range(0,np.size(liste_fields),1):
#     data = liste_fields[i]
#     data_1 = liste_fields_origin[i]
#     arcpy.CalculateField_management(CP,data_1,"updateField(!{}!,!{}!)".format(data_1,data),"PYTHON_9.3",codeblock)

# for i in range(0,np.size(liste_fields),1):
#     data = liste_fields[i]
#     arcpy.DeleteField_management(CP, data)

# ######### CD93 #########
# arcpy.AddMessage("Traitement CD93...")
# arcpy.JoinField_management(CP,"osm_id",CD93,"osm_id",["SDIC93","SDIC93_TYPE","REALISE","SOURCE","ANNEE_ACHEVEMENT"])

# liste_fields = ["REALISE_1","SOURCE_1","ANNEE_ACHEVEMENT_1"]
# liste_fields_origin = ["REALISE","SOURCE","ANNEE_ACHEVEMENT"]

# for i in range(0,np.size(liste_fields),1):
#     data = liste_fields[i]
#     data_1 = liste_fields_origin[i]
#     arcpy.CalculateField_management(CP,data_1,"updateField(!{}!,!{}!)".format(data_1,data),"PYTHON_9.3",codeblock)

# for i in range(0,np.size(liste_fields),1):
#     data = liste_fields[i]
#     arcpy.DeleteField_management(CP, data)

# ######### CD94 #########
# arcpy.AddMessage("Traitement CD94...")
# arcpy.JoinField_management(CP,"osm_id",CD94,"osm_id",["SDIC94","SDIC94_TYPE","ID","REALISE","SOURCE","ANNEE_ACHEVEMENT"])

# liste_fields = ["REALISE_1","SOURCE_1","ANNEE_ACHEVEMENT_1"]
# liste_fields_origin = ["REALISE","SOURCE","ANNEE_ACHEVEMENT"]

# for i in range(0,np.size(liste_fields),1):
#     data = liste_fields[i]
#     data_1 = liste_fields_origin[i]
#     arcpy.CalculateField_management(CP,data_1,"updateField(!{}!,!{}!)".format(data_1,data),"PYTHON_9.3",codeblock)

# for i in range(0,np.size(liste_fields),1):
#     data = liste_fields[i]
#     arcpy.DeleteField_management(CP, data)

# arcpy.AlterField_management(CP,"ID","ID_SDIC94","ID_SDIC94")

# arcpy.MakeFeatureLayer_management("amenagement_cyclable_projet_merge_2022","amenagement_cyclable_projet_merge_2022_lyr")
# arcpy.SelectLayerByAttribute_management("amenagement_cyclable_projet_merge_2022_lyr","NEW_SELECTION","osm_id IS NULL OR osm_id = 0")
# arcpy.CopyFeatures_management("amenagement_cyclable_projet_merge_2022_lyr","cyclable_osm_apur_2022_null")

# arcpy.AddMessage("Merge des données...")
# arcpy.Merge_management("cyclable_osm_apur_2022_null;CYCLABLE_PROJET", "amenagement_cyclable_projet_2022", 'osm_id "osm_id" true true false 8 Double 0 0 ,First,#,cyclable_osm_apur_2022_null,osm_id,-1,-1,CYCLABLE_PROJET,osm_id,-1,-1;SDIC93 "SDIC93" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,SDIC93,-1,-1,CYCLABLE_PROJET,SDIC93,-1,-1;ANNEE_ACHEVEMENT "ANNEE_ACHEVEMENT" true true false 4 Long 0 0 ,First,#,cyclable_osm_apur_2022_null,ANNEE_ACHEVEMENT,-1,-1,CYCLABLE_PROJET,ANNEE_ACHEVEMENT,-1,-1;SOURCE "SOURCE" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,SOURCE,-1,-1,CYCLABLE_PROJET,SOURCE,-1,-1;REALISE "REALISE" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,REALISE,-1,-1,CYCLABLE_PROJET,REALISE,-1,-1;SDIC93_TYPE "SDIC93_TYPE" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,SDIC93_TYPE,-1,-1,CYCLABLE_PROJET,SDIC93_TYPE,-1,-1;ID_SDIC94 "ID_SDIC94" true true false 100 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,ID_SDIC94,-1,-1,CYCLABLE_PROJET,ID_SDIC94,-1,-1;SDIC94 "SDIC94" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,SDIC94,-1,-1,CYCLABLE_PROJET,SDIC94,-1,-1;SDIC94_TYPE "SDIC94_TYPE" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,SDIC94_TYPE,-1,-1,CYCLABLE_PROJET,SDIC94_TYPE,-1,-1;SDIC92 "SDIC92" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,SDIC92,-1,-1,CYCLABLE_PROJET,SDIC92,-1,-1;SDIC92_TYPE "SDIC92_TYPE" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,SDIC92_TYPE,-1,-1,CYCLABLE_PROJET,SDIC92_TYPE,-1,-1;PVP "PVP" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,PVP,-1,-1,CYCLABLE_PROJET,PVP,-1,-1;PVP_TYPE "PVP_TYPE" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,PVP_TYPE,-1,-1,CYCLABLE_PROJET,PVP_TYPE,-1,-1;BCO "BCO" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,BCO,-1,-1,CYCLABLE_PROJET,BCO,-1,-1;RERV "RERV" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,RERV,-1,-1,CYCLABLE_PROJET,RERV,-1,-1;RERV_NOM "RERV_NOM" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,RERV_NOM,-1,-1,CYCLABLE_PROJET,RERV_NOM,-1,-1;PVM "PVM" true true false 50 Text 0 0 ,First,#,cyclable_osm_apur_2022_null,PVM,-1,-1,CYCLABLE_PROJET,PVM,-1,-1;PVM_NUMERO "PVM_NUMERO" true true false 4 Long 0 0 ,First,#,cyclable_osm_apur_2022_null,PVM_NUMERO,-1,-1,CYCLABLE_PROJET,PVM_NUMERO,-1,-1;Shape_Leng "Shape_Leng" true true false 8 Double 0 0 ,First,#,cyclable_osm_apur_2022_null,Shape_Leng,-1,-1,CYCLABLE_PROJET,Shape_Leng,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0 ,First,#,cyclable_osm_apur_2022_null,Shape_Length,-1,-1,CYCLABLE_PROJET,Shape_Length,-1,-1')

codeblock ="""
def updateField(value):
    if value == " ":
        return None
    else: 
        return value"""

nbres_champs = [f.name for f in arcpy.ListFields("amenagement_cyclable_projet_2022")]
print(nbres_champs)
nbres_champs = ['osm_id', 'SDIC93', 'ANNEE_ACHEVEMENT', 'SOURCE', 'REALISE', 'SDIC93_TYPE', 'ID_SDIC94', 'SDIC94', 'SDIC94_TYPE', 'SDIC92', 'SDIC92_TYPE', 'PVP', 'PVP_TYPE', 'BCO', 'RERV', 'RERV_NOM', 'PVM', 'PVM_NUMERO']
for i in nbres_champs:
    print(i)
    arcpy.CalculateField_management("amenagement_cyclable_projet_2022",i,"updateField(!{}!)".format(i),"PYTHON_9.3",codeblock)


codeblock ="""
def updateField(value):
    if value == None:
        return "Non"
    else: 
        return value"""

nbres_champs = ['SDIC93', 'SDIC94','SDIC92', 'PVP','BCO', 'RERV', 'PVM']
for i in nbres_champs:
    print(i)
    arcpy.CalculateField_management("amenagement_cyclable_projet_2022",i,"updateField(!{}!)".format(i),"PYTHON_9.3",codeblock)

codeblock ="""
def updateField(value):
    if value == 0:
        return None
    else: 
        return value"""

nbres_champs = ['osm_id', 'PVM_NUMERO',"ANNEE_ACHEVEMENT"]
for i in nbres_champs:
    print(i)
    arcpy.CalculateField_management("amenagement_cyclable_projet_2022",i,"updateField(!{}!)".format(i),"PYTHON_9.3",codeblock)