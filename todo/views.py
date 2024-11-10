from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .models import ToDo
from django.contrib.auth.decorators import login_required
from .forms import TodoForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.pdfgen import canvas  # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle  # type: ignore
from reportlab.lib import colors  # type: ignore
from reportlab.lib.units import inch  # type: ignore
from g4f.client import Client  # type: ignore
from django.core.paginator import Paginator
from django.db.models import Case, When, Value, IntegerField

import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Create your views here.
@login_required
def todo_list(request):
    # Obtenez toutes les tâches de l'utilisateur
    todos = ToDo.objects.filter(user_id=request.user.id)

    # Parcourir les tâches et mettre à jour le statut si nécessaire
    for todo in todos:
        # Only update overdue status if the task is not completed
        if (
            todo.due_date
            and timezone.now().date() > todo.due_date
            and todo.status != "completed"
        ):
            todo.status = "overdue"  # Mettre le statut en "overdue"
            todo.save()  # Sauvegarder les modifications

    # Ordre des tâches : pending, overdue, completed
    todos = todos.annotate(
        status_order=Case(
            When(status="pending", then=Value(1)),
            When(status="overdue", then=Value(2)),
            When(status="completed", then=Value(3)),
            output_field=IntegerField(),
        )
        ).order_by("status_order", "-created_at")


    # Pagination pour 6 tâches par page
    paginator = Paginator(todos, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "todo/listetodo.html", {"page_obj": page_obj})


@login_required
def create_task(request):
    if request.method == "POST":
        form = TodoForm(
            request.POST, is_update=False
        )  # Passer is_update=False pour la création
        if form.is_valid():
            todo = form.save(commit=False)  # Ne pas sauvegarder tout de suite
            todo.user = request.user  # Associer la tâche à l'utilisateur connecté
            todo.save()  # Maintenant, sauvegarder
            return redirect("user_todo_list")  # Rediriger vers la liste des tâches
    else:
        form = TodoForm(
            is_update=False
        )  # Passer is_update=False pour le formulaire vide
    
    messages.success(request, "Tâche ajouter avec succès.")
    return render(request, "todo/create_task.html", {"form": form})


@login_required
def update_task(request, pk):
    todo = get_object_or_404(
        ToDo, pk=pk, user=request.user
    )  # Vérifie que l'utilisateur possède la tâche
    if request.method == "POST":
        form = TodoForm(
            request.POST, instance=todo, is_update=True
        )  # Passer is_update=True pour la mise à jour
        if form.is_valid():
            form.save()
            return redirect("user_todo_list")  # Rediriger vers la liste des tâches
    else:
        form = TodoForm(
            instance=todo, is_update=True
        )  # Passer is_update=True pour le formulaire d'instance

    messages.success(request, "Tâche modifier avec succès.")
    return render(request, "todo/update_task.html", {"form": form, "todo": todo})


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(ToDo, id=task_id, user=request.user)
    task.delete()
    messages.success(request, "Tâche supprimée avec succès.")
    return redirect("user_todo_list")


@login_required
def complete_task(request, task_id):
    todo = get_object_or_404(ToDo, id=task_id, user=request.user)
    todo.status = "completed"  # Update status to "completed"
    todo.save()  # Save changes
    
    messages.success(request, "statue de tâche changer a terminer avec succès.")
    return HttpResponseRedirect(reverse("user_todo_list"))


def download_tasks_pdf(request):
    # Create a PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="tasks.pdf"'

    # Create a SimpleDocTemplate for better layout control
    doc = SimpleDocTemplate(response, pagesize=A4)

    # Initialize a list to hold the elements
    elements = []
    styles = getSampleStyleSheet()

    # Add title
    title = Paragraph("Liste de Tâches", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))  # Add space below title

    # Fetch all tasks
    todos = ToDo.objects.filter(user_id=request.user.id)

    # Prepare data for the table
    data = [["Titre", "Description", "Date Limite", "Statut"]]

    # Add each task to the data
    for task in todos:
        status_color = (
            colors.green
            if task.status == "completed"
            else colors.red if task.status == "overdue" else colors.orange
        )
        data.append(
            [
                Paragraph(task.title, styles["Normal"]),
                Paragraph(task.description, styles["Normal"]),
                Paragraph(task.due_date.strftime("%d/%m/%Y"), styles["Normal"]),
                Paragraph(task.status, styles["Normal"]),
            ]
        )

    # Create a table
    table = Table(data)

    # Add style to the table
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(table)

    # Build the PDF
    doc.build(elements)

    return response


