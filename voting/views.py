# voting/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Election, Candidate, Vote
from users.models import CustomUser
from users.views import _send_sms  # reuse helper
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to Smart Voting App</h1>")


@login_required
def vote_view(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    user = request.user

    # check election active window
    now = timezone.now()
    if not (election.start_time <= now <= election.end_time) or not election.is_active:
        messages.error(request, "This election is not active.")
        return redirect('home')

    # ensure user belongs to same area as election (if you use area)
    if hasattr(user, 'area') and election.area_id != getattr(user, 'area').id:
        messages.error(request, "You are not registered for this election area.")
        return redirect('home')

    # check DB-level uniqueness as well but give friendly message
    existing = Vote.objects.filter(voter=user, election=election).exists()
    if existing or user.has_voted:
        messages.info(request, "You have already voted in this election.")
        return redirect('home')

    if request.method == "POST":
        candidate_id = request.POST.get('candidate')
        candidate = get_object_or_404(Candidate, id=candidate_id, election=election)
        # optional: enforce OTP/face check here before creating vote

        # create vote
        Vote.objects.create(voter=user, election=election, candidate=candidate)
        # flag user as voted (helps read performance)
        user.has_voted = True
        user.save()

        # send SMS confirmation
        _send_sms(user.mobile_number, f"Dear {user.username}, your vote for {candidate.name} ({candidate.party}) has been recorded successfully.")

        messages.success(request, "Your vote has been recorded. Thank you for voting.")
        return redirect('home')

    candidates = election.candidates.all()
    return render(request, 'voting/vote.html', {'election': election, 'candidates': candidates})
