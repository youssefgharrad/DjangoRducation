# Projet Django - Guide d'installation et de démarrage

## Étapes d'installation

### 1. Cloner le projet depuis GitHub
Pour cloner le projet, exécutez la commande suivante dans votre terminal :
``` 
git clone https://github.com/DjangoEducation/DjangoEducation.git 
```

### 2.Créez un nouveau dossier pour votre projet et placez projet cloner dans ce dossier :

``` 
mkdir DjangoProject
cd DjangoProject
```
Ensuite, créez un environnement virtuel nommé djangoEnv :
``` 
virtualenv djangoEnv
```

### 3. Activez votre environnement virtuel. utilisez la commande suivante :
``` 
djangoEnv\Scripts\activate
```
Vous verrez que le prompt de votre terminal change, indiquant que l'environnement virtuel est activé.

### 4. Avec l'environnement virtuel activé, installez Django version 4.2 :
``` 
python -m pip install django==4.2

```
### 5. Une fois Django installé, entrez dans le dossier du projet cloné à partir de GitHub. Supposons que vous soyez déjà dans le répertoire de votre projet : 
``` 
cd ../Django-authentification-master/firstProject
```
Exécutez ensuite les commandes suivantes pour générer et appliquer les migrations :

``` 
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un super utilisateur :
```
python manage.py createsuperuser
```

### 7. Démarrer le serveur : 
``` 
python manage.py runserver
```

