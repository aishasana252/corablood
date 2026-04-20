from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from donors.models import Donor
from clinical.models import DonorWorkflow, Question, Medication, QuestionnaireResponse, PostDonationSurvey, DonorMedicationRecord
from .base import _get_or_create_workflow


@csrf_exempt
@login_required
def portal_questionnaire(request):
    donor = request.user.donor_profile
    workflow = _get_or_create_workflow(request, donor)

    if not workflow:
        messages.info(request, "No active donation workflow found. Please book an appointment.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        import json
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except:
                data = {}
        else:
            data = request.POST

        answers = {}
        signature_data = data.get('signature_data')
        additional_notes = data.get('additional_notes')

        if isinstance(data.get('answers'), dict):
            answers = data.get('answers')
        else:
            for key, value in data.items():
                if key.startswith('q_'):
                    answers[key.replace('q_', '')] = value

        QuestionnaireResponse.objects.update_or_create(
            workflow=workflow,
            defaults={
                'answers': answers,
                'signature_data': signature_data,
                'additional_notes': additional_notes,
                'passed': True
            }
        )
        workflow.status = DonorWorkflow.Step.MEDICATION
        workflow.save()
        messages.success(request, "Questionnaire submitted and signed successfully.")
        return redirect('portal:dashboard')

    raw_questions = Question.objects.filter(is_active=True).order_by('order')
    categories = {}
    for q in raw_questions:
        if q.category not in categories:
            categories[q.category] = []
        categories[q.category].append(q)

    return render(request, 'donors/portal/questionnaire.html', {
        'workflow': workflow,
        'categories': categories,
        'donor': donor
    })


@csrf_exempt
@login_required
def portal_medication(request):
    donor = request.user.donor_profile
    workflow = _get_or_create_workflow(request, donor)

    if not workflow:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        import json
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except:
                data = {}
        else:
            data = request.POST

        is_on_med = data.get('is_on_medication') == 'true' or data.get('is_on_medication') is True

        if isinstance(data.get('medications'), list):
            med_ids = data.get('medications')
        else:
            med_ids = request.POST.getlist('medications')

        notes = data.get('notes')

        record, _ = DonorMedicationRecord.objects.update_or_create(
            workflow=workflow,
            defaults={
                'is_on_medication': is_on_med,
                'notes': notes,
                'recorded_by': request.user
            }
        )
        if med_ids:
            record.medications_taken.set(med_ids)

        # Advance to clinical stages (VITALS) regardless of appointment status
        workflow.status = DonorWorkflow.Step.VITALS
        workflow.save()
        messages.success(request, "Medication record updated.")
        return redirect('portal:dashboard')

    medications_list = Medication.objects.filter(is_active=True).order_by('category', 'name')
    categories = {}
    for med in medications_list:
        if med.category not in categories:
            categories[med.category] = []
        categories[med.category].append(med)

    return render(request, 'donors/portal/medication.html', {
        'workflow': workflow,
        'categories': categories
    })


@login_required
def portal_post_donation(request):
    donor = request.user.donor_profile
    workflow = _get_or_create_workflow(request, donor)

    if not workflow:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        comfort = request.POST.get('comfort', 5)
        staff = request.POST.get('staff', 5)
        wait = request.POST.get('wait', 5)
        comments = request.POST.get('comments')

        PostDonationSurvey.objects.update_or_create(
            workflow=workflow,
            defaults={
                'comfort_during_process': comfort,
                'staff_satisfaction': staff,
                'wait_time_satisfaction': wait,
                'comments': comments
            }
        )
        workflow.status = DonorWorkflow.Step.LABS
        workflow.save()
        messages.success(request, "Thank you for your feedback!")
        return redirect('portal:dashboard')

    survey_options = [
        ('1', '😡'),
        ('2', '😟'),
        ('3', '😐'),
        ('4', '😊'),
        ('5', '😍'),
    ]

    return render(request, 'donors/portal/post_donation.html', {
        'workflow': workflow,
        'survey_options': survey_options
    })
