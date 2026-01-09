# SwitchZ - Riot Account Switcher

SwitchZ est un gestionnaire de comptes League of Legends moderne et rapide. Il permet de changer de compte instantanément sans avoir à retaper son mot de passe, avec une interface Dark Mode et un suivi automatique du rang (LP/Division).

![SwitchZ Interface]([https://via.placeholder.com/600x400?text=Screenshot+de+SwitchZ](https://image.noelshack.com/fichiers/2026/02/6/1768001579-capture-d-cran-2026-01-10-003237.png)) 

## Fonctionnalités
- **Connexion Instantanée** : Changez de compte en un clic.
- **Auto Rank Tracker** : Affiche automatiquement votre rang (ex: Gold IV - 50 LP) en interrogeant le client LoL.
- **Safe Logout** : Système de déconnexion propre pour éviter l'invalidation des sessions.
- **Interface Moderne** : Design sombre avec CustomTkinter.
- **Léger** : Ne tourne pas en fond quand vous jouez.

## Installation

### Prérequis
1. Avoir [Python](https://www.python.org/downloads/) installé (cochez "Add to PATH" à l'installation).
2. Avoir le client Riot Games installé.

### Étapes
1. Clonez ce dépôt ou téléchargez le fichier ZIP.
2. Ouvrez un terminal dans le dossier.
3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
4. Lancez l'application : python switchz.py

Comment ajouter vos comptes ?
SwitchZ fonctionne par "capture de session". Vous ne donnez pas votre mot de passe au logiciel, il copie simplement votre session active.

Lancez SwitchZ.

Cliquez sur le bouton "Safe Logout (Ajouter compte)" (en bas en rouge) ou lancez Riot manuellement.

Connectez-vous à votre compte.

IMPORTANT : Vous devez cocher la case "Rester connecté" (Stay signed in).

Une fois sur l'écran d'accueil du jeu (bouton JOUER visible), retournez sur SwitchZ.

Entrez un nom (ex: Main, Smurf) et cliquez sur "SAUVEGARDER".

Le logiciel va capturer votre rang et sauvegarder la session.

Répétez l'opération pour vos autres comptes.

⚠️ Avertissement
Ce logiciel est un outil tiers non officiel. Il n'interagit pas avec le jeu en partie (pas de script/cheat), il automatise seulement la gestion des fichiers de configuration du client Riot. Utilisation à vos propres risques. Ce projet n'est pas affilié à Riot Games.