##IA PARTIE ##


# Fonction d'interaction avec le modèle GPT
def ask_gpt(message):
    client = Client()  # Instancie le client GPT
    try:
        response = client.chat.completions.create(
            model="blackboxai", messages=[{"role": "user", "content": message}]
        )
        if response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "No response received from GPT."
    except Exception as e:
        return f"Error: {str(e)}"


# Fonction pour vérifier si la réponse suit le format attendu
def is_formatted_correctly(response_message):
    required_keywords = ["title:", "description:", "due_date:", "justification:"]
    return all(keyword in response_message for keyword in required_keywords)


# Vue Django pour lister les tâches avec IA
def user_todo_list(request):
    # Récupérer les tâches en attente et en retard pour l'utilisateur connecté
    todos = ToDo.objects.filter(user=request.user, status__in=["pending", "overdue"])

    # Vérifiez si le nombre de tâches est inférieur à 3
    if todos.count() < 3:
        messages.info(
            request,
            "Pour générer des priorités par IA, vous devez avoir au moins 3 tâches en attente ou en retard.",
        )
        return redirect("user_todo_list")  # Redirige vers la liste des tâches

    # Préparer le message pour GPT avec des consignes de priorité
    message = (
        "Organise les tâches suivantes par priorité en fonction des critères suivants pour déterminer l'importance relative :\n"
        "- **Urgence** : L'échéance (due_date) peut indiquer l'urgence, mais elle ne doit pas être le seul critère de priorisation.\n"
        "- **Mots-clés** : Les tâches contenant des mots-clés comme 'réunion', 'présentation', 'examen', ou 'médecin' sont souvent critiques.\n"
        "- **Complexité** : Les descriptions longues et détaillées peuvent impliquer une complexité ou un effort plus important.\n"
        "- **Impact** : Tenez compte de l'impact potentiel de chaque tâche.\n"
        "- **Conséquences** : Privilégiez les tâches ayant une conséquence directe, comme un examen ou un rendez-vous médical.\n"
        "- **Justification** : Incluez une justification pour la priorisation de chaque tâche.\n\n"
        "Retournez les tâches organisées dans le format suivant :\n"
        "1 - title: <titre> description: <description> due_date: <date limite> justification: <raison de la priorité>\n"
        "2 - title: <titre> description: <description> due_date: <date limite> justification: <raison de la priorité>\n\n"
    )

    # Ajouter les tâches au message pour GPT
    for i, task in enumerate(todos, 1):
        message += f"{i} - title: {task.title} description: {task.description} due_date: {task.due_date}\n"

    # Obtenir la réponse de GPT
    response_message = ask_gpt(message)

    print("message:", response_message)

    # Initialisation des paramètres de la boucle de vérification
    retry_count = 0
    max_retries = 5  # Limite pour éviter une boucle infinie

    # Boucle pour obtenir une réponse formatée selon les critères demandés
    while (
        not response_message
        or response_message == "No message received"
        or response_message == "Request ended with status code 403"
        or not is_formatted_correctly(response_message)  # Vérification du format
    ) and retry_count < max_retries:
        response_message = ask_gpt(message)
        retry_count += 1

    organized_tasks = []
    if response_message and "Error:" not in response_message:
        # Diviser les tâches en blocs séparés par un saut de ligne double
        task_blocks = response_message.strip().split("\n\n")

        for task_block in task_blocks:
            task_data = {}

            # Extraire chaque champ par clé
            for line in task_block.split("\n"):
                if "title:" in line:
                    task_data["title"] = line.split("title:", 1)[1].strip()
                elif "description:" in line:
                    task_data["description"] = line.split("description:", 1)[1].strip()
                elif "due_date:" in line:
                    task_data["due_date"] = line.split("due_date:", 1)[1].strip()
                elif "justification:" in line:
                    task_data["justification"] = line.split("justification:", 1)[
                        1
                    ].strip()

            # Ajouter la tâche seulement si toutes les clés sont présentes
            if task_data:
                organized_tasks.append(task_data)

    # Pagination pour 6 tâches par page
    paginator = Paginator(organized_tasks, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "todo/tachespriority.html", {"page_obj": page_obj})
