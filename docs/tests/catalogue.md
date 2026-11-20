# Catalogue des tests

_Généré automatiquement le 20/11/2026 14:45 — ne pas éditer à la main._
**77 tests** — 77 documentés (100%).


## `tests/api/test_api_smoke.py`

Tests d'API MiniShop — Parties A & B (Atelier 9).

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| ✅ | `test_health` | api | Vérifie que l'endpoint /health répond 200 avec le statut ok. | 0.01s |
| ✅ | `test_liste_produits` | api | Vérifie que GET /products retourne le catalogue complet des produits. | 0.01s |
| ✅ | `test_produit_par_id_200` | api | Vérifie que GET /products/{id} retourne le détail d'un produit existant. | 0.00s |
| ✅ | `test_produit_inconnu_404` | api | Vérifie que GET /products/{id} retourne 404 pour un identifiant inconnu. | 0.01s |
| ✅ | `test_cart_quote_200_avec_coupon` | api | Vérifie le calcul de devis via POST /cart/quote avec application d'un coupon valide. | 0.00s |
| ✅ | `test_cart_quote_produit_inconnu_404` | api | Vérifie que POST /cart/quote retourne 404 si un produit du panier est inconnu. | 0.00s |
| ✅ | `test_cart_quote_erreurs_validation_422` (paramétré) | api, parametrize | Vérifie que POST /cart/quote rejette les charges utiles invalides avec 422. | 0.02s |
| ✅ | `test_creation_et_lecture_commande_201_puis_200` | api | Vérifie la création d'une commande (201) puis sa consultation par identifiant (200). | 0.01s |
| ✅ | `test_commande_inconnue_404` | api | Vérifie que GET /orders/{id} retourne 404 pour une commande inexistante. | 0.00s |
| ✅ | `test_creation_commande_panier_vide_422` | api | Vérifie que POST /orders refuse la création d'une commande sur panier vide (422). | 0.00s |
| ✅ | `test_metrics_expose_compteur_http` | api | Vérifie que l'endpoint /metrics expose les compteurs Prometheus des requêtes HTTP. | 0.01s |
| ✅ | `test_contrat_openapi_routes_et_types` | api | Vérifie la conformité des routes et schémas exposés dans /openapi.json. | 0.02s |
| ⏭ | `test_variante_serveur_reel_httpx` | api, skipif | Vérifie le fonctionnement de l'API contre une instance serveur réelle via HTTPX. | 0.00s |

## `tests/e2e/test_parcours_achat.py`

Tests fonctionnels UI de bout en bout Playwright (Atelier 8).

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| · | `test_page_accueil` | e2e | Vérifie l'affichage du titre et du catalogue de produits sur la page d'accueil. | 0.00s |
| · | `test_parcours_achat_avec_coupon_et_commande` | e2e | Vérifie le parcours E2E complet d'ajout au panier, coupon et validation de commande. | 0.00s |
| · | `test_coupon_invalide_affiche_alerte` | e2e | Vérifie l'affichage d'un message d'alerte lors de la saisie d'un coupon invalide. | 0.00s |
| · | `test_bouton_commander_desactive_si_panier_vide` | e2e | Vérifie que le bouton Commander reste désactivé tant que le panier est vide. | 0.00s |

## `tests/e2e/test_selenium_accueil.py`

Test UI comparatif avec Selenium WebDriver (Atelier 8 — Partie B).

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| · | `test_selenium_titre_et_ajout_produit` | e2e | Vérifie avec Selenium le chargement de l'accueil et l'ajout d'un produit au panier. | 0.00s |

## `tests/generated/test_pricing_ai.py`

