# Big-Data : Quel est l'impact économique des retards SNCF sur la région PACA

Dans la région PACA (Provence-Alpes-Côte d'Azur), les retards SNCF génèrent des pertes économiques massives pour les entreprises et les salariés. L'**objectif** est donc de quantifier l'impact économique des perturbations SNCF sur la région PACA pour permettre aux entreprises et collectivités d'anticiper et d'optimiser leurs continuités d'activité.

Pour ce faire, nous utiliserons la source de données officielle de la SNCF, à savoir l’[API SNCF Open Data](https://numerique.sncf.com/startup/api/) (limitée à la région PACA). Afin d’estimer le coût socio-économique, nous nous appuierons également sur la source officielle [Valeurs recommandées pour le calcul socio-économique](https://www.ecologie.gouv.fr/sites/default/files/documents/V.3.pdf) publiée par les ministères en charge de l’Aménagement du territoire et de la Transition écologique, qui fournit les valeurs de temps. Le document le plus récent que nous ayons identifié date toutefois de 2015. Par souci de simplicité méthodologique, nous ne prendrons pas en compte, dans un premier temps, la durée du trajet. Cela permet donc de dire : 

    COÛT PERTE €/h = nb_passagers × retard_minutes × 8,8€/3600

## I. Installation

### 1 . Récupérer le repository

Tout d'abord, installer `git` sur votre machine hôte. Puis cloner le repo, au moyen de la commande suivante : 

```bash 
git clone https://github.com/Oceane4973/Big-Data.git
```

### 2 . Générer les tokens d'accès

Créer un token pour l'API SNCF au lien suivant : https://numerique.sncf.com/startup/api/token-developpeur/. Le token vous sera envoyé par mail et demandé pour la suite des étapes, veuillez le copier.

### 3 . Renseigner les variables d'environement

Dans le dossier `/Big-Data` ainsi crée, renommer le fichier `.env-exemple` en `.env`. L'ouvrir et spécifier les valeurs suivantes :

```bash



```

> En fonction de la qualité du réseau, il peut être nécessaire d'attendre au moins 10 minutes pour le lancement du airflow-webserver