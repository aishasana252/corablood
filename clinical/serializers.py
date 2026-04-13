from rest_framework import serializers
from .models import DonorWorkflow, Question, QuestionnaireResponse, VitalSigns, BloodDraw, VitalLimit, AdverseReaction, PostDonationSurvey, PreSeparation, DonationAttachment, LabResult, LabOrder, DonorMedicationRecord, Medication

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text_en', 'text_ar', 'category', 'defer_if_answer_is', 'deferral_days', 'is_active', 'order']
        extra_kwargs = {
            'text_ar': {'required': False, 'allow_blank': True}
        }

    def validate(self, data):
        if not data.get('text_ar'):
            data['text_ar'] = data.get('text_en', 'Translation Pending')
        return data

class QuestionnaireResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireResponse
        fields = ['answers', 'passed', 'signature_data', 'additional_notes']

class VitalSignsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSigns
        fields = ['weight_kg', 'bp_systolic', 'bp_diastolic', 'pulse', 'temperature_c', 'hemoglobin', 'iqama_checked']

class VitalLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalLimit
        fields = '__all__'

class BloodDrawSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = BloodDraw
        fields = [
            'bag_visual_inspection', 'iqama_checked', 'both_arm_inspection',
            'arm', 'blood_type', 'blood_nature', 'drawn_start_time',
            'drawn_end_time', 'segment_number', 'first_unit_volume',
            'duration_minutes'
        ]
        extra_kwargs = {
            'blood_type': {'required': False, 'allow_blank': True},
            'segment_number': {'required': False, 'allow_blank': True},
            'drawn_start_time': {'required': False},
            'drawn_end_time': {'required': False},
            'first_unit_volume': {'required': False, 'allow_null': True}
        }

class AdverseReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdverseReaction
        fields = '__all__'

class PostDonationSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostDonationSurvey
        fields = '__all__'

class DonorMedicationRecordSerializer(serializers.ModelSerializer):
    medications_taken_names = serializers.SerializerMethodField()
    
    class Meta:
        model = DonorMedicationRecord
        fields = ['is_on_medication', 'medications_taken', 'medications_taken_names', 'other_medication_notes', 'notes', 'pharmacist_reviewed', 'deferred_due_to_medication']

    def get_medications_taken_names(self, obj):
        return [m.name for m in obj.medications_taken.all()]

class PreSeparationSerializer(serializers.ModelSerializer):
    received_by_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PreSeparation
        fields = '__all__'

    def get_received_by_name(self, obj):
        return obj.received_by.get_full_name() if obj.received_by else None

    def get_verified_by_name(self, obj):
        return obj.verified_by.get_full_name() if obj.verified_by else None

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonorWorkflow
        fields = ['id', 'status', 'created_at']

