# coding:utf-8
import arcpy

# ---- Activer l'overwrite pour tout le script ----
arcpy.env.overwriteOutput = True

# ---- Fonction pour remplacer les NULL par 0 ----
def remplacer_null(table, prefixe="F"):
    """Remplace les valeurs NULL par 0 pour tous les champs commençant par prefixe"""
    fields = [f.name for f in arcpy.ListFields(table) if f.name.startswith(prefixe)]
    for field in fields:
        expression = f"Reclass(!{field}!)"
        code_block = """
def Reclass(val):
    if val is None:
        return 0
    return val
"""
        arcpy.management.CalculateField(table, field, expression, "PYTHON3", code_block)
    arcpy.AddMessage(f"Remplacement des NULL dans {table} terminé !")
    return fields

# ---- Fonction pour calculer statistiques, pivoter et calculer les colonnes finales ----
def calc_stats_pivot_dyn(input_table, pivot_field, case_field, out_pivot):
    stats_table = out_pivot.replace("_pivot", "_stats")

    # Statistiques
    arcpy.analysis.Statistics(
        in_table=input_table,
        out_table=stats_table,
        statistics_fields="shape_Length SUM",
        case_field=case_field,
        concatenation_separator=""
    )

    # Pivot
    arcpy.management.PivotTable(
        in_table=stats_table,
        fields=pivot_field,
        pivot_field=case_field.split(";")[1],
        value_field="SUM_shape_Length",
        out_table=out_pivot
    )

    # Remplacer les NULL et récupérer la liste des Fxx
    f_fields = remplacer_null(out_pivot, prefixe="F")

    # Calcul dynamique des aménagements cyclables
    def field_exists(f):
        return f in f_fields

    arcpy.management.CalculateField(out_pivot, "voies_vertes", "(!F20!*2)/1000" if field_exists("F20") else "0", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField(out_pivot, "pistes_cyclables",
                                    "((!F11!*2)+!F10!)/1000" if field_exists("F11") and field_exists("F10") else "0",
                                    "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField(out_pivot, "amenagements_cyclables_secu", "!voies_vertes!+!pistes_cyclables!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField(out_pivot, "bandes_cyclables",
                                    "((!F12!*2)+!F13!)/1000" if field_exists("F12") and field_exists("F13") else "0",
                                    "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField(out_pivot, "double_sens_cyclable", "!F16!/1000" if field_exists("F16") else "0", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField(out_pivot, "voie_bus_cyclables",
                                    "(!F14!+!F17!+(2*!F18!))/1000" if all(field_exists(f) for f in ["F14","F17","F18"]) else "0",
                                    "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField(out_pivot, "amenagements_cyclables_partag", "!bandes_cyclables!+!double_sens_cyclable!+!voie_bus_cyclables!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField(out_pivot, "total_amenagements_exi", "!amenagements_cyclables_partag!+!amenagements_cyclables_secu!", "PYTHON3", "", "DOUBLE")

# ---- Fonction principale ----
def stats_cyclable_mgp_epci_dyn(input_table, chemin):
    arcpy.AddMessage("Import couche mgp, epci et accès vélo...")
    arcpy.env.workspace = chemin

    mgp_chemin = r'\\zsfa\sig$\12_BDPPC\maj_pc\script\connexions_sde\utilisateur.sde\apur.diffusion.limite_administrative\apur.diffusion.mgp'
    epci_chemin = r'\\zsfa\sig$\12_BDPPC\maj_pc\script\connexions_sde\utilisateur.sde\apur.diffusion.limite_administrative\apur.diffusion.epci'
    acces_velo_chemin = r'\\zsfa\zsf-apur\PROJETS\AMENAGEMENTS_CYCLABLES_METROPOLE\0_DONNEES\Accessibilite_garesGPE\Accessibilite_garesGPE.gdb\Accessibilite_velo_800m_3km_surf'
    idf_chemin = r'\\zsfa\sig$\12_BDPPC\maj_pc\script\connexions_sde\utilisateur.sde\apur.diffusion.limite_administrative\apur.diffusion.idf'

    # Import des feature classes
    for fc_name, fc_path in [("mgp", mgp_chemin), ("epci", epci_chemin), ("acces_velo", acces_velo_chemin),("idf", idf_chemin)]:
        arcpy.AddMessage(f"Import de {fc_name}...")
        arcpy.conversion.FeatureClassToFeatureClass(fc_path, chemin, fc_name)

    # Liste des intersections à traiter
    intersections = [
        ("acces_velo", "n_sq_st__tobreak", "n_sq_st__tobreak;c_acniv1", "stats_acces_velo_pivot"),
        ("mgp", "l_epci", "l_epci;c_acniv1", "stats_mgp_pivot"),
        ("epci", "l_epci", "l_epci;c_acniv1", "stats_epci_pivot"),
        ("idf", "l_reg", "l_reg;c_acniv1", "stats_idf_pivot")
    ]

    for fc, pivot_field, case_field, out_pivot in intersections:
        out_fc = f"{input_table}_{fc}"
        arcpy.AddMessage(f"Intersection et statistiques {fc}...")
        arcpy.analysis.Intersect(
            in_features=f"{input_table} #;{fc} #",
            out_feature_class=out_fc,
            join_attributes="ALL",
            cluster_tolerance=None,
            output_type="INPUT"
        )
        calc_stats_pivot_dyn(out_fc, pivot_field, case_field, out_pivot)

# ---- Exécution ----
chemin = r"P:\SIG\12_BDPPC\BDPPCDIF\Publications_temporaires\MAJ_AMENAGEMENT_CYCLABLE_07_25\MAJ_AMENAGEMENT_CYCLABLE_07_25.gdb"
input_table = "amenagement_cyclable_2025"
stats_cyclable_mgp_epci_dyn(input_table, chemin)
