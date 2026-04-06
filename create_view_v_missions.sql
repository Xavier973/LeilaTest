DROP VIEW IF EXISTS v_missions;

CREATE VIEW v_missions AS
SELECT
    f.id                                                            AS mission_id,
    f.statut,
    f.mission                                                       AS type_mission,
    f.debut                                                         AS mission_debut,
    f.fin                                                           AS mission_fin,
    e.identifiant                                                   AS engin_immatriculation,
    e.type                                                          AS engin_type,
    e.marque                                                        AS engin_marque,
    e.modele                                                        AS engin_modele,
    CAST(e.contenance AS DECIMAL(6,2))                              AS engin_contenance_t,
    p.nom                                                           AS chauffeur_nom,
    p.prenom                                                        AS chauffeur_prenom,
    rmt.libelle                                                     AS remettant,
    rmt.activite                                                    AS remettant_activite,
    dst.libelle                                                     AS destinataire,
    dst.activite                                                    AS destinataire_activite,
    r.kilometrageDebut                                              AS km_depart,
    l.kilometrageDebut                                              AS km_arrivee,
    (l.kilometrageDebut - r.kilometrageDebut)                       AS distance_km,
    TIMESTAMPDIFF(MINUTE, r.dateDebut, r.dateFin)                   AS attente_chargement_min,
    TIMESTAMPDIFF(MINUTE, r.dateFin,   l.dateDebut)                 AS duree_trajet_min,
    TIMESTAMPDIFF(MINUTE, l.dateDebut, l.dateFin)                   AS attente_dechargement_min,
    TIMESTAMPDIFF(MINUTE, r.dateDebut, l.dateFin)                   AS duree_totale_min,
    r.gpsLatitude                                                   AS lat_retrait,
    r.gpsLongitude                                                  AS lon_retrait,
    l.gpsLatitude                                                   AS lat_livraison,
    l.gpsLongitude                                                  AS lon_livraison,
    GROUP_CONCAT(DISTINCT m.libelle ORDER BY m.id SEPARATOR ', ')   AS marchandises,
    SUM(COALESCE(m.poidsNet,  0))                                   AS poids_net_total_t,
    SUM(COALESCE(m.poidsBrut, 0))                                   AS poids_brut_total_t
FROM Formulaire f
JOIN Entite      ent ON ent.formulaireId = f.id AND ent.fonction = 'EQ-5003'
JOIN Engin       e   ON e.entiteId       = ent.id
JOIN Retrait     r   ON r.enginId        = e.id
JOIN Livraison   l   ON l.enginId        = e.id
JOIN Personne    p   ON p.enginId        = e.id
LEFT JOIN Entite rmt ON rmt.retraitId    = r.id
LEFT JOIN Entite dst ON dst.livraisonId  = l.id
LEFT JOIN Marchandise m ON m.enginId     = e.id
WHERE f.mission IN ('Transport marchandises', 'Location à la journée', 'Location au voyage')
  AND (l.kilometrageDebut - r.kilometrageDebut) BETWEEN 1 AND 300
  AND NOT (
        r.gpsLatitude   IS NOT NULL
    AND l.gpsLatitude   IS NOT NULL
    AND r.gpsLatitude   = l.gpsLatitude
    AND r.gpsLongitude  = l.gpsLongitude
    AND (l.kilometrageDebut - r.kilometrageDebut) > 100
  )
GROUP BY f.id;

-- Vérification rapide
SELECT
    COUNT(*)                    AS total_missions,
    COUNT(DISTINCT engin_immatriculation) AS nb_engins,
    MIN(mission_debut)          AS debut_periode,
    MAX(mission_debut)          AS fin_periode,
    ROUND(AVG(distance_km), 1)  AS dist_moy_km,
    SUM(distance_km)            AS km_total
FROM v_missions;
