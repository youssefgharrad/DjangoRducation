from io import BytesIO
import os
import string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CourseForm,ChapitreForm
from .models import Course,Chapitre ,Summarize
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import random
from .models import CoursParticiperParUser
from .models import Course
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect





import google.generativeai as genai
import PyPDF2

from fpdf import FPDF


@login_required(login_url='signin')
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            print(f"Utilisateur assigné : {course.user}")
            course.save()
            print("Cours sauvegardé avec succès")
            return redirect('courses_list')
    else:
        form = CourseForm()
    return render(request, 'cours/add_course.html', {'form': form})


@login_required(login_url='signin')
def courses_list(request):
    user = request.user
    if user.role == 'Enseignant' :
        courses = Course.objects.filter(user=request.user)
    else:
        courses = Course.objects.all()
    return render(request, 'cours/courses_list.html', {'courses': courses})

# views.py
@login_required(login_url='signin')
def update_course(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'cours/update_course.html', {'form': form, 'course': course})


@login_required(login_url='signin')
def delete_course(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('courses_list')
    return render(request, 'cours/delete_course.html', {'course': course})


@login_required(login_url='signin')
def courses_selectionner(request, course_id):
    user = request.user
    if user.role == 'Enseignant' :
        cours_id = get_object_or_404(Course, id=course_id, user=request.user)
        chapters = Chapitre.objects.filter(cours_id=cours_id)  
    else:
        cours_id = get_object_or_404(Course, id=course_id)
        chapters = Chapitre.objects.filter(cours_id=cours_id,viewChapitre=1) 
    return render(request, 'chapitre/chapitre_list.html', {'course': cours_id, 'chapters': chapters, 'user': user})

@login_required(login_url='signin')
def participer_cours(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    participation, created = CoursParticiperParUser.objects.get_or_create(user=user, course=course)

    if created:
        message = "Vous avez participé avec succès à ce cours."
    else:
        message = "Vous avez déjà participé à ce cours."

    return redirect(reverse('courses_list'))
@login_required(login_url='signin')
def mes_cours_participes(request):
    user = request.user

    participations = CoursParticiperParUser.objects.filter(user=user)

    cours_participes = [participation.course for participation in participations]

    context = {
        'cours_participes': cours_participes,
    }

    return render(request, 'cours/mes_cours_participes.html', context)


@login_required(login_url='signin')
def recommend_courses(request):
    user = request.user
    recommended_courses = Course.objects.filter(
        specialites=user.specialite,
        niveau=user.experience
    )
    if not recommended_courses.exists():
        recommended_courses = Course.objects.filter(
            niveau=user.experience
        )

    user_participations = CoursParticiperParUser.objects.filter(user=user).values_list('course_id', flat=True)
    for course in recommended_courses:
        course.already_participated = course.id in user_participations

    context = {
        'recommended_courses': recommended_courses,
        'user': user
    }

    return render(request, 'cours/suggestions.html', context)

    
@login_required(login_url='signin')
def add_chapitre(request, course_id):
    print(f"enetred     : {course_id}")
    course = get_object_or_404(Course, id=course_id, user=request.user)
    print(f"course  : {course}")
    if request.method == 'POST':
        form = ChapitreForm(request.POST, request.FILES)
        if form.is_valid():
            print(f"valid  :")
            chapitre = form.save(commit=False)  # Do not save to the database yet
            chapitre.cours = course  # Set the course for this chapter
            chapitre.save()  # Save the chapter with the course set
            return redirect('courses_selectionner', course_id=course.id)  # Redirect to the course's chapter list
    else:
        form = ChapitreForm()

    return render(request, 'chapitre/add_chapitre.html', {'form': form, 'course': course})


@csrf_exempt  # Consider using decorators to ensure security
def toggle_view_chapitre(request):
    if request.method == "POST":
        chapter_id = request.POST.get('chapter_id')
        viewed = request.POST.get('viewed') == 'true'  # Convert to boolean
        
        # Assuming you have a Chapter model
        chapter = Chapitre.objects.get(id=chapter_id)
        chapter.viewChapitre = viewed
        chapter.save()
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required(login_url='signin')
def delete_chapitre(request, chapter_id):
    chapitre = Chapitre.objects.get(id=chapter_id)
    cours= chapitre.cours_id 
    if request.method == 'POST':
        chapitre.delete()
        return redirect('courses_selectionner', course_id=cours)
    return render(request, 'cours/delete_chapitre.html', {'chapitre': chapitre})


os.environ["GEMINI_API_KEY"] = ""
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def summarize_pdf(request, chapter_id):
    try:
        chapter = Chapitre.objects.get(id=chapter_id)
    except Chapitre.DoesNotExist:
        return JsonResponse({"error": "Chapter not found."}, status=404)

    pdf_path = chapter.document.path
    search_term = request.GET.get("search_term", "").strip()

    # Open the PDF and extract text
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        full_text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

    if search_term:
        term_locations = [
            f"Page {page_num + 1}" for page_num, page in enumerate(pdf_reader.pages)
            if search_term.lower() in (page.extract_text() or "").lower()
        ]

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        explanation_response = model.generate_content(
            f"Fournissez des informations détaillées sur '{search_term}' dans ce texte :\n{full_text}"
        )
        explanation_text = "<p>" + explanation_response.text.replace("\n", "</p><p>") + "</p>"
        
        return JsonResponse({
            "term": search_term,
            "locations": term_locations,
            "explanation": explanation_text,
        })

    # Summarize PDF content
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    summary_response = model.generate_content(f"Résumez avec les points clés : {full_text}")
    pdf_summary = summary_response.text

    print(f"PDF : {pdf_summary} \n\n")


    # Save PDF summary to storage
    storage_path = "storage"
    os.makedirs(storage_path, exist_ok=True)  # Create storage folder if it doesn't exist

    str_characters =  string.ascii_lowercase + string.digits

    # Define the PDF file path
    sanitized_title = "".join([c if c.isalnum() else "_" for c in chapter.title])
    random_string = "".join(random.choice(str_characters) for _ in range(10))

    # Generate a new random filename for each attempt
            
    pdf_buffer = f"{storage_path}/{sanitized_title}.pdf"

    # Create the PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, pdf_summary)
            
    # Try to save the PDF
    try:
        pdf.output(pdf_buffer)
        print(f"PDF saved as {pdf_buffer}")
        # Description model content
        description_response = model.generate_content(f"Generate brief description for: {full_text}")
        description = description_response.text

        # Save the summary as a Summarize object
        with open(pdf_buffer, 'rb') as pdf_file:
            summary = Summarize(
                title=f"Summary of {chapter.title}",
                description=description,
                cours=chapter.cours,
                categorie=chapter.categorie
            )
            summary.pdf.save(f"{chapter.title}_{random_string}_summary.pdf", ContentFile(pdf_file.read()))
            summary.save()
    except Exception as e:
        print(f"Failed to save PDF: {e}")

    organized_summary = "<p>" + pdf_summary.replace("\n", "</p><p>") + "</p>"

    return JsonResponse({"summary": organized_summary})
    
