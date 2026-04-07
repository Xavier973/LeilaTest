SELECT
    chauffeur_nom,
    chauffeur_prenom,
    COUNT(*)                                    AS nb_missions,
    ROUND(AVG(duree_totale_min), 0)             AS duree_moy_min,
    MAX(duree_totale_min)                       AS duree_max_min,
    SUM(CASE WHEN duree_totale_min > 600 THEN 1 ELSE 0 END) AS missions_suspectes,
    ROUND(SUM(duree_totale_min) / 60.0, 1)     AS heures_totales,
    ROUND(AVG(attente_chargement_min), 0)       AS attente_charg_moy,
    ROUND(AVG(attente_dechargement_min), 0)     AS attente_decharg_moy
FROM v_missions
GROUP BY chauffeur_nom, chauffeur_prenom
ORDER BY heures_totales DESC;

SELECT e.id, identifiant,
`type`,
libelle,
marque,
modele,
proprietaire,
contenance,
fonction,
entiteId,
e.createdAt AS engin_createdAt,
e.updatedAt AS engin_updatedAt
r.createdAt AS retrait_createdAt,
r.updatedAt AS retrait_updatedAt,
l.createdAt AS livraison_createdAt,
l.updatedAt AS livraison_updatedAt
FROM engin e
join retrait r on e.id = r.enginID
join livraison l on e.id = l.enginID