# Fondations natives C++20 et contrats structurels partagés (#235, #237)

Source normative unique : [tllib-specs@07439bab](https://github.com/Tradition-Learning-Community/tllib-specs/tree/07439babd59c657354e3200ed24c55e2e3eeb72c/handoff/shared). Ce document décrit seulement les choix techniques d'implémentation. Aucune logique scientifique des domaines n'est répliquée.

## API publique

- include/tllib/core/identity.hpp : FeatureId, DomainId, Version, Fingerprint, PackageStatus, ScientificStatus, ExecutionStatus. La grammaire FeatureId suit le schéma du handoff ; aucune normalisation de casse.
- include/tllib/core/result.hpp : Result<T> contient soit une valeur soit une Error ; accès const-only à la valeur ; Error garde code technique, stable_code original, identifiant TLC-FC, provenance, message et contexte.
- include/tllib/shared/contracts.hpp : types structurels natifs, validateurs, dépendances vérifiées sans cycle et transport canonique.

## Correspondances normatives

| Contrat tllib-specs@07439bab | Porteur C++ | Acceptations |
| --- | --- | --- |
| TLC-HC-FEATURE-ID | core::FeatureId | HC-FID-001 à 003 |
| TLC-HC-SCIENTIFIC-REFERENCE | shared::ScientificReference | HC-SREF-001 à 003 |
| TLC-HC-REFERENCE-COLLECTION | shared::ReferenceCollection | HC-RCOL-001 à 003 |
| TLC-HC-UNRESOLVED-ITEM | shared::UnresolvedItem | HC-UNR-001 à 003 |
| TLC-HC-OPAQUE-VALUE | shared::OpaqueValue | HC-OPA-001 à 003 |
| TLC-HC-STRUCTURED-ERROR | shared::StructuredError | HC-ERR-001 à 003 |
| TLC-HC-TRACEABILITY | shared::Traceability | HC-TRC-001 à 003 |
| TLC-HC-DESCRIPTOR-ENVELOPE | shared::DescriptorEnvelope | HC-ENV-001 à 003 |

Contrats complets et acceptations : [handoff/shared](https://github.com/Tradition-Learning-Community/tllib-specs/tree/07439babd59c657354e3200ed24c55e2e3eeb72c/handoff/shared). Les tests natifs utilisent leurs exemples valides, invalides et de préservation comme références, sans recopier les spécifications.

## Règles techniques observables

1. TLHC/1.0.0 est un cadrage binaire canonique interne à champs de taille préfixée. L'encodage est déterministe et préserve les octets opaques et les champs ordonnés. Il n'est ni une sérialisation JSON normative, ni un format scientifique de domaine. La lecture vérifie le cadrage, le type et la version ; les objets typés doivent être validés avant publication.
2. Toute version partagée différente de 1.0.0 est rejetée. Les dépendances entre les huit contrats sont acycliques, vérifiées à la compilation.
3. Une référence rejette chemin absolu, traversée parent, séparateur vide, chemin Windows et intervalle de lignes invalide. Elle conserve les champs de provenance exactement. La résolution des références est explicite via un callback fourni par l'appelant, sans réseau caché.
4. Les collections distinguent identités opaques et références de provenance, respectent la cardinalité, le caractère map/set, les doublons interdits et l'ordre source. Elles ne prétendent pas fixer un conteneur scientifique ou un backend.
5. Un état unresolved n'est jamais implicitement résolu. Une OpaqueValue ne subit aucune interprétation, conversion, évaluation ni normalisation de payload. La représentation est propriétaire des octets et des chaînes ; aucune durée de vie empruntée.
6. StructuredError conserve le code stable, le contexte et le TLC-FC à travers to_core_error ; le texte du message ne sert pas d'identité. Result<T> n'expose aucun résultat partiel.
7. Un descripteur peut avoir un objet status vide, conformément à HC-ENV-001 ; des statuts scientifiques ne sont jamais inventés par défaut. Les statuts fournis sont des enums fermés.

## Compiler et tester

    cmake -S . -B build/native-core -DBUILD_TESTING=ON
    cmake --build build/native-core --parallel 2
    ctest --test-dir build/native-core --output-on-failure

Le workflow ciblé Native core C++20 exécute les mêmes commandes sur les PR qui touchent les sources natives. Les résultats prouvent les mécanismes structurels natifs, et non une exécution ou certification des 694 fonctionnalités scientifiques.

## Hors périmètre

Runtime, providers, concurrence, génération automatique depuis les specs, bindings Python, backends numériques, installation Python et conformité complète des features relèvent de leurs propres issues. Les futures versions de wire nécessiteront un arbitrage explicite de compatibilité.
