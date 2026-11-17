# Stratégie de test — MiniShop

> Modèle à compléter pendant l'Atelier 12. Une stratégie de test tient sur 2 pages : si elle est plus longue, personne ne la lit.

## 1. Périmètre et risques
| Zone | Risque métier | Probabilité | Impact | Niveau de test principal |
|---|---|---|---|---|
| Calcul des prix (`pricing.py`) | Mauvais montant facturé | Moyenne | Élevé | Unitaire + génération IA |
| API commandes | Commande perdue | Faible | Élevé | API + contrat |
| Interface | Parcours bloqué | Moyenne | Moyen | E2E + visuel |
| Performance | Abandon de panier | … | … | Charge (Locust/JMeter) |
| Sécurité | Fuite / injection | … | … | SAST, SCA, DAST (ZAP) |

## 2. Pyramide et quality gates
| Étape pipeline | Tests | Seuil bloquant |
|---|---|---|
| PR | lint, unitaires, API | 100 % OK, couverture ≥ 85 % |
| main | + E2E, visuel, sécurité | 0 vulnérabilité HIGH/CRITICAL |
| nocturne | charge, ZAP complet | p95 < 300 ms, erreurs < 1 % |

## 3. Règles pour les tests générés par IA
- **Traçabilité obligatoire** : tout test issu d'un LLM porte le marqueur `pytestmark = [pytest.mark.generated, pytest.mark.unit]` et vit dans `tests/generated/`.
- **Relecture humaine avant merge** : aucun test généré n'est fusionné sans audit des assertions, des bornes exactes (`>=` vs `>`) et des divergences éventuelles (`# DIVERGENCE SPEC/CODE`).
- **Preuve par mutation** : la couverture ne suffit pas ; tout lot généré doit être validé par `ai_tools/mutation_score.py` (cible ≥ 80 %, référence mesurée sur `pricing.py` : 84 % LLM vs 89 % manuel et 71 % offline).
- **Confidentialité des prompts** : interdiction stricte d'envoyer des secrets, clés API, données personnelles (PII) ou dumps de production à un fournisseur externe ; privilégier les spécifications Gherkin et le code métier anonymisé (ou `LLM_PROVIDER=offline` / modèle local).
- **Responsabilité** : le développeur ou QA qui ouvre la Pull Request reste **entièrement responsable** de la pertinence et de la maintenance des tests générés qu'il soumet, au même titre que du code écrit à la main.

## 4. Gestion des tests instables (flaky)
- Détection : `ai_tools/test_history.py` (score ≥ 0,6).
- Quarantaine : marqueur `flaky`, ticket ouvert, délai de correction 5 jours.

## 5. Indicateurs suivis
Taux de réussite sur main, durée de la suite, nombre de tests flaky, couverture, MTTR d'une régression.
