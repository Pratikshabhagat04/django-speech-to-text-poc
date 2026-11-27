from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import TranscriptionForm
from .models import Transcription

def dashboard(request):
    query = request.GET.get("q", "").strip()
    records = Transcription.objects.all()
    if query:
        records = records.filter(
            Q(title__icontains=query) |
            Q(text__icontains=query) |
            Q(language__icontains=query)
        )
    return render(request, "transcriptions/dashboard.html", {
        "records": records,
        "query": query,
        "total": Transcription.objects.count(),
    })

def create_page(request):
    return render(request, "transcriptions/create.html")

def detail(request, pk):
    record = get_object_or_404(Transcription, pk=pk)
    return render(request, "transcriptions/detail.html", {"record": record})

def update(request, pk):
    record = get_object_or_404(Transcription, pk=pk)
    if request.method == "POST":
        form = TranscriptionForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Transcription updated.")
            return redirect("dashboard")
    else:
        form = TranscriptionForm(instance=record)
    return render(request, "transcriptions/edit.html", {"form": form, "record": record})

def delete(request, pk):
    record = get_object_or_404(Transcription, pk=pk)
    if request.method == "POST":
        record.delete()
        messages.success(request, "Transcription deleted.")
    return redirect("dashboard")
