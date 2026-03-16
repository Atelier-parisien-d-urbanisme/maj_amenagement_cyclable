Ce projet contient deux scripts python :
1) maj_amenagement_cyclable_bnac.py
2) maj_amenagement_cyclable_idfm.py

==============================

Le script Python maj_amenagement_cyclable_bnac.py permet de mettre à jour la base de données des aménagements cyclables d’Île-de-France (IDF) à partir des données nationales issues de la Base Nationale des Aménagements Cyclables (BNAC).
Les données sources proviennent du portail data.gouv.fr, jeu de données : Aménagements cyclables France Métropolitaine.

Le script automatise :
 - 📥 Le téléchargement des données BNAC (GeoJSON)
 - 🗂 La création d’un workspace (.gdb)
 - 🔄 La conversion et projection des données
 - ✂ Le découpage à l’échelle IDF
 - 🧹 La normalisation des champs
 - 🧮 La catégorisation des aménagements (niveaux APUR / c_acniv1, c_acniv2)
 - 📊 Produit des statistiques territoriales (MGP, EPCI)

La couche qui est traité reprend les différents champs dans la base de données BNAC. Y est ajouté les champs suivants :
- c_acniv1 : Code cyclable pour représentation cartographique simplifiée des aménagements cyclables suivant une nomenclature à 10 postes (valeurs : de 10 à 20)
- c_acniv2 : Code cyclable pour représentation cartographique simplifiée des aménagements cyclables suivant une nomenclature à 2 postes (valeurs : 1 et 2)
Ces champs sont construits à partir des champs présents dans les données BNAC: ame_d, ame_g, regime_d, regime_g, sens_d et sens_g d.

==============================

Le script Python maj_amenagement_cyclable_idfm.py permet de mettre à jour la base de données des aménagements cyclables d’Île-de-France (IDF) à partir des données provenant d'Iles-de-France Mobilités (IDFM).
Les données sources proviennent du portail data.iledefrance-mobilites.fr, jeu de données : Aménagements vélo en Île-de-France.

Le script automatise :
 - 📥 Télécharge le GeoJSON IDFM
 - 🗂️ Crée un workspace (dossier + File Geodatabase)
 - 🔄 Convertit les données en Feature Class
 - 🧹 Réorganise les champs
 - 🧠 Recalcule la classification cyclable APUR (niveaux APUR / c_acniv1, c_acniv2)
 - 🔍 Compare ancienne et nouvelle base
 - 📊 Produit des statistiques territoriales (MGP, EPCI, zones d’accessibilité vélo)

Les différents champs sont référencées ici : https://geocatalogue.apur.org/catalogue/srv/fre/catalog.search#/metadata/a9c76257-46f0-44a3-a6e6-ac70eb7c7892

==============================

🎯 c_acniv1 – Classification détaillée
 - Code	Type d’aménagement
 - 10	Piste cyclable unidirectionnelle
 - 11	Piste bidirectionnelle
 - 12	Bande bidirectionnelle
 - 13	Bande unidirectionnelle
 - 14	Bande + voie bus
 - 16	Double sens cyclable
 - 17	Voie bus partagée
 - 18	Voie bus bidirectionnelle
 - 19	Aménagement partagé
 - 20	Voie verte

🎯 c_acniv2 – Classification simplifiée
 - Code	Type d’aménagement
 - 1	 Piste cyclable structurante
 - 2	 Autre aménagement cyclable
