# WiZ Advanced

[![Validate](https://github.com/chamo1101/hacs-wiz-advanced/actions/workflows/validate.yml/badge.svg)](https://github.com/chamo1101/hacs-wiz-advanced/actions/workflows/validate.yml)

Custom integration Home Assistant qui ajoute le pilotage fin des ampoules **WiZ** en local
(UDP 38899), là où l'intégration officielle `wiz` s'arrête.

Aucun cloud, aucune dépendance Python, aucun compte : uniquement le réseau local.

## Pourquoi cette intégration

L'intégration `wiz` du cœur de Home Assistant expose marche/arrêt, intensité, température de blanc
et 16 effets. Elle ne remonte pas :

| Manque dans HA | Apport de WiZ Advanced |
|---|---|
| Scène **Dim-to-warm** (id 40) absente de la liste | Sélecteur complet des **17 scènes** du firmware |
| `number.*_effect_speed` souvent `unavailable` | Entité **Vitesse** fonctionnelle (scènes animées) |
| Aucun retour d'état réel (scène, RSSI, vitesse) | Capteur **État** + capteur de connectivité |

## Entités créées

- `select.wiz_scene` — les 17 scènes (Cozy, Wake-up, Bedtime, Warm white, Daylight, Cool white,
  Night light, Focus, Relax, TV time, Candlelight, Golden white, Pulse, Steampunk, Diwali, Alarm,
  **Dim-to-warm**)
- `number.wiz_speed` — vitesse des scènes animées (Pulse, Steampunk, Diwali), 20–200 %
- `sensor.wiz_state` — scène courante + attributs : allumée, intensité, température de blanc,
  vitesse, RSSI, IP
- `binary_sensor.wiz_online` — joignabilité de l'ampoule

## Installation (HACS)

1. HACS → ⋮ → **Dépôts personnalisés**
2. Ajouter `https://github.com/chamo1101/hacs-wiz-advanced` avec la catégorie **Integration**
3. Installer **WiZ Advanced**, puis redémarrer Home Assistant
4. **Paramètres → Appareils et services → Ajouter une intégration → WiZ Advanced** → saisir l'IP
   de l'ampoule (elle reste sur le même réseau, port UDP 38899)

Installation manuelle : copier `custom_components/wiz_advanced` dans le dossier `config/custom_components/`
puis redémarrer.

## Coexistence avec l'intégration officielle

Les deux peuvent tourner en même temps : gardez `wiz` pour l'allumage, l'intensité et la
température de blanc, et utilisez WiZ Advanced pour les scènes et la vitesse. Cette intégration
ne crée volontairement **aucune** entité `light` pour éviter un doublon.

## Limites matérielles (vérifiées sur module `ESP21_SHTW_01`, firmware 1.38.0)

- **Rhythm / rythme circadien** (`sceneId 1000`) : refusé par le firmware (`-32602 Invalid params`)
- **Scènes RGB** (Ocean, Party, Fireplace, Forest…) : acceptées en apparence puis ignorées — les
  modules *tunable white* ne savent pas les afficher
- **Fondu entrée/sortie, préréglages WiZclick, minDimming** : `setUserConfig` répond
  `-32600 Invalid Request` sur ce firmware, ils ne sont donc pas exposés
- Choisir une scène **allume** l'ampoule : c'est le comportement du firmware, pas de l'intégration

## Testé

- Ampoule : WiZ Tunable White (module `ESP21_SHTW_01`, firmware 1.38.0)
- Home Assistant : 2026.11.1
- Validation de code : `tests/test_imports.py` (stubs HA) + `tests/test_api.py` (aller-retour UDP réel)

## Avertissement

Projet indépendant, non affilié à WiZ, Signify ou à la fondation Open Home Foundation.
