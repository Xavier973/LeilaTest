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

SELECT
    e.id,
    e.identifiant,
    e.contenance,
    e.fonction,
    e.entiteId,
    e.createdAt                                         AS engin_createdAt,
    e.updatedAt                                         AS engin_updatedAt,
    r.dateDebut                                         AS retrait_dateDebut,
    r.dateFin                                           AS retrait_dateFin,
    r.createdAt                                         AS retrait_createdAt,
    r.updatedAt                                         AS retrait_updatedAt,
    l.dateDebut                                         AS livraison_dateDebut,
    l.dateFin                                           AS livraison_dateFin,
    l.createdAt                                         AS livraison_createdAt,
    l.updatedAt                                         AS livraison_updatedAt,
    -- Durée calculée pour confirmer le filtre
    TIMESTAMPDIFF(MINUTE, r.dateDebut, l.dateFin)       AS duree_totale_min,
    ROUND(TIMESTAMPDIFF(MINUTE, r.dateDebut, l.dateFin) / 60.0, 1) AS duree_totale_h,
    -- Nb de jours entre début retrait et fin livraison
    DATEDIFF(l.dateFin, r.dateDebut)                    AS nb_jours_ecart
FROM engin e
JOIN retrait  r ON e.id = r.enginId
JOIN livraison l ON e.id = l.enginId
WHERE TIMESTAMPDIFF(MINUTE, r.dateDebut, l.dateFin) > 600
ORDER BY duree_totale_min DESC;

SELECT
    e.id,
    e.identifiant,
    e.contenance,
    e.fonction,
    e.entiteId,
    r.dateDebut                                         AS retrait_dateDebut,
    r.dateFin                                           AS retrait_dateFin,
    l.dateDebut                                         AS livraison_dateDebut,
    l.dateFin                                           AS livraison_dateFin,
    -- Durée calculée pour confirmer le filtre
    TIMESTAMPDIFF(MINUTE, r.dateDebut, l.dateFin)       AS duree_totale_min,
    ROUND(TIMESTAMPDIFF(MINUTE, r.dateDebut, l.dateFin) / 60.0, 1) AS duree_totale_h,
    -- Nb de jours entre début retrait et fin livraison
    DATEDIFF(l.dateFin, r.dateDebut)                    AS nb_jours_ecart
FROM engin e
JOIN retrait  r ON e.id = r.enginId
JOIN livraison l ON e.id = l.enginId
WHERE TIMESTAMPDIFF(MINUTE, r.dateDebut, l.dateFin) > 600
ORDER BY duree_totale_min DESC;

SELECT id,
numero,
dateDebut,
dateFin,
kilometrageDebut,
kilometrageFin,
gpsLatitude,
gpsLongitude,
createdAt,
updatedAt,
enginId,
observation
FROM location;

SELECT
    chauffeur_nom,
    chauffeur_prenom,
    type_duree,
    COUNT(*)                                AS nb_missions,
    ROUND(AVG(duree_totale_min), 0)         AS duree_moy_min,
    ROUND(AVG(duree_totale_min) / 60, 1)   AS duree_moy_h,
    MAX(duree_totale_min)                  AS duree_max_min,
    ROUND(SUM(duree_totale_min) / 60, 1)   AS heures_total
FROM v_missions
GROUP BY chauffeur_nom, chauffeur_prenom, type_duree
ORDER BY type_duree;

SELECT id, libelle, code, mission, serviceClient, poste, projet, site, statut, observation, debut, fin, createdAt, updatedAt, collecteId
FROM formulaire
ORDER BY site;

SELECT id, libelle, code, mission, serviceClient, poste, projet, site, statut, observation, debut, fin, createdAt, updatedAt, collecteId
FROM formulaire
GROUP BY mission;