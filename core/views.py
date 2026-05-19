from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from .models import Level, Subject, PastPaper, ZimsecInfo, UserProfile, TopicalNote, Textbook, Purchase
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, views as auth_views
from .forms import SignUpForm, ProfileUpdateForm
from django.contrib import messages
from django.conf import settings
from urllib.parse import urlencode
from paynow import Paynow
from .models import Textbook, Purchase, Payment
import uuid

# ---------------- CUSTOM LOGIN VIEW ----------------
class CustomLoginView(auth_views.LoginView):
    template_name = "core/login.html"
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/profile/'


# ---------------- HOME ----------------
def home(request):
    return render(request, "core/home.html")


# ---------------- DASHBOARD ----------------
@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on role"""
    try:
        role = request.user.userprofile.role
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=request.user, role='student')
        role = 'student'

    if role == "tutor":
        return render(request, "core/tutor_dashboard.html")
    return render(request, "core/student_dashboard.html")


# ---------------- GUIDE ----------------
@login_required
def guide_view(request):
    """Study guide page - one guide per subject"""
    level_param = request.GET.get('level', 'grade7').lower()
    
    LEVEL_MAP = {
        'grade7': 'Grade 7',
        'olevel': "O'Level",
        'alevel': "A'Level",
    }
    
    level_name = LEVEL_MAP.get(level_param, 'Grade 7')
    
    try:
        level = Level.objects.get(name=level_name)
        subjects = Subject.objects.filter(level=level).order_by('name')
        
        # Create list with subjects and their first approved guide
        subject_guides = []
        for subject in subjects:
            guide = subject.guide_set.filter(is_approved=True).first()
            subject_guides.append({
                'subject': subject,
                'guide': guide
            })
            
    except Level.DoesNotExist:
        subject_guides = []
        level_name = 'Grade 7'
    
    return render(request, "core/guide.html", {
        "subject_guides": subject_guides,
        "level_name": level_name,
        "current_level": level_param,
    })

# ---------------- PROFILE ----------------
@login_required
def profile_view(request):
    """User profile page"""
    user_profile = request.user.userprofile
    
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user_profile)
    
    return render(request, "core/profile.html", {
        "profile": user_profile,
        "form": form,
        "user": request.user
    })


# ---------------- SYLLABUS ----------------
LEVEL_NAME_MAP = {
    "grade7": {
        "db_name": "Grade 7",
        "paper_code": "GRADE7",
    },
    "olevel": {
        "db_name": "O'Level",
        "paper_code": "OLEVEL",
    },
    "alevel": {
        "db_name": "A'Level",
        "paper_code": "ALEVEL",
    },
}

def syllabus_view(request, level_name):
    config = LEVEL_NAME_MAP.get(level_name.lower())
    if not config:
        return render(request, "404.html", status=404)
    
    level = get_object_or_404(Level, name=config["db_name"])
    subjects = Subject.objects.filter(level=level).order_by("name")
    
    return render(request, "core/syllabus.html", {
        "level_name": config["db_name"],  # "Grade 7", "O'Level", or "A'Level"
        "current_level": level_name,  # "grade7", "olevel", "alevel"
        "subjects": subjects
    })


# ---------------- PAST PAPERS ----------------
def past_paper_subjects(request, level_name):
    config = LEVEL_NAME_MAP.get(level_name.lower())
    if not config:
        return render(request, "404.html", status=404)

    level = get_object_or_404(Level, name=config["db_name"])
    subjects = Subject.objects.filter(level=level).order_by("name")

    return render(request, "core/past_papers/subjects.html", {
        "level": level,
        "level_name": level_name,
        "subjects": subjects
    })


def past_paper_years(request, level_name, subject_id):
    config = LEVEL_NAME_MAP.get(level_name.lower())
    level = get_object_or_404(Level, name=config["db_name"])
    subject = get_object_or_404(Subject, id=subject_id, level=level)

    years = PastPaper.objects.filter(
        level=config["paper_code"],
        subject=subject
    ).values_list("year", flat=True).distinct().order_by("-year")

    return render(request, "core/past_papers/years.html", {
        "level_name": level_name,
        "subject": subject,
        "years": years
    })


def past_paper_sessions(request, level_name, subject_id, year):
    config = LEVEL_NAME_MAP.get(level_name.lower())
    level = get_object_or_404(Level, name=config["db_name"])
    subject = get_object_or_404(Subject, id=subject_id, level=level)

    sessions = PastPaper.objects.filter(
        level=config["paper_code"],
        subject=subject,
        year=year
    ).values_list("session", flat=True).distinct()

    return render(request, "core/past_papers/sessions.html", {
        "level_name": level_name,
        "subject": subject,
        "year": year,
        "sessions": sessions
    })


def past_paper_papers(request, level_name, subject_id, year, session):
    config = LEVEL_NAME_MAP.get(level_name.lower())
    level = get_object_or_404(Level, name=config["db_name"])
    subject = get_object_or_404(Subject, id=subject_id, level=level)
    
    session_variations = [session]
    if session == 'Nov':
        session_variations.append('November')
    elif session == 'November':
        session_variations.append('Nov')
    
    papers = PastPaper.objects.filter(
        level=config["paper_code"],
        subject=subject,
        year=year,
        session__in=session_variations,
        is_approved=True
    )

    return render(request, "core/past_papers/papers.html", {
        "level_name": level_name,
        "subject": subject,
        "year": year,
        "session": session,
        "papers": papers
    })


# ---------------- Topical Notes  ----------------
@login_required
def topical_notes_view(request):
    """Topical notes - FREE for all logged-in users"""
    level_param = request.GET.get('level', 'grade7').lower()
    
    LEVEL_MAP = {
        'grade7': 'Grade 7',
        'olevel': "O'Level",
        'alevel': "A'Level",
    }
    
    level_name = LEVEL_MAP.get(level_param, 'Grade 7')
    
    try:
        level = Level.objects.get(name=level_name)
        subjects = Subject.objects.filter(level=level).order_by('name')
        
        subject_notes = []
        for subject in subjects:
            notes = TopicalNote.objects.filter(subject=subject, is_approved=True)
            subject_notes.append({
                'subject': subject,
                'notes': notes
            })
            
    except Level.DoesNotExist:
        subject_notes = []
        level_name = 'Grade 7'
    
    return render(request, "core/topical_notes.html", {
        "subject_notes": subject_notes,
        "level_name": level_name,
        "current_level": level_param,
    })

# ---------------- Text Books ----------------
@login_required
def textbooks_view(request):
    """Textbooks - PAID, check if user purchased"""
    level_param = request.GET.get('level', 'grade7').lower()
    
    LEVEL_MAP = {
        'grade7': 'Grade 7',
        'olevel': "O'Level",
        'alevel': "A'Level",
    }
    
    level_name = LEVEL_MAP.get(level_param, 'Grade 7')
    
    try:
        level = Level.objects.get(name=level_name)
        subjects = Subject.objects.filter(level=level).order_by('name')
        
        subject_books = []
        for subject in subjects:
            books = Textbook.objects.filter(subject=subject, is_published=True)
            # Check which books user purchased
            books_with_status = []
            for book in books:
                is_purchased = Purchase.objects.filter(
                    user=request.user, 
                    textbook=book
                ).exists()
                books_with_status.append({
                    'book': book,
                    'is_purchased': is_purchased
                })
            
            subject_books.append({
                'subject': subject,
                'books': books_with_status
            })
            
    except Level.DoesNotExist:
        subject_books = []
        level_name = 'Grade 7'
    
    return render(request, "core/textbooks.html", {
        "subject_books": subject_books,
        "level_name": level_name,
        "current_level": level_param,
    })


# ---------------- Purchased Textbook  ----------------
@login_required
def purchase_textbook(request, book_id):
    """Handle textbook purchase with PayPal or Paynow redirect."""
    book = get_object_or_404(Textbook, id=book_id, is_published=True)
    
    # Check if already purchased
    if Purchase.objects.filter(user=request.user, textbook=book).exists():
        messages.info(request, "You already own this textbook!")
        return redirect('textbooks')
    
    payment_status = request.GET.get("payment")
    if payment_status == "success":
        transaction_id = request.GET.get("tx") or f"TX-{uuid.uuid4().hex[:12].upper()}"
        Purchase.objects.get_or_create(
            user=request.user,
            textbook=book,
            defaults={
                "amount_paid": book.price,
                "transaction_id": transaction_id,
            },
        )
        messages.success(request, f"Successfully purchased {book.title}!")
        return redirect('textbooks')

    if payment_status == "cancel":
        messages.warning(request, "Payment was cancelled.")
        return redirect('textbooks')

    gateway = request.POST.get("gateway", request.GET.get("gateway", "paynow")).lower()
    callback_base = request.build_absolute_uri(request.path)
    success_url = f"{callback_base}?payment=success&tx={uuid.uuid4().hex[:16].upper()}"
    cancel_url = f"{callback_base}?payment=cancel"

    if gateway == "paypal":
        business_email = getattr(settings, "PAYPAL_BUSINESS_EMAIL", "")
        if not business_email:
            messages.error(request, "PayPal is not configured. Please select another payment method.")
            return redirect('textbooks')

        paypal_url = getattr(settings, "PAYPAL_CHECKOUT_URL", "https://www.paypal.com/cgi-bin/webscr")
        params = {
            "cmd": "_xclick",
            "business": business_email,
            "item_name": book.title,
            "amount": f"{book.price:.2f}",
            "currency_code": getattr(settings, "PAYMENT_CURRENCY", "USD"),
            "invoice": f"BOOK-{book.id}-{request.user.id}-{int(datetime.now().timestamp())}",
            "return": success_url,
            "cancel_return": cancel_url,
        }
        return redirect(f"{paypal_url}?{urlencode(params)}")

    if gateway == "paynow":
        integration_id = getattr(settings, "PAYNOW_INTEGRATION_ID", "")
        integration_key = getattr(settings, "PAYNOW_INTEGRATION_KEY", "")
        if not integration_id or not integration_key:
            messages.error(request, "Paynow is not configured. Please select another payment method.")
            return redirect('textbooks')

        paynow_url = getattr(settings, "PAYNOW_CHECKOUT_URL", "https://www.paynow.co.zw/Payment/Link")
        params = {
            "id": integration_id,
            "reference": f"BOOK-{book.id}-{request.user.id}-{int(datetime.now().timestamp())}",
            "amount": f"{book.price:.2f}",
            "returnurl": success_url,
            "resulturl": cancel_url,
        }
        return redirect(f"{paynow_url}?{urlencode(params)}")

    messages.error(request, "Unsupported payment gateway selected.")
    return redirect('textbooks')


# ---------------- ABOUT ZIMSEC EXAMS ----------------
def zimsec_section(request, section_name):
    info = ZimsecInfo.objects.filter(section=section_name).order_by("-last_updated")

    section_titles = {
        "exam_dates": "Exam Dates",
        "registration": "How to Register",
        "results": "How to Get Results",
    }

    return render(request, "core/zimsec_section.html", {
        "infos": info,
        "section_title": section_titles.get(section_name, "ZIMSEC Information")
    })


# ---------------- HELP/FAQ ----------------
def help_page(request):
    return render(request, "core/help.html")


def help_section(request, section_name):
    section_titles = {
        "how-to-register": "How to Register",
        "how-to-get-results": "How to Get Results", 
        "exam-dates": "Exam Dates",
        "contact": "Contact Information",
    }
    
    context = {
        "section_title": section_titles.get(section_name, "Help & Support"),
        "section_name": section_name,
    }
    
    return render(request, "core/help.html", context)


# ---------------- SIGNUP ----------------
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            user.userprofile.role = form.cleaned_data["role"]
            user.userprofile.save()
            
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            
            return redirect('login')
    else:
        form = SignUpForm()
    
    return render(request, "core/signup.html", {"form": form})

# ---------------- Purchase ----------------
@login_required
def purchase_textbook(request, book_id):
    """Initiate Paynow payment"""
    book = get_object_or_404(Textbook, id=book_id, is_published=True)
    
    # Check if already purchased
    if Purchase.objects.filter(user=request.user, textbook=book).exists():
        messages.info(request, "You already own this textbook!")
        return redirect('textbooks')
    
    # Check for pending payment
    existing_payment = Payment.objects.filter(
        user=request.user, 
        textbook=book,
        status='pending'
    ).first()
    
    if existing_payment:
        # Check if payment was completed
        paynow = Paynow(
            settings.PAYNOW_INTEGRATION_ID,
            settings.PAYNOW_INTEGRATION_KEY,
            settings.PAYNOW_RESULT_URL,
            settings.PAYNOW_RETURN_URL
        )
        
        payment = paynow.check_transaction_status(existing_payment.poll_url)
        
        if payment.paid:
            # Payment completed, create purchase
            Purchase.objects.create(
                user=request.user,
                textbook=book,
                amount_paid=book.price,
                transaction_id=existing_payment.paynow_reference
            )
            existing_payment.status = 'paid'
            existing_payment.save()
            messages.success(request, "Payment successful! You can now download your book.")
            return redirect('textbooks')
        else:
            # Still pending, redirect to payment
            return redirect(payment.redirect_url)
    
    # Create new payment
    paynow = Paynow(
        settings.PAYNOW_INTEGRATION_ID,
        settings.PAYNOW_INTEGRATION_KEY,
        settings.PAYNOW_RESULT_URL,
        settings.PAYNOW_RETURN_URL
    )
    
        # Create payment
    email = request.user.email or f"user{request.user.id}@example.com"
    payment = paynow.create_payment(
        f"BOOK-{book.id}-{request.user.id}",
        email
    )
    
    
    # Add item
    payment.add(book.title, book.price)
    
    # Send to Paynow
    response = paynow.send(payment)
    
    if response.success:
        # Save payment record
        payment_record = Payment.objects.create(
            user=request.user,
            textbook=book,
            amount=book.price,
            paynow_reference=response.reference,
            poll_url=response.poll_url
        )
        
        # Redirect to Paynow payment page
        return redirect(response.redirect_url)
    else:
        messages.error(request, "Payment initialization failed. Please try again.")
        return redirect('textbooks')


@login_required
def payment_result(request):
    """Paynow callback - updates payment status"""
    reference = request.GET.get('reference')
    
    try:
        payment_record = Payment.objects.get(paynow_reference=reference)
        
        # Check status with Paynow
        paynow = Paynow(
            settings.PAYNOW_INTEGRATION_ID,
            settings.PAYNOW_INTEGRATION_KEY,
            settings.PAYNOW_RESULT_URL,
            settings.PAYNOW_RETURN_URL
        )
        
        status = paynow.check_transaction_status(payment_record.poll_url)
        
        if status.paid:
            payment_record.status = 'paid'
            payment_record.save()
            
            # Create purchase record
            Purchase.objects.get_or_create(
                user=payment_record.user,
                textbook=payment_record.textbook,
                defaults={
                    'amount_paid': payment_record.amount,
                    'transaction_id': reference
                }
            )
            
        elif status.cancelled:
            payment_record.status = 'cancelled'
            payment_record.save()
            
    except Payment.DoesNotExist:
        pass
    
    return render(request, 'core/payment_result.html')


@login_required
def payment_return(request):
    """User return page after payment"""
    reference = request.GET.get('reference')
    
    try:
        payment = Payment.objects.get(paynow_reference=reference, user=request.user)
        
        if payment.status == 'paid':
            messages.success(request, "Payment successful! Your book is now available for download.")
        elif payment.status == 'pending':
            messages.info(request, "Payment is still being processed. Please check back in a few minutes.")
        else:
            messages.error(request, "Payment was not completed. Please try again.")
            
    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
    
    return redirect('textbooks')