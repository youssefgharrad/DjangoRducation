from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from .models import *
from gestionCours.models import Course
from django.utils import timezone
from django.db import IntegrityError
from g4f.client import Client  # type: ignore
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from django.db.models import DateField
from django.db.models.functions import TruncDate
import logging
from gestionQuiz import *

import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# # Messages constants
# NO_MESSAGE_ERROR = "Aucun message reçu."
# NO_RESPONSE_ERROR = "No response received from GPT."
# DATA_RETRIEVAL_ERROR = "Erreur lors de la récupération des données de cours."
# GENERATION_ERROR = "Erreur lors de la génération de la réponse."


client = Client()

# Liste des questions prédéfinies et réponses associées
PREDEFINED_QUESTIONS = {
    "cours disponible ?": "courses",
    "quels sont les cours disponibles ?": "courses",
    "quels cours proposez-vous ?": "courses",
    "pouvez-vous m'indiquer les cours disponibles ?": "courses",
    "avez-vous des cours ?": "courses",
    "quels sont les cours existants ?": "courses",
    "quels types de cours sont proposés ?": "courses",
    "quelle formation est disponible ?": "courses",
    "quels modules sont disponibles ?": "courses",
    "quiz pour chaque cours": "courses_with_quizzes",
    "pouvez-vous me donner les quiz pour chaque cours ?": "courses_with_quizzes",
    "quels sont les quiz disponibles pour les cours ?": "courses_with_quizzes",
    "y a-t-il des quiz pour chaque cours ?": "courses_with_quizzes",
    "donnez-moi les quiz associés aux cours": "courses_with_quizzes",
    "quiz disponibles pour les cours ?": "courses_with_quizzes",
    "y a-t-il un quiz pour chaque cours ?": "courses_with_quizzes",
    "pouvez-vous lister les quiz pour les différents cours ?": "courses_with_quizzes",
    "quels cours ont des quiz disponibles ?": "courses_with_quizzes"
}


# Fonction d'interaction avec le modèle GPT
def ask_gpt(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": message}]
        )
        if response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "No response received from GPT."
    except Exception as e:
        return f"Error: {str(e)}"


@login_required(login_url="signin")
def chatbot(request):
    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        print(f"Message from user: {message}")

        if not message:
            return JsonResponse({"error": "Aucun message reçu."})

        # Vérification si la question est prédéfinie
        response_type = PREDEFINED_QUESTIONS.get(message.lower())

        # Réponse basée sur le type de question prédéfinie
        if response_type == "courses":
            response_message = handle_courses_only()
        elif response_type == "courses_with_quizzes":
            response_message = handle_courses_with_quizzes()
        else:
            # Si la question n'est pas prédéfinie, envoyer directement à GPT pour une réponse logique
            response_message = ask_gpt(message)

            # Répéter l'appel à GPT jusqu'à obtenir une réponse valide
            retry_count = 0
            max_retries = 5  # Limite pour éviter une boucle infinie
            while (not response_message or response_message == "No message received" or response_message =="Request ended with status code 403") and retry_count < max_retries:
                response_message = ask_gpt(message)
                retry_count += 1


            print(response_message)
            # Si toujours aucune réponse valide, renvoyer un message d'erreur générique
            if not response_message or response_message == "No message received" or response_message =="Request ended with status code 403":
                response_message = "Je ne comprends pas bien votre question, pouvez-vous la reformuler ?"

        # Enregistrer la conversation dans la base de données
        try:
            chat = Chat(
                user=request.user,
                message=message,
                response=response_message,
                created_at=timezone.now(),
            )
            chat.save()
        except Exception as e:
            print(f"Error saving chat to database: {str(e)}")

        return JsonResponse({"message": message, "response": response_message})

    return render(request, "chatbot/chatbot.html", {"chats": []})


# Fonctions de gestion des cours et quiz
def handle_courses_only():
    try:
        courses = Course.objects.all()
        if courses.exists():
            response_message = "Here are some available courses:\n\n"
            for course in courses:
                response_message += f"- **{course.title}**: {course.description}\n\n"
        else:
            response_message = "Currently, there are no available courses."
    except Exception as e:
        print(f"Error fetching courses: {str(e)}")
        response_message = "An error occurred while retrieving course information."
    return response_message


def handle_courses_with_quizzes():
    try:
        courses_with_quizzes = Course.objects.prefetch_related("quizzes").all()
        if courses_with_quizzes.exists():
            response_message = "Here are some available courses with their quizzes:\n\n"
            for course in courses_with_quizzes:
                response_message += f"- **{course.title}**: {course.description}\n"
                quizzes = course.quizzes.all()
                if quizzes.exists():
                    response_message += "  Quizzes:\n"
                    for quiz in quizzes:
                        response_message += (
                            f"    - **{quiz.title}**: {quiz.description}\n"
                        )
                else:
                    response_message += "  No quizzes available for this course.\n"
                response_message += "\n"
        else:
            response_message = "Currently, there are no available courses."
    except Exception as e:
        print(f"Error fetching courses with quizzes: {str(e)}")
        response_message = (
            "An error occurred while retrieving course and quiz information."
        )
    return response_message


@login_required(login_url="signin")
def historiquechatbot(request):
    # Query the chats for the logged-in user, ordered by creation date (most recent first)
    chats = Chat.objects.filter(user=request.user).order_by("created_at")

    # Group chats by date
    grouped_chats = group_chats_by_date(chats)

    print(request.user.id)  # Print the current user object to the console

    # Pass the grouped chats to the template
    return render(
        request, "chatbot/historiquechatbot.html", {"grouped_chats": grouped_chats}
    )


def group_chats_by_date(chats):
    grouped_chats = {}
    for chat in chats:
        chat_date = chat.created_at.date()  # Use the original date without TruncDate
        if chat_date not in grouped_chats:
            grouped_chats[chat_date] = []

        # Store both the message and the response in a dictionary
        grouped_chats[chat_date].append(
            {
                "id": chat.id,  # Include the chat ID in the grouped data
                "message": chat.message,
                "response": chat.response,
                "dateEnvoie": chat.created_at,
            }
        )

    return grouped_chats


@login_required(login_url="signin")
def delete_chats_by_date(request, date):
    # Ensure the date is in the correct format
    date_obj = timezone.datetime.strptime(date, "%Y-%m-%d").date()

    # Delete all chats for the user on that specific date
    Chat.objects.filter(user=request.user.id, created_at__date=date_obj).delete()

    return redirect("historique_chatbot")  # Redirect to chat history page
