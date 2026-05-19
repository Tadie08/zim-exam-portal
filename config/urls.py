from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [

    # -------------------- Logins/Outs/Password Reset --------------------
    path("login/", views.CustomLoginView.as_view(), name="login"),
    
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("signup/", views.signup_view, name="signup"),
    
    # Profile page (username click)
    path("profile/", views.profile_view, name="profile"),
    
    # Guide page
    path("guide/", views.guide_view, name="guide"),

    # Password Reset URLs...
    path("password-reset/", 
         auth_views.PasswordResetView.as_view(
             template_name="core/password_reset.html",
             email_template_name="core/password_reset_email.html",
             subject_template_name="core/password_reset_subject.txt",
             success_url="/password-reset/done/"
         ), 
         name="password_reset"),
    
    path("password-reset/done/", 
         auth_views.PasswordResetDoneView.as_view(
             template_name="core/password_reset_done.html"
         ), 
         name="password_reset_done"),
    
    path("password-reset-confirm/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(
             template_name="core/password_reset_confirm.html",
             success_url="/password-reset-complete/"
         ), 
         name="password_reset_confirm"),
    
    path("password-reset-complete/", 
         auth_views.PasswordResetCompleteView.as_view(
             template_name="core/password_reset_complete.html"
         ), 
         name="password_reset_complete"),

    # -------------------- Admin --------------------
    path("admin/", admin.site.urls),

    # -------------------- Home --------------------
    path("", views.home, name="home"),

    # -------------------- Syllabus --------------------
    path("syllabus/<str:level_name>/", views.syllabus_view, name="syllabus"),

    # -------------------- PAST PAPERS --------------------
    path("past-papers/<str:level_name>/", views.past_paper_subjects, name="past_paper_subjects"),
    path("past-papers/<str:level_name>/<int:subject_id>/", views.past_paper_years, name="past_paper_years"),
    path("past-papers/<str:level_name>/<int:subject_id>/<int:year>/", views.past_paper_sessions, name="past_paper_sessions"),
    path("past-papers/<str:level_name>/<int:subject_id>/<int:year>/<str:session>/", views.past_paper_papers, name="past_paper_papers"),

    # -------------------- Topical Notes --------------------
    path("topical-notes/", views.topical_notes_view, name="topical_notes"),
    path("textbooks/", views.textbooks_view, name="textbooks"),
    path("textbooks/purchase/<int:book_id>/", views.purchase_textbook, name="purchase_textbook"),

    # -------------------- ABOUT ZIMSEC EXAMS --------------------
    path("about-zimsec/<str:section_name>/", views.zimsec_section, name="zimsec_section"),

    # -------------------- HELP/FAQ -------------------- 
    path("help/", views.help_page, name="help"),
    path("help/<str:section_name>/", views.help_section, name="help_section"), 

# -------------------- Purchase --------------------
    path("textbooks/purchase/<int:book_id>/", views.purchase_textbook, name="purchase_textbook"),
    path("payment/result/", views.payment_result, name="payment_result"),
    path("payment/return/", views.payment_return, name="payment_return"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)