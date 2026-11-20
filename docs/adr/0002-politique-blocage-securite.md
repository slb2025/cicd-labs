# ADR 0002 — Politique de blocage sécurité en CI/CD

- **Statut** : accepté
- **Date** : 2026-11-20

## Contexte
La pipeline `Security (DevSecOps)` exécute des contrôles SAST (`Bandit`, `Ruff`), SCA (`pip-audit`), conteneur (`Trivy`, SBOM `CycloneDX`) et DAST (`OWASP ZAP`). Lors des exécutions sur l'image `minishop` (`debian 13.7`), Trivy a signalé des vulnérabilités `HIGH` dans des paquets système sans correctif disponible, tandis que `zap-baseline.py` retournait un code `2` sur de simples avertissements.

## Options étudiées
| Critère | Bloquer sur toute alerte / tout `HIGH` | Bloquer sur `HIGH`/`CRITICAL` corrigeable et `--ignore-unfixed` en CI | Ignorer toutes les alertes de sécurité |
|---|---|---|---|
| Prévention des failles exploitables | Élevée | Élevée | Nulle |
| Risque de faux blocages sur PR/main | Élevé (CVE système sans fix) | Faible | Nul |
| Visibilité des écarts restants | Totale dans les logs | Conservée via rapports/SBOM et runs planifiés | Aucune |

## Décision
Bloquer la pipeline sur les vulnérabilités `HIGH` ou `CRITICAL` disposant d'un correctif (`pip-audit`), ignorer les CVE système sans correctif (`--ignore-unfixed`) sur `Trivy` en CI, et ne faire échouer `zap-baseline.py` que sur les règles passées en `FAIL` (`-I` avec `10021` en `FAIL` dans `security/zap-rules.tsv`).

## Conséquences
- Les failles corrigeables et les règles `FAIL` bloquent immédiatement l'intégration.
- Les CVE sans correctif et les avertissements `WARN` restent traçables dans les artefacts (SBOM `CycloneDX`, rapport `ZAP`) sans paralyser la livraison continue.
