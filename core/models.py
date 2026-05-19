from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import hashlib
import uuid


# -------------------- EDUCATION STRUCTURE --------------------

class Level(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Subject(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.level})"


# -------------------- PAST EXAM PAPERS --------------------

class PastPaper(models.Model):
    LEVEL_CHOICES = [
        ('GRADE7', 'Grade 7'),
        ('OLEVEL', 'O Level'),
        ('ALEVEL', 'A Level'),
    ]

    SESSION_CHOICES = [
        ('June', 'June'),
        ('November', 'November'),
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    year = models.IntegerField()
    session = models.CharField(max_length=10, choices=SESSION_CHOICES)
    paper_name = models.CharField(max_length=50)
    file = models.FileField(upload_to='past_papers/')
    is_approved = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject.name} {self.year} {self.paper_name}"

# -------------------- GUIDE --------------------
class Guide(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='guides/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.subject}"


# --------------------  SYLLABUS  --------------------

class Syllabus(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    effective_from = models.IntegerField()
    effective_to = models.IntegerField(null=True, blank=True)
    file = models.FileField(upload_to="syllabi/")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Syllabus: {self.subject}"


# -------------------- TOPICAL NOTES & REVISION --------------------

class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.name} ({self.subject})"


class TopicResource(models.Model):
    RESOURCE_TYPES = [
        ("notes", "Notes"),
        ("examples", "Worked Examples"),
        ("questions", "Topical Questions"),
        ("video", "Video"),
        ("pdf", "PDF"),
        
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to="topic_resources/", blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.topic})"


# -------------------- ABOUT ZIMSEC EXAMS --------------------

class ZimsecInfo(models.Model):
    SECTION_CHOICES = [
        ("exam_dates", "Exam Dates"),
        ("registration", "How to Register"),
        ("results", "How to Get Results"),
    ]

    section = models.CharField(max_length=50, choices=SECTION_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# -------------------- USER PROFILE & ACCESS CONTROL --------------------

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    # NEW: Profile fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    school = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # NEW: Security question for password reset (optional extra security)
    security_question = models.CharField(max_length=200, default="What was your first pet's name?")
    security_answer_hash = models.CharField(max_length=64, blank=True, null=True)
    
    # Subscription fields (for later)
    is_subscribed = models.BooleanField(default=False)
    subscription_expiry = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    def set_security_answer(self, answer):
        """Hash and store security answer"""
        self.security_answer_hash = hashlib.sha256(answer.lower().encode()).hexdigest()
    
    def check_security_answer(self, answer):
        """Verify security answer"""
        if not self.security_answer_hash:
            return False
        return self.security_answer_hash == hashlib.sha256(answer.lower().encode()).hexdigest()

# -------------------- AUTO CREATE USER PROFILE --------------------

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            role="student"   # default role
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "userprofile"):
        instance.userprofile.save()

# -------------------- Topical Notes --------------------

class TopicalNote(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    file = models.FileField(upload_to='topical_notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.topic} - {self.subject}"

# -------------------- Tectbooks --------------------
class Textbook(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    file = models.FileField(upload_to='textbooks/')
    cover_image = models.ImageField(upload_to='textbook_covers/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - {self.subject}"

# -------------------- Purchase --------------------
class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ['user', 'textbook']  # One purchase per user per book
        
    def __str__(self):
        return f"{self.user.username} - {self.textbook.title}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paynow_reference = models.CharField(max_length=100, blank=True)
    poll_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.textbook.title} - {self.status}"