Tests pytest du calcul de panier MiniShop (minishop.pricing).

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| ✅ | `test_panier_vide` | generated, unit | Un panier vide a un total nul et aucuns frais de livraison. | 0.00s |
| ✅ | `test_achat_simple_avec_frais_de_livraison` | generated, unit | Un panier sous 50 € après remise paie des frais de livraison de 4,90 €. | 0.00s |
| ✅ | `test_livraison_offerte_a_partir_de_50_euros` | generated, unit | La livraison est offerte quand le total après remise atteint 50 € ou plus. | 0.00s |
| ✅ | `test_remise_volume_des_10_unites` | generated, unit | Dès 10 stickers, une remise volume de 5 % s'applique à la ligne. | 0.00s |
| ✅ | `test_coupon_de_bienvenue` | generated, unit | WELCOME10 applique 10 % de remise quand le sous-total atteint 20 €. | 0.00s |
| ✅ | `test_coupon_de_bienvenue_sous_le_seuil` | generated, unit | WELCOME10 n'accorde aucune remise si le sous-total est inférieur à 20 €. | 0.00s |
| ✅ | `test_coupon_de_livraison_offerte` | generated, unit | FREESHIP offre la livraison sans appliquer de remise sur les articles. | 0.00s |
| ✅ | `test_coupon_inconnu` | generated, unit | Un code coupon non répertorié lève une erreur 'Coupon inconnu'. | 0.00s |
| ✅ | `test_produit_inconnu` | generated, unit | Un produit absent du catalogue lève une erreur 'Produit inconnu'. | 0.00s |
| ✅ | `test_coupon_etudiant_sans_minimum_d_achat` | generated, unit | STUDENT15 applique 15 % de remise sans minimum d'achat. | 0.00s |
| ✅ | `test_coupon_etudiant_non_cumulable_avec_la_remise_volume` | generated, unit | STUDENT15 ne s'applique pas aux lignes bénéficiant de la remise volume. | 0.00s |
| ✅ | `test_coupon_etudiant_sur_panier_mixte` | generated, unit | STUDENT15 ne remise que les lignes sans remise volume dans un panier mixte. | 0.00s |
| ✅ | `test_limite_seuil_remise_volume` (paramétré) | generated, unit, parametrize | La remise volume s'applique exactement à partir de 10 unités, pas avant. | 0.00s |
| ✅ | `test_limite_quantite_hors_bornes` (paramétré) | generated, unit, parametrize | Une quantité hors de l'intervalle 1..99 lève une ValueError. | 0.00s |
| ✅ | `test_limite_quantite_bornes_incluses` (paramétré) | generated, unit, parametrize | Les bornes 1 et 99 sont des quantités valides. | 0.00s |
| ✅ | `test_limite_quantite_non_entiere` (paramétré) | generated, unit, parametrize | Une quantité qui n'est pas un entier (y compris booléen) lève une ValueError. | 0.00s |
| ✅ | `test_limite_quantite_zero_dans_devis` | generated, unit | Une quantité nulle dans un devis lève une ValueError. | 0.00s |
| ✅ | `test_limite_livraison_exactement_au_seuil` | generated, unit | Un total après remise exactement égal à 50 € obtient la livraison offerte. | 0.00s |
| ✅ | `test_limite_livraison_juste_sous_le_seuil` | generated, unit | Un total de 37.50 € paie la livraison standard. | 0.00s |
| ✅ | `test_limite_remise_coupon_fait_repasser_sous_le_seuil` | generated, unit | La livraison se calcule après remise : WELCOME10 fait repasser le total sous 50 €. | 0.00s |
| ✅ | `test_limite_freeship_sur_petit_panier` | generated, unit | FREESHIP supprime la livraison même sur un panier très en dessous de 50 €. | 0.00s |
| ✅ | `test_limite_welcome10_applique_apres_remise_volume` | generated, unit | WELCOME10 s'applique sur le sous-total déjà réduit par la remise volume. | 0.00s |
| ✅ | `test_limite_fixed5_sous_le_seuil` | generated, unit | FIXED5 n'accorde rien quand le sous-total est inférieur à 30 €. | 0.00s |
| ✅ | `test_limite_fixed5_au_dessus_du_seuil` | generated, unit | FIXED5 accorde 5 € de remise à partir de 30 € de sous-total. | 0.00s |
| ✅ | `test_limite_student15_sur_remise_volume_partielle` | generated, unit | STUDENT15 ne remise que la ligne sans remise volume dans un panier de 9 mugs. | 0.00s |
| ✅ | `test_limite_code_coupon_insensible_a_la_casse_et_aux_espaces` (paramétré) | generated, unit, parametrize | Les codes coupon sont normalisés (espaces retirés, casse ignorée). | 0.00s |
| ✅ | `test_limite_coupon_vide_equivalent_a_aucun_coupon` | generated, unit | Une chaîne de coupon vide ne déclenche aucune remise. | 0.00s |
| ✅ | `test_limite_arrondi_commercial_au_centime` (paramétré) | generated, unit, parametrize | Les montants sont arrondis au centime en ROUND_HALF_UP. | 0.00s |
| ✅ | `test_limite_arrondi_remise_student_demi_centime` | generated, unit | La remise STUDENT15 sur 12.50 € (1.875 €) est arrondie à 1.88 €. | 0.00s |
| ✅ | `test_limite_sous_total_est_somme_des_lignes` | generated, unit | Le sous-total est la somme exacte des totaux de lignes. | 0.00s |
| ✅ | `test_limite_devis_as_dict_montants_en_chaine_decimale` | generated, unit | La sérialisation expose les montants sous forme de chaînes décimales à 2 chiffres. | 0.00s |

## `tests/generated/test_pricing_offline.py`

