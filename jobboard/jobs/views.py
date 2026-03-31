from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.db.models import Q, F, Count, Avg, Sum
from django.http import HttpResponseForbidden

from .models import Job, Application
from .forms import JobPostForm, ApplicationForm, JobSearchForm


# ============================================================
# ListView — shows a list of objects
# ============================================================

class JobListView(ListView):
    """
    ListView automatically:
    - Queries model.objects.all()
    - Passes result as object_list (or <model_name>_list) to template
    - Handles pagination via paginate_by
    """
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'    # Variable name in template
    paginate_by = 10                # Auto-pagination

    def get_queryset(self):
        """
        Override to customize the queryset.
        
        Demonstrates:
        - Q objects for complex OR/AND queries
        - select_related() to avoid N+1 on ForeignKey
        - F expressions referencing field values
        """
        # Base queryset — only active jobs
        # select_related('posted_by') does a SQL JOIN so accessing
        # job.posted_by doesn't trigger an extra query per job
        qs = Job.objects.filter(is_active=True).select_related('posted_by')
        
        self.form = JobSearchForm(self.request.GET)
        
        if self.form.is_valid():
            q = self.form.cleaned_data.get('q')
            job_type = self.form.cleaned_data.get('job_type')
            location = self.form.cleaned_data.get('location')
            
            # Q objects — complex queries with OR (|) and AND (&)
            if q:
                qs = qs.filter(
                    Q(title__icontains=q) |          # OR
                    Q(company_name__icontains=q) |   # OR
                    Q(description__icontains=q)       # OR
                )
            
            if job_type:
                qs = qs.filter(job_type=job_type)
            
            if location:
                qs = qs.filter(location__icontains=location)
        
        # annotate() — adds a computed field to each object in the QuerySet
        # Count('applications') counts related Application objects per job
        qs = qs.annotate(application_count=Count('applications'))
        
        return qs

    def get_context_data(self, **kwargs):
        """Add extra data to the template context."""
        context = super().get_context_data(**kwargs)
        context['search_form'] = getattr(self, 'form', JobSearchForm())
        
        # aggregate() — computes a single summary value over the whole QuerySet
        stats = Job.objects.filter(is_active=True).aggregate(
            total_jobs=Count('id'),
            total_applications=Count('applications'),
        )
        context['stats'] = stats
        return context


# ============================================================
# DetailView — shows one object
# ============================================================

