# Aniteve
Un site pour regarder vos animés préférés sans pub en français.

<div align="center">
  <img style="height: 200px; width: 200px; margin-bottom: 50px" src="https://github.com/user-attachments/assets/e2659831-2278-466c-8429-bfa939df0032"/>
</div>

Aniteve est une plateforme complète qui vous permet de regarder et télécharger vos animes préférés sans aucune publicité. L'application TV, le site web (et prochainement l'application mobile) sont parfaitement synchronisés, vous offrant une expérience fluide et agréable.

## Fonctionnalités principales

### Regarder des animes

  - Gratuitement : Aucune publicité ou coût caché.

  - HD : Profitez d'une qualité vidéo optimale pour vos animes.

  - Différentes sources : Changez de source simplement

### Gestion de l'avancement

  - Reprenez un épisode là où vous l'avez laissé, que ce soit sur le site ou les applications.

  - Synchronisation en temps réel entre vos appareils.

### Découvertes et nouveautés

  - Une page d'accueil dynamique qui met en avant les derniers épisodes ajoutés ainsi que les nouvelles saisons.

### Système de compte utilisateur

  - Créez un compte pour sauvegarder vos préférences et votre progression.
 
  - Historique de visionnage pour retrouver facilement vos épisodes vus.

  - Synchronisation des données entre tous vos appareils connectés.

### Télécharger

  - Télécharger n'importe quel épisode.

## Installation

### Prérequis

  - Docker (testé sur la version 27.4.0) [Installer](https://docs.docker.com/engine/install/)

  - Make

  - NodeJs (testé sur la version 20.16.0) [Installer](https://nodejs.org/en/download)

### Configurer

1. Cloner le projet
```sh
$> git clone https://github.com/Kum1ta/Aniteve
```

2. Variables d'environnement
```sh
$> cd Aniteve/docker-compose && touch .env
```
Ce fichier va contenir toutes les clés et mot de passe utilisés par le serveur. Le fichier .env doit contenir ça :
```
KEY_API_TMDB="[Clé API TMDB]"
PASSWORD_SERVER="[Mot de passe utilisé pour la connexion au serveur]"
SECRET_KEY="[Mettre une string aléatoire ici (secret key flask)]"
WEBHOOK_URL="[Webhook discord (optionnel)]"
```
- [TMDB](https://www.themoviedb.org/settings/api)
- Le webhook discord sert pour faire des backup en envoyant la database toutes les 24h.

# Démarrer

1. Retourner à la racine du projet

2. ``` sh
   make
   ```

3. Tout est prêt !

Accessible sur l'adresse [http://localhost:8555](http://localhost:8555)
Pour toute sorti en dehors de votre réseau local, je vous conseille fortement de passer en https pour plus de sécurité

### Screenshots (Website)

| ![Image 1](https://github.com/user-attachments/assets/5353a0ab-ce00-421e-b7e2-a71c1fe52037) | ![Image 2](https://github.com/user-attachments/assets/cb23509d-827d-4477-bc0d-70d7898bb61e) |
|------------------------------------------------|------------------------------------------------|
| ![Image 3](https://github.com/user-attachments/assets/fa62721c-001b-4449-ad9c-cfb8450c816d) | ![Image 4](https://github.com/user-attachments/assets/abe26311-626d-42bd-901f-c29d7e0c73b1) |
| ![Image 5](https://github.com/user-attachments/assets/7a43601e-e031-4cf4-9e94-422379fb005c) | ![Image 6](https://github.com/user-attachments/assets/058d657f-dc31-431c-9f7c-261d66cdf9c9) |                                                |
  
### Avertissement

Je tiens à rappeler que regarder des animes sans passer par des plateformes légales peut être contraire aux droits d'auteur. Accéder ou télécharger des contenus protégés sans l'accord des ayants droit est illégal dans de nombreux pays et peut entraîner des sanctions. Aniteve est un projet personnel à but éducatif et ne promeut pas le piratage. Nous vous encourageons vivement à soutenir l'industrie de l'anime en utilisant des moyens légaux pour profiter de ces œuvres.
