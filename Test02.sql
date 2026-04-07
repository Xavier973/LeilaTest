SELECT
    e.identifiant                                               AS engin,
    e.type                                                      AS type_engin,
    e.marque,
    COUNT(DISTINCT m.id)                                        AS nb_pleins,
    ROUND(SUM(m.quantite), 0)                                   AS total_litres,
    ROUND(AVG(m.quantite), 1)                                   AS moy_litres_par_plein,
    ROUND(km.km_total, 0)                                       AS km_total,
    -- Formule : (litres / km) × 100
    ROUND(SUM(m.quantite) / NULLIF(km.km_total, 0) * 100, 1)   AS L_pour_100km
FROM mouvementstock m
JOIN formulaire f  ON f.id             = m.formulaireId
JOIN entite ent    ON ent.formulaireId = f.id
                   AND ent.fonction    = 'EQ-5003'
JOIN engin e       ON e.entiteId       = ent.id
-- Km totaux par engin depuis v_missions
LEFT JOIN (
    SELECT engin_immatriculation, SUM(distance_km) AS km_total
    FROM v_missions
    GROUP BY engin_immatriculation
) km ON km.engin_immatriculation = e.identifiant
WHERE m.produit = 'Gasoil'
GROUP BY e.identifiant, e.type, e.marque, km.km_total
ORDER BY total_litres DESC;

SELECT
    e.identifiant                                               AS engin,
    e.type                                                      AS type_engin,
    e.marque,
    COUNT(DISTINCT m.id)                                        AS nb_pleins,
    ROUND(SUM(m.quantite), 0)                                   AS total_litres,
    ROUND(AVG(m.quantite), 1)                                   AS moy_litres_par_plein,
    -- Km missions (trajets chargés uniquement)
    ROUND(km.km_missions, 0)                                    AS km_missions,
    -- Km odomètre total (premier retrait → dernière livraison)
    (od.km_max - od.km_min)                                     AS km_odometre,
    -- L/100km sur km odomètre = valeur réaliste
    ROUND(SUM(m.quantite) / NULLIF(od.km_max - od.km_min, 0) * 100, 1) AS L_pour_100km
FROM mouvementstock m
JOIN formulaire f  ON f.id             = m.formulaireId
JOIN entite ent    ON ent.formulaireId = f.id
                   AND ent.fonction    = 'EQ-5003'
JOIN engin e       ON e.entiteId       = ent.id
LEFT JOIN (
    SELECT engin_immatriculation, SUM(distance_km) AS km_missions
    FROM v_missions
    GROUP BY engin_immatriculation
) km ON km.engin_immatriculation = e.identifiant
-- Odomètre : étendue totale sur la période
LEFT JOIN (
    SELECT r.enginId,
           MIN(r.kilometrageDebut) AS km_min,
           MAX(l.kilometrageDebut) AS km_max
    FROM retrait r
    JOIN livraison l ON l.enginId = r.enginId
    GROUP BY r.enginId
) od ON od.enginId = e.id
WHERE m.produit = 'Gasoil'
GROUP BY e.identifiant, e.type, e.marque, km.km_missions, od.km_min, od.km_max
ORDER BY total_litres DESC;

SELECT
    e.identifiant                                               AS engin,
    e.type                                                      AS type_engin,
    e.marque,
    COUNT(DISTINCT m.id)                                        AS nb_pleins,
    ROUND(SUM(m.quantite), 0)                                   AS total_litres,
    ROUND(AVG(m.quantite), 1)                                   AS moy_litres_par_plein,
    ROUND(km.km_missions, 0)                                    AS km_missions,
    (od.km_max - od.km_min)                                     AS km_odometre,
    ROUND(SUM(m.quantite) / NULLIF(od.km_max - od.km_min, 0) * 100, 1) AS L_pour_100km
FROM mouvementstock m
JOIN formulaire f  ON f.id             = m.formulaireId
JOIN entite ent    ON ent.formulaireId = f.id
                   AND ent.fonction    = 'EQ-5003'
JOIN engin e       ON e.entiteId       = ent.id
LEFT JOIN (
    SELECT engin_immatriculation, SUM(distance_km) AS km_missions
    FROM v_missions
    GROUP BY engin_immatriculation
) km ON km.engin_immatriculation = e.identifiant
-- Odomètre : grouper par identifiant pour couvrir TOUS les enginId du même véhicule
LEFT JOIN (
    SELECT
        e2.identifiant,
        MIN(r.kilometrageDebut) AS km_min,
        MAX(l.kilometrageDebut) AS km_max
    FROM retrait r
    JOIN engin e2 ON e2.id = r.enginId
    JOIN livraison l ON l.enginId = r.enginId
    GROUP BY e2.identifiant
) od ON od.identifiant = e.identifiant
WHERE m.produit = 'Gasoil'
GROUP BY e.identifiant, e.type, e.marque, km.km_missions, od.km_min, od.km_max
ORDER BY total_litres DESC;