class JobDetailView(DetailView):
    """
    DetailView automatically:
    - Gets object by pk from URL
    - Passes it as 'object' (or model name) to template
    """
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

    def get_queryset(self):
        # select_related for ForeignKey (single related object)
        return Job.objects.select_related('posted_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.get_object()
        
        # Check if current user has already applied
        if self.request.user.is_authenticated:
            context['already_applied'] = Application.objects.filter(
                job=job,
                applicant=self.request.user
            ).exists()
        
        context['application_form'] = ApplicationForm()
        return context


# ============================================================
# CreateView — handles GET (show form) and POST (save form)
# LoginRequiredMixin — redirects to LOGIN_URL if not authenticated
# ============================================================

class JobCreateView(LoginRequiredMixin, CreateView):
    """
    CreateView handles both:
    - GET: renders empty form
    - POST: validates and saves, then redirects
    
    LoginRequiredMixin checks authentication.
    If not logged in → redirects to settings.LOGIN_URL
    """
    model = Job
    form_class = JobPostForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('jobs:job_list')  # Redirect after success

    def dispatch(self, request, *args, **kwargs):
        """
        dispatch() runs before get() or post().
        Override for custom permission checks.
        """
        if request.user.is_authenticated and not request.user.is_company:
            messages.error(request, 'Only company accounts can post jobs.')
            return redirect('jobs:job_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Called when form.is_valid() is True.
        Set posted_by before saving.
        """
        # commit=False → creates object but doesn't save to DB yet
        job = form.save(commit=False)
        job.posted_by = self.request.user
        job.company_name = self.request.user.company_name or self.request.user.username
        job.save()
        
        messages.success(self.request, f'Job "{job.title}" posted successfully!')
        return redirect('jobs:job_detail', pk=job.pk)

    def form_invalid(self, form):
        """Called when form.is_valid() is False."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Post a New Job'
        context['submit_label'] = 'Post Job'
        return context


# ============================================================
# UpdateView — edit existing object
# ============================================================

class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    form_class = JobPostForm
    template_name = 'jobs/job_form.html'

    def get_success_url(self):
        return reverse_lazy('jobs:job_detail', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        job = self.get_object()
        # Only the job poster can edit it
        if job.posted_by != request.user:
            messages.error(request, 'You can only edit your own job postings.')
            return redirect('jobs:job_detail', pk=job.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit: {self.object.title}'
        context['submit_label'] = 'Save Changes'
        return context


# ============================================================
# DeleteView — confirm + delete
# ============================================================

class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('jobs:job_list')

    def dispatch(self, request, *args, **kwargs):
        job = self.get_object()
        if job.posted_by != request.user:
            return HttpResponseForbidden('Access denied.')
        return super().dispatch(request, *args, **kwargs)


# ============================================================
# Function-based view for applying — shows file upload handling
# ============================================================

@login_required
def apply_to_job(request, pk):
    """
    FBV with file upload.
    Demonstrates: request.FILES, form with files, redirect()
    """
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    # Prevent companies from applying
    if request.user.is_company:
        messages.error(request, 'Company accounts cannot apply to jobs.')
        return redirect('jobs:job_detail', pk=pk)
    
    # Prevent duplicate applications
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied to this job.')
        return redirect('jobs:job_detail', pk=pk)
    
    if request.method == 'POST':
        # For file uploads, pass BOTH request.POST and request.FILES
        # Without request.FILES, file data is ignored
        form = ApplicationForm(request.POST, request.FILES)
        
        if form.is_valid():
            # cleaned_data — dict of validated, cleaned values
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            
            messages.success(
                request,
                f'Application submitted to {job.company_name}! Good luck! 🎉'
            )
            return redirect('jobs:my_applications')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ApplicationForm()
    
    return render(request, 'jobs/apply.html', {
        'form': form,
        'job': job,
    })


@login_required
def my_applications(request):
    """
    Shows current user's applications.
    
    select_related('job', 'job__posted_by') — follows FK chain:
    Application → Job → User (posted_by)
    All fetched in ONE query with JOINs, avoiding N+1.
    
    N+1 problem: If you loop 50 applications and access application.job.title,
    Django fires 1 query for applications + 50 queries for each job = 51 queries.
    select_related solves this with a single JOIN.
    """
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related(
        'job',           # Gets the related Job
        'job__posted_by' # Also gets the Job's posted_by user (chain!)
    ).order_by('-applied_at')
    
    return render(request, 'jobs/my_applications.html', {
        'applications': applications,
    })


@login_required
def company_dashboard(request):
    """
    Dashboard for company users.
    
    Demonstrates:
    - annotate() — adds aggregate data to each object
    - prefetch_related() — for ManyToMany or reverse FK (applications)
    - F expressions
    """
    if not request.user.is_company:
        return redirect('jobs:job_list')
    
    # annotate() adds 'num_applications' to each job object
    # Count('applications') counts related Application objects
    jobs = Job.objects.filter(
        posted_by=request.user
    ).annotate(
        num_applications=Count('applications'),
        # F() references another field in the same row
        # Here we'd use it for comparisons, e.g.:
        # days_since_posted=F('created_at')  (conceptual)
    ).prefetch_related(
        'applications',           # Prefetch all applications
        'applications__applicant' # And their applicants — avoids N+1
    ).order_by('-created_at')
    
    # aggregate() returns a dict with summary stats
    overall_stats = Application.objects.filter(
        job__posted_by=request.user
    ).aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        hired=Count('id', filter=Q(status='hired')),
    )
    
    return render(request, 'jobs/company_dashboard.html', {
        'jobs': jobs,
        'stats': overall_stats,
    })