class WorkflowDetailSerializer(serializers.ModelSerializer):
    vitals = VitalSignsSerializer(source='vitalsigns_set', many=True, read_only=True)
    blood_draw = BloodDrawSerializer(read_only=True)
    adverse_reaction = AdverseReactionSerializer(read_only=True)
    survey = PostDonationSurveySerializer(read_only=True)
    pre_separation = PreSeparationSerializer(read_only=True)
    medication_record = DonorMedicationRecordSerializer(read_only=True)
    
    # New Lab Fields - Using method fields to ensure correct querying
    lab_results = serializers.SerializerMethodField()
    lab_orders = serializers.SerializerMethodField()
    
    answers = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()

    class Meta:
        model = DonorWorkflow
        fields = ['id', 'status', 'created_at', 'code', 'vitals', 'blood_draw', 'answers', 'adverse_reaction', 'survey', 'pre_separation', 'lab_results', 'lab_orders', 'medication_record']
    
    def get_code(self, obj):
        """Return the official donation code if available, fallback to ID."""
        if obj.donation_code:
            return obj.donation_code
        return f'WF-{obj.id:05d}'
    
    def get_answers(self, obj):
        if hasattr(obj, 'questionnaire'):
             return obj.questionnaire.answers
        return []

    def get_lab_results(self, obj):
        from .models import LabResult
        results = LabResult.objects.filter(workflow=obj).order_by('-created_at')
        return LabResultSerializer(results, many=True).data

    def get_lab_orders(self, obj):
        from .models import LabOrder
        orders = LabOrder.objects.filter(workflow=obj).order_by('-created_at')
        return LabOrderSerializer(orders, many=True).data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        # Robust lookup: Bypass descriptor/caching by querying DB directly
        vitals = VitalSigns.objects.filter(workflow=instance).first()
        if vitals:
             ret['vitals'] = VitalSignsSerializer(vitals).data
        else:
             ret['vitals'] = None
        
        # Blood Draw
        draw = BloodDraw.objects.filter(workflow=instance).first()
        if draw:
            ret['blood_draw'] = BloodDrawSerializer(draw).data
        else:
             ret['blood_draw'] = None

        # Adverse Reaction
        reaction = AdverseReaction.objects.filter(workflow=instance).first()
        if reaction:
             ret['adverse_reaction'] = AdverseReactionSerializer(reaction).data
        else:
             ret['adverse_reaction'] = None
             
        # Survey
        survey = PostDonationSurvey.objects.filter(workflow=instance).first()
        if survey:
             ret['survey'] = PostDonationSurveySerializer(survey).data
        else:
             ret['survey'] = None

        # Pre-Separation
        pre_sep = PreSeparation.objects.filter(workflow=instance).first()
        if pre_sep:
             ret['pre_separation'] = PreSeparationSerializer(pre_sep).data
        else:
             ret['pre_separation'] = None

        # Questionnaire
        q = QuestionnaireResponse.objects.filter(workflow=instance).first()
        if q:
            ret['questionnaire'] = QuestionnaireResponseSerializer(q).data
        else:
            ret['questionnaire'] = None

        # Medication Record
        med_rec = DonorMedicationRecord.objects.filter(workflow=instance).first()
        if med_rec:
            ret['medication_record'] = DonorMedicationRecordSerializer(med_rec).data
        else:
            ret['medication_record'] = None

        return ret

class DonationAttachmentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = DonationAttachment
        fields = ['id', 'title', 'notes', 'file', 'file_name', 'file_url', 'created_at', 'created_by_name']
        read_only_fields = ['created_by', 'created_at']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else 'System'

    def get_file_name(self, obj):
        return obj.file.name.split('/')[-1] if obj.file else ''

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None

class LabResultSerializer(serializers.ModelSerializer):
    technician_name = serializers.SerializerMethodField()
    class Meta:
        model = LabResult
        fields = '__all__'
    
    def get_technician_name(self, obj):
        return obj.technician.get_full_name() if obj.technician else 'System'

class LabOrderSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    class Meta:
        model = LabOrder
        fields = '__all__'

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else 'System'

class DonationListSerializer(serializers.ModelSerializer):
    donation_code = serializers.CharField(source='id') # Using ID as code for now, or use a specific field if exists
    donation_date = serializers.DateTimeField(source='created_at')
    donor_details = serializers.SerializerMethodField()
    components_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = DonorWorkflow
        fields = ['id', 'donation_code', 'donation_date', 'status', 'donor_details', 'components_summary']

    def get_donor_details(self, obj):
        return {
            'full_name': obj.donor.full_name,
            'blood_group': obj.donor.blood_group,
            'national_id': obj.donor.national_id,
            'iqama_id': obj.donor.national_id, # Legacy fallback
            'mobile': obj.donor.mobile
        }

    def get_components_summary(self, obj):
        # Avoid circular import at top level
        from inventory.models import BloodComponent
        comps = obj.components.all()
        if comps.exists():
            return ", ".join([c.component_type for c in comps])
        return "Whole Blood"