Tests générés automatiquement depuis pricing.feature (moteur : offline).

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| ✅ | `test_panier_vide` | generated, unit | Panier vide | 0.00s |
| ✅ | `test_achat_simple_avec_frais_de_livraison` | generated, unit | Achat simple avec frais de livraison | 0.00s |
| ✅ | `test_livraison_offerte_a_partir_de_50_euros` | generated, unit | Livraison offerte à partir de 50 euros | 0.00s |
| ✅ | `test_remise_volume_des_10_unites` | generated, unit | Remise volume dès 10 unités | 0.00s |
| ✅ | `test_coupon_de_bienvenue` | generated, unit | Coupon de bienvenue | 0.00s |
| ✅ | `test_coupon_de_bienvenue_sous_le_seuil` | generated, unit | Coupon de bienvenue sous le seuil | 0.00s |
| ✅ | `test_coupon_de_livraison_offerte` | generated, unit | Coupon de livraison offerte | 0.00s |
| ✅ | `test_coupon_inconnu` | generated, unit | Coupon inconnu | 0.00s |
| ✅ | `test_produit_inconnu` | generated, unit | Produit inconnu | 0.00s |
| ✅ | `test_coupon_etudiant_sans_minimum_d_achat` | generated, unit | Coupon étudiant sans minimum d'achat | 0.00s |
| ✅ | `test_coupon_etudiant_non_cumulable_avec_la_remise_volume` | generated, unit | Coupon étudiant non cumulable avec la remise volume | 0.00s |
| ✅ | `test_coupon_etudiant_sur_panier_mixte` | generated, unit | Coupon étudiant sur panier mixte | 0.00s |

## `tests/unit/test_pricing.py`

Tests unitaires des règles de prix.

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| ✅ | `test_money_arrondi_commercial` (paramétré) | unit, parametrize | Vérifie l'arrondi commercial au centime supérieur (ROUND_HALF_UP). | 0.00s |
| ✅ | `test_line_total_sans_remise` | unit | Vérifie le calcul du total d'une ligne sans remise de volume. | 0.00s |
| ✅ | `test_line_total_remise_volume_limites` (paramétré) | unit, parametrize | Vérifie le seuil d'application de la remise de volume de 5 % à partir de 10 unités. | 0.00s |
| ✅ | `test_line_total_quantite_invalide` (paramétré) | unit, parametrize | Vérifie le rejet par ValueError des quantités nulles, négatives, hors bornes ou non entières. | 0.00s |
| ✅ | `test_coupon_discount_valide` (paramétré) | unit, parametrize | Vérifie le calcul des remises pour les coupons valides et leurs seuils d'activation. | 0.00s |
| ✅ | `test_coupon_inconnu_leve_value_error` (paramétré) | unit, parametrize | Vérifie qu'un code coupon inconnu lève une exception ValueError. | 0.00s |
| ✅ | `test_shipping_cost_limites` (paramétré) | unit, parametrize | Vérifie la gratuité des frais de port à partir de 50 € ou avec le coupon FREESHIP. | 0.00s |
| ✅ | `test_quote_panier_vide` | unit | Vérifie le calcul d'un devis sur panier vide (sous-total et frais de port à 0,00 €). | 0.00s |
| ✅ | `test_quote_produit_inconnu` | unit | Vérifie qu'un devis contenant un produit inconnu lève une exception KeyError. | 0.00s |
| ✅ | `test_quote_seuil_fixed5_sur_book` | unit | Vérifie l'activation du coupon FIXED5 dès 30,00 € d'achat sur un article. | 0.00s |
| ✅ | `test_quote_livraison_facturee_si_total_passe_sous_50_apres_remise` | unit | Vérifie la facturation du port lorsque la remise fait passer le total sous 50,00 €. | 0.00s |
| ✅ | `test_student15_sans_minimum_et_sans_remise_volume` | unit | Vérifie la remise de 15 % du coupon STUDENT15 sans minimum d'achat sur ligne sans remise volume. | 0.00s |
| ✅ | `test_student15_non_cumulable_si_remise_volume` | unit | Vérifie que STUDENT15 ne se cumule pas sur une ligne bénéficiant déjà de la remise volume. | 0.00s |
| ✅ | `test_student15_panier_mixte_applique_uniquement_lignes_sans_volume` | unit | Vérifie l'application sélective de STUDENT15 aux seules lignes sans remise volume d'un panier mixte. | 0.00s |

## `tests/visual/test_visual.py`

Tests de régression visuelle (Atelier 7).

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| · | `test_accueil` | visual | Vérifie la non-régression visuelle de la page d'accueil par comparaison SSIM. | 0.00s |
| · | `test_panier_avec_total` | visual | Vérifie la non-régression visuelle du panier après calcul du devis. | 0.00s |
