#coding:utf-8

import arcpy

# Ce script permet de mettre traiter et suivre les traces amenagement cyclable et RER V etc... 
# Database Connections\perron@apur@zpostgresig.sde\apur.diffusion.cyclable\apur.diffusion.amenagement_cyclable

path = arcpy.env.workspace = r'\\zsfa\ZSF-APUR\SIG\12_BDPPC\BDPPCDIF\Publications_temporaires\MAJ_AMENAGEMENT_CYCLABLE\CD78.gdb' # Localisation du workspace
arcpy.env.overwriteOutput = True # Attention permet d'écraser fichier du même nom

### Localisation des entrées / noms des variables ###
rer_v = "RERV_APUR_2022"
# amenagement_cyclable = "amenagement_cyclable_2022"
# amenagement_cyclable = "LOCAL_MERGE_RERV_MERGE_BCO"

# voie = "troncon_voie_paris_2021"
CD92 = "CD92_proj"
PVM = "PVM_APUR_2022"
BCO = "BCO_APUR_2022"
PVP ="PVP_APUR_2022"
CD94 = "CD94_APUR_2022"
CD93 = "CD93_APUR_2022"
RERV = "RER_V_APUR_OSM_2022"
BCO = "BCO_APUR_OSM_2022"
PVM = "PVM_APUR_OSM_2022"
PCO = "Amenagements_cyclables_PCO"
GPSO = "GPSO_CYCLABLE"

CD98 = "CD_78"
voie = "projet_amenagement_cyclable"
amenagement_cyclable = "amenagement_cyclable"

arcpy.AddMessage("Lancement du traitement des données cyclable...")

# arcpy.AddMessage("Buffer des données cyclable...")
# arcpy.Buffer_analysis(rer_v, "PISTE_BUFF", "100 Meters", "FULL", "ROUND", "NONE", "", "GEODESIC")

arcpy.AddMessage("Buffer des données cyclable...")
arcpy.Buffer_analysis(CD98, "PISTE_BUFF", "400 Meters", "FULL", "ROUND", "NONE", "", "GEODESIC")

list_traitement = [voie,amenagement_cyclable]
for i in list_traitement:
    print("Traitement sur "+i)
    arcpy.AddMessage("Selection les pistes sur le buffer...")
    arcpy.MakeFeatureLayer_management(i, "AMENAGEMENT_CYLCLABLE_LYR")
    arcpy.SelectLayerByLocation_management("AMENAGEMENT_CYLCLABLE_LYR","INTERSECT","PISTE_BUFF")
    arcpy.CopyFeatures_management("AMENAGEMENT_CYLCLABLE_LYR","AMENAGEMENT_CYLCLABLE_SEL")

    arcpy.AddMessage("Conversion en points...")
    arcpy.FeatureVerticesToPoints_management("AMENAGEMENT_CYLCLABLE_SEL", "AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS","BOTH_ENDS")

    arcpy.AddMessage("Selection les pistes sur le buffer...")
    arcpy.MakeFeatureLayer_management("AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS", "AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_LYR")
    arcpy.SelectLayerByLocation_management("AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_LYR","INTERSECT","PISTE_BUFF")
    arcpy.CopyFeatures_management("AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_LYR","AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL")

    arcpy.AddMessage("Dissolve des points afin de compter les extremites dans le buffer...")
    arcpy.Dissolve_management("AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL", "AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL_DISS", "ORIG_FID", "ORIG_FID COUNT", "MULTI_PART", "DISSOLVE_LINES")

    arcpy.AddMessage("Identity pour recuperer les donnees du buffer...")
    arcpy.Identity_analysis("AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL_DISS", "PISTE_BUFF", "AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL_DISS_ID", "ALL", "", "NO_RELATIONSHIPS")

    arcpy.AddMessage("Selection des objets ayant leurs deux points dans le buffer...")
    arcpy.MakeFeatureLayer_management("AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL_DISS_ID", "AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL_DISS_ID_LYR")
    arcpy.SelectLayerByAttribute_management("AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL_DISS_ID_LYR","NEW_SELECTION","COUNT_ORIG_FID = 2")
    arcpy.CopyFeatures_management("AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL_DISS_ID_LYR","AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL_DISS_ID_SEL")

    # champs = ["Nom","Description","Ligne","Nom_ligne","Phase"] # RER V
    # champs = ["Type_piste","Existant"] # CD92

    # champs = ["n_"] # PVM

    # champs = ["etat","echeance","moa","financeur","Route_depa","Territoire","Ville_de_P"] # BCO
    # champs = ["descriptio","typo"] # PVP

    # champs = ["ID","LIB_ITINER","LIB_ETAT_A","LIB_TYPOLO","CREATION"] # CD94
    # champs = ["projet","date_echea","source","rg_cle"] # CD93

    # champs = ["RERV","RERV_NOM","REALISE","SOURCE","ANNEE_ACHEVEMENT"] #RERV
    # champs = ["BCO","REALISE","SOURCE","ANNEE_ACHEVEMENT"] #BCO

    # champs = ["PVM","PVM_NUMERO","SOURCE"] #PVM

    champs = ["cd_78_type"]

    arcpy.AddMessage("Joindre les tables...")
    arcpy.CopyFeatures_management("AMENAGEMENT_CYLCLABLE_SEL","PISTE_2022")
    arcpy.JoinField_management("PISTE_2022","objectid","AMENAGEMENT_CYLCLABLE_SEL_PTS_ENDS_SEL_DISS_ID_SEL","ORIG_FID",champs)

    arcpy.AddMessage("Selection des objets non null...")
    arcpy.MakeFeatureLayer_management("PISTE_2022", "PISTE_2022_LYR")
    arcpy.SelectLayerByAttribute_management("PISTE_2022_LYR","NEW_SELECTION","{} IS NOT NULL".format(champs[0]))
    arcpy.CopyFeatures_management("PISTE_2022_LYR","PISTE_BUFF"+i)

arcpy.AddMessage("1er traitement de la base de données cyclable terminée...")

arcpy.AddMessage("2eme traitement de correction à la main...")


# codeblock ="""
# def updateField(insee_com):

#     if  insee_com == None :
#         return 'non'
#     else: 
#         return 'oui'"""

# arcpy.CalculateField_management("PISTE_2022_MODIF_NEAR","PISTE_2022_MODIF.Existant_OSM","updateField(!PISTE_2022_MODIF.insee_com!)","PYTHON_9.3",codeblock)

# codeblock ="""
# def updateField(Type_piste):

#     if  Type_piste == 'Franchissement ou liaisons à étudier' :
#         return 'Itinéraire interdépartementaux'
#     else: 
#         return 'non'"""

# arcpy.CalculateField_management("PISTE_2022_MODIF_NEAR","Franchissement_etudier","updateField(!Type_piste!)","PYTHON_9.3",codeblock)