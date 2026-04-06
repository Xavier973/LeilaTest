SELECT
    f.id,
    f.code,
    f.mission,
    f.equipe,
    f.site,
    f.statut,
    f.debut,
    f.collecteId,
    ms.quantite     AS litres,
    ms.fournisseur,
    ms.espaceOrigine
FROM formulaire f
JOIN mouvementstock ms ON ms.formulaireId = f.id
WHERE f.code = 'CRB'
ORDER BY f.debut
LIMIT 15;

-- Personne a enginId → on cherche le chauffeur qui a saisi le formulaire CRB
SELECT
    f.id            AS formulaire_id,
    f.debut         AS date_plein,
    f.equipe,
    p.nom,
    p.prenom,
    e.identifiant   AS engin_id,
    e.libelle       AS engin_libelle,
    e.type          AS engin_type,
    ms.quantite     AS litres,
    ms.fournisseur,
    ms.espaceOrigine
FROM formulaire f
JOIN mouvementstock ms ON ms.formulaireId = f.id
JOIN personne p        ON p.enginId = (
    -- [INCERTITUDE] chemin de jointure à confirmer
    SELECT e2.id FROM engin e2 WHERE e2.entiteId = p.entiteId LIMIT 1
)
JOIN engin e           ON e.id = p.enginId
WHERE f.code = 'CRB'
ORDER BY f.debut
LIMIT 20;

SELECT * FROM mouvementstock mvs
JOIN formulaire f ON f.id = mvs.formulaireId
JOIN personne p ON p.mvsId = mvs.id
JOIN engin e ON e.id = p.enginId


SELECT * FROM personne p
JOIN engin e ON e.id = p.enginId

SELECT * FROM personne p
JOIN mouvementstock mvs ON p.mvsId = mvs.id

SELECT * FROM personne p
JOIN engin e ON e.id = p.enginId
JOIN mouvementstock mvs ON p.mvsId = mvs.id

SELECT
    p.nom,
    e.identifiant   AS engin,
    mvs.quantite    AS litres
FROM personne p
JOIN engin e            ON e.id = p.enginId
JOIN mouvementstock mvs ON p.mvsId = mvs.id

-- Diagnostic rapide sur la table Personne
SELECT
    COUNT(*)                            AS nb_total,
    SUM(CASE WHEN enginId IS NOT NULL THEN 1 ELSE 0 END)  AS avec_enginId,
    SUM(CASE WHEN mvsId IS NOT NULL THEN 1 ELSE 0 END)    AS avec_mvsId,
    SUM(CASE WHEN enginId IS NOT NULL 
             AND mvsId IS NOT NULL THEN 1 ELSE 0 END)     AS avec_les_deux
FROM personne;

SELECT
    id, nom, prenom, enginId, mvsId
FROM personne
LIMIT 20;

-- Combien d'entités sont liées à un même formulaire CRB ?
SELECT
    f.id            AS formulaire_id,
    f.code,
    COUNT(ent.id)   AS nb_entites_liees,
    GROUP_CONCAT(ent.fonction) AS fonctions
FROM formulaire f
JOIN entite ent ON ent.formulaireId = f.id
WHERE f.code = 'CRB'
GROUP BY f.id
LIMIT 20;

-- Vérifier la cohérence : un seul engin par formulaire CRB ?
SELECT
    f.id            AS formulaire_id,
    f.debut,
    e.identifiant   AS engin,
    m.quantite      AS litres
FROM mouvementstock m
JOIN formulaire f   ON f.id = m.formulaireId
JOIN entite ent     ON ent.formulaireId = f.id AND ent.fonction = 'EQ-5003'
JOIN engin e        ON e.entiteId = ent.id
WHERE m.produit = 'Gasoil'
  AND f.code = 'CRB'
ORDER BY f.debut
LIMIT 20;


-- Consommation carburant par engin, avec nombre de pleins et litres totaux
WITH carburant_engin AS (
    SELECT
        e.identifiant             AS engin,
        e.type                    AS type_engin,
        e.marque,
        COUNT(DISTINCT m.id)      AS nb_pleins,
        SUM(m.quantite)           AS litres_total,
        ROUND(AVG(m.quantite), 1) AS litres_moy_par_plein
    FROM mouvementstock m
    JOIN formulaire f   ON f.id            = m.formulaireId
    JOIN entite ent     ON ent.formulaireId = f.id
                       AND ent.fonction     = 'EQ-5003'
    JOIN engin e        ON e.entiteId       = ent.id
    WHERE m.produit = 'Gasoil'
    GROUP BY e.identifiant, e.type, e.marque, e.modele
),
km_engin AS (
    SELECT
        Engin_Immatriculation     AS engin,
        SUM(distance_km)          AS km_total,
        COUNT(*)                  AS nb_missions
    FROM v_missions
    WHERE distance_km BETWEEN 1 AND 300
    GROUP BY Engin_Immatriculation
)
SELECT
    c.engin,
    c.type_engin,
    c.marque,
    c.nb_pleins,
    k.nb_missions,
    ROUND(c.litres_total, 0)                                AS litres_total,
    ROUND(k.km_total, 0)                                    AS km_total,
    ROUND(c.litres_total / NULLIF(k.km_total, 0) * 100, 1) AS L_pour_100km,
    ROUND(c.litres_total * 1.60, 0)                         AS cout_estime_euros
FROM carburant_engin c
LEFT JOIN km_engin k ON k.engin = c.engin
ORDER BY litres_total DESC;

-- voir les engins les plus consommateurs, même sans info km
SELECT
    e.identifiant        AS engin,
    e.type               AS type_engin,
    e.marque,
    COUNT(DISTINCT m.id) AS nb_pleins,
    SUM(m.quantite)      AS total_litres,
    AVG(m.quantite)      AS moy_litres_par_plein
FROM mouvementstock m
JOIN formulaire f  ON f.id       = m.formulaireId
JOIN entite ent    ON ent.formulaireId = f.id
                   AND ent.fonction    = 'EQ-5003'   -- filtre clé : évite ×4 doublons
JOIN engin e       ON e.entiteId  = ent.id
WHERE m.produit = 'Gasoil'
GROUP BY e.identifiant, e.type, e.marque
ORDER BY total_litres DESC;

-- Détail des pleins pour vérifier la cohérence
SELECT
    e.identifiant       AS engin,
    f.debut             AS date_plein,
    m.quantite          AS litres,
    m.espaceOrigine     AS lieu,
    -- Jours écoulés depuis le plein précédent
    DATEDIFF(f.debut, LAG(f.debut) OVER (
        PARTITION BY e.identifiant ORDER BY f.debut
    ))                  AS jours_depuis_dernier_plein
FROM mouvementstock m
JOIN formulaire f   ON f.id            = m.formulaireId
JOIN entite ent     ON ent.formulaireId = f.id
                   AND ent.fonction     = 'EQ-5003'
JOIN engin e        ON e.entiteId       = ent.id
WHERE m.produit = 'Gasoil'
ORDER BY e.identifiant, f.debut;

-- Approche directe : on évite toute jointure intermédiaire ambiguë
SELECT
    e.identifiant                               AS engin,
    e.type                                      AS type_engin,

    -- Km capturés dans v_missions (trajets chargés uniquement)
    vm.km_missions,

    -- Km odomètre : MAX kilométrage livraison - MIN kilométrage retrait
    -- sur toute la période, par engin
    od.km_max_livraison - od.km_min_retrait     AS km_odometre_estime,

    -- Ratio : combien de km réels pour 1 km de mission
    ROUND(
        (od.km_max_livraison - od.km_min_retrait)
        / NULLIF(vm.km_missions, 0)
    , 2)                                        AS ratio_odometre_vs_missions

FROM engin e

-- Km missions : agrégation déjà propre dans v_missions
LEFT JOIN (
    SELECT
        Engin_Immatriculation       AS engin,
        SUM(distance_km)            AS km_missions
    FROM v_missions
    WHERE distance_km BETWEEN 1 AND 300
    GROUP BY Engin_Immatriculation
) vm ON vm.engin = e.identifiant

-- Km odomètre : MIN retrait et MAX livraison par engin
LEFT JOIN (
    SELECT
        r.enginId,
        MIN(r.kilometrageDebut)     AS km_min_retrait,
        MAX(l.kilometrageDebut)     AS km_max_livraison
    FROM retrait r
    JOIN livraison l ON l.enginId = r.enginId
    GROUP BY r.enginId
) od ON od.enginId = e.id

WHERE vm.km_missions IS NOT NULL
ORDER BY vm.km_missions DESC
LIMIT 40;


