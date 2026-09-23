# XIV Databar Forever — 5.7.2-forever-beta.1

**Portage pour WoW Forever 1.60.1 (`_classic_beta_`).**
Testé avec succès dans le client (connexion, barre et modules fonctionnels).
Le dépôt de référence reste
<https://github.com/ZelionGG/XIV_Databar-Continued>.

## Installation

1. Quitter complètement WoW. Sauvegarder le dossier existant de l'addon et ses
   fichiers `WTF/Account/.../SavedVariables/XIV_Databar_Continued.lua` et `.bak`.
2. Télécharger l'archive **XIV_Databar_Forever-5.7.2-forever-beta.1.zip** fournie
   avec la version de test. **Ne pas utiliser « Code → Download ZIP »** : le
   dépôt source ne contient pas les bibliothèques nécessaires.
3. Déplacer l'ancien dossier de l'addon hors de `Interface/AddOns`, puis extraire
   le ZIP dans `D:\World of Warcraft\_classic_beta_\Interface\AddOns\`.
4. Vérifier le chemin final :
   `Interface\AddOns\XIV_Databar_Continued\XIV_Databar_Continued.toc`.
   Ne pas renommer le dossier en `XIV-Databar-Forever`.
5. Tester d'abord avec **XIV seul**, puis ouvrir `/xivc`.

## Modifications

- Manifest `XIV_Databar_Continued_Camelot.toc`, interface **16001**. Le ZIP
  contient uniquement le manifeste générique pour éviter de sélectionner un
  ancien manifeste Retail/Vanilla. Les sources gardent leurs autres variantes.
- Détection Forever distincte du contenu Retail : Forever expose les API
  Mainline (`WOW_PROJECT_ID = 1`), ce n'est pas le client Era.
- API `C_SpecializationInfo` pour les talents, `C_Item.IsUsableItem` pour les
  objets et `C_CurrencyInfo.GetCoinTextureString` pour les pièces ; replis vers
  les anciens globals conservés.
- Identité de personnage et royaume alignée sur AceDB (PvE/PvP/RP/Hardcore).
- AceDB avec la correction Forever officielle de la bibliothèque, révision 36.
- Pas de Grande chambre forte, de logement ni de téléportations Mythique+ dans
  cette variante ; pas de recherche de pierre de Dalaran au démarrage.
- Les réponses `GUILD_ROSTER_UPDATE` n'entraînent plus de nouvelle requête.
  Les autres rafraîchissements partagent une limite d'une requête par 10 s.
- LibDataBroker chargé comme Script Lua, et non Include XML.

## Vérification

Les tests exécutent du vrai code Lua 5.1 avec des API WoW simulées aux frontières.
Ils ne reproduisent ni le réseau, ni le moteur graphique, ni les restrictions
sécurisées du client ; ils complètent donc le test en jeu, sans le remplacer.

Validé dans le client Forever 1.60.1 : chargement de l'addon et affichage de la
barre avec ses modules. Si un module précis pose problème, signaler les étapes
et la première erreur Lua complète.

- [x] Connexion avec XIV et affichage correct de la barre.
- [ ] `/xivc`, modification des options, rechargement `/reload`.
- [ ] Argent/sacs, durabilité, XP/monnaies, réputation, métiers et horloge.
- [ ] Pierre de foyer et menus ; talents et changements de configuration.
- [ ] Combat, sortie de combat, changement de zone et déconnexion/reconnexion.
- [ ] Persistance après fermeture complète du client.

Pour les erreurs Lua : `/console scriptErrors 1`, puis `/reload`. Copier **la
première erreur complète**, avec le moment précis et le numéro de build. Pour
une simple déconnexion sans crash, noter l'heure, tout code `WOW519...`, et si
elle survient aussi sans addon. Un rapport `Errors` plus ancien peut correspondre
à un autre incident. Pour désactiver l'affichage : `/console scriptErrors 0`.

Des builds de la bêta ont des défauts de SavedVariables et d'exécution des
scripts sécurisés. Cette version ne remplace pas les fonctions sécurisées de
Blizzard et ne modifie pas la configuration réseau ou les fichiers du jeu.

## Construction et tests

Python 3.10+ pour le packager ; Python 3.12 est la version de validation.

```sh
python3 -m venv .venv
.venv/bin/pip install -r tests/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
python3 scripts/package_forever.py --output dist/XIV_Databar_Forever-5.7.2-forever-beta.1.zip
```

Sous Windows, remplacer `.venv/bin/python` par `.venv\Scripts\python.exe`.
Le packager télécharge de vraies bibliothèques, vérifie leurs SHA-256, conserve
les licences incluses, valide récursivement les références TOC/XML, puis crée
un ZIP à métadonnées fixes. Les fichiers SVN sont verrouillés par empreinte :
un changement upstream provoque un échec explicite, pas une mise à jour muette.
Aucun envoi à CurseForge/Wago/WoWInterface n'est effectué.

## Sources de compatibilité

- [Blizzard UI extrait, build 1.60.1.69977](https://github.com/Gethe/wow-ui-source/commit/c6e89983189e4f626f549204a23c2d2bea93080a)
- [Capture des API Forever, build 69893](https://github.com/Thunderz96/forever-addon-kit/blob/main/data/forever_api.json)
- [Correction AceDB Forever](https://github.com/WoWUIDev/Ace3/commit/1e98fc00874779334d7a3f0cb399c7ae9a15fead)
- [Manifest Camelot testé dans Interaction](https://github.com/Adaptvx/Interaction/pull/95)

L'existence d'une fonction dans une capture n'assure pas que toute fonctionnalité
Retail soit disponible ou stable dans Forever.
