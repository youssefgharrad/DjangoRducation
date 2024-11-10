# DjangoRducation
## Overview
DjangoEducation is an online course management platform, developed with Django, Python, and PostgreSQL, that enables teachers to create and manage course content, track student progress, and foster engagement. It includes AI-driven features to enhance the learning experience.
## Login Dashboard
![image](https://github.com/user-attachments/assets/3c681d88-58c2-4a89-92b6-f699a8e2934d)

## Teacher's Dashboard
![image](https://github.com/user-attachments/assets/78377968-0aac-498f-9a92-e80e82ff2c56)

![image](https://github.com/user-attachments/assets/abff92f5-06e8-4442-aca3-ccbd4ff733ec)

## Student's Dashboard
![image](https://github.com/user-attachments/assets/32e40139-7eda-4364-8166-2b4ffe0549a0)


# Projet Django - Installation Guide

## Étapes d'installation

### 1. Clone the Repository
To get started, clone the project using the following command:
``` 
git clone https://github.com/DjangoEducation/DjangoEducation.git 
```

### 2.Set Up Project Folder and Virtual Environment
Create a new directory for the project, move into it, and set up a virtual environment:
``` 
mkdir DjangoProject
cd DjangoProject
virtualenv djangoEnv
```

### 3. Activate the Virtual Environment
Activate the virtual environment with this command:
``` 
djangoEnv\Scripts\activate
```

### 4. Install Django
While the environment is activated, install Django version 4.2:
``` 
python -m pip install django==4.2

```
### 5. Navigate to Project Folder and Apply Migrations
Move into the cloned project folder and generate and apply migrations:
``` 
cd ../Django-authentification-master/firstProject
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser
Create a superuser account to access the admin dashboard:
```
python manage.py createsuperuser
```

### 7. Start the Server
``` 
python manage.py runserver
```
