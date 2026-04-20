from django.utils import timezone
from .models import DonorWorkflow, QuestionnaireResponse, VitalSigns, BloodDraw

class WorkflowService:
    @staticmethod
    def get_active_workflow(donor):
        return DonorWorkflow.objects.filter(
            donor=donor
        ).exclude(
            status=DonorWorkflow.Step.COMPLETED
        ).order_by('-created_at').first()

    @staticmethod
    def start_workflow(donor, user=None):
        # check if active exists
        active = WorkflowService.get_active_workflow(donor)
        if active:
            return active
        
        return DonorWorkflow.objects.create(
            donor=donor,
            status=DonorWorkflow.Step.QUESTIONNAIRE,
            created_by=user
        )

    @staticmethod
    def submit_questionnaire(workflow, answers, user=None):
        # Create response
        # Simple logic: if any answer is 'yes' -> fail? No, that's brittle. 
        # For V3, let's assume all passed for now or implement rule engine later.
        # But for the "Engine" part:
        
        response, created = QuestionnaireResponse.objects.update_or_create(
            workflow=workflow,
            defaults={
                'answers': answers,
                'passed': True, # TODO: Rule Engine
                'reviewed_by': user
            }
        )
        
        if response.passed:
            workflow.status = DonorWorkflow.Step.MEDICATION
            workflow.save()
            
        return response

    @staticmethod
    def _track_changes(instance, new_data, user, request_type, ref_code):
        from .models import ModificationRequest
        changes = []
        for key, new_value in new_data.items():
            if hasattr(instance, key):
                old_value = getattr(instance, key)
                # Simple comparison. For complex types, might need string conversion
                if str(old_value) != str(new_value):
                    changes.append(f"{key}: {old_value} -> {new_value}")
        
        if changes:
            ModificationRequest.objects.create(
                request_type=request_type,
                reference_code=ref_code,
                modification_details="\n".join(changes),
                created_by=user,
                status=ModificationRequest.Status.DONE # Auto-approved for now, but logged
            )

    @staticmethod
    def submit_vitals(workflow, data, user=None):
        # Validation Logic
        passed = True
        reasons = []

        from .models import VitalLimit
        limits = VitalLimit.load()

        if data.get('weight_kg', 0) < limits.min_weight_kg:
            passed = False
            reasons.append(f"Weight under {limits.min_weight_kg}kg")
        
        if data.get('hemoglobin', 0) < limits.min_hemoglobin:
            passed = False
            reasons.append(f"Hemoglobin under {limits.min_hemoglobin}")
            
        if data.get('temperature_c', 0) > limits.max_temperature_c:
            passed = False
            reasons.append(f"Temperature over {limits.max_temperature_c}")

        # Check for existing to track changes
        existing = VitalSigns.objects.filter(workflow=workflow).first()
        if existing:
            from .models import ModificationRequest
            WorkflowService._track_changes(
                existing, 
                data, 
                user, 
                ModificationRequest.RequestType.DONATION, 
                f"VitalSigns-{workflow.id}"
            )

        vitals, created = VitalSigns.objects.update_or_create(
            workflow=workflow,
            defaults={
                'examiner': user,
                'passed': passed,
                **data
            }
        )
        
        if passed:
            workflow.status = DonorWorkflow.Step.COLLECTION
        else:
            workflow.status = DonorWorkflow.Step.DEFERRED
            
        workflow.save()
        return vitals, reasons

    @staticmethod
    def submit_blood_draw(workflow, data, user=None):
        # Update logic to match new BloodDraw model
        existing = BloodDraw.objects.filter(workflow=workflow).first()
        if existing:
            from .models import ModificationRequest
            WorkflowService._track_changes(
                existing, 
                data, 
                user, 
                ModificationRequest.RequestType.DONATION, 
                f"BloodDraw-{workflow.id}"
            )

        draw, created = BloodDraw.objects.update_or_create(
            workflow=workflow,
            defaults={
                'examiner': user,
                'bag_visual_inspection': data.get('bag_visual_inspection', False),
                'iqama_checked': data.get('iqama_checked', False),
                'both_arm_inspection': data.get('both_arm_inspection', False),
                'arm': data.get('arm', ''),
                'blood_type': data.get('blood_type', ''),
                'blood_nature': data.get('blood_nature', 'Whole Blood'),
                'first_unit_volume': data.get('first_unit_volume'),
                'drawn_start_time': data.get('drawn_start_time'),
                'drawn_end_time': data.get('drawn_end_time'),
                'segment_number': data.get('segment_number', ''),
                # Apheresis fields
                'procedure_type': data.get('procedure_type'),
                'is_filtered': data.get('is_filtered', False),
                'total_acd_used': data.get('total_acd_used'),
                'actual_acd_to_donor': data.get('actual_acd_to_donor'),
                'post_platelet_count': data.get('post_platelet_count'),
                'post_hct': data.get('post_hct'),
                'blood_volume_processed': data.get('blood_volume_processed'),
                'total_saline_used': data.get('total_saline_used'),
                'apheresis_start_time': data.get('apheresis_start_time'),
                'apheresis_end_time': data.get('apheresis_end_time'),
                'kit_lot_no': data.get('kit_lot_no'),
                'kit_lot_expiry': data.get('kit_lot_expiry') or None,
                'acd_lot_no': data.get('acd_lot_no'),
                'acd_lot_expiry': data.get('acd_lot_expiry') or None,
                'machine_name': data.get('machine_name'),
                'platelets_collected_volume': data.get('platelets_collected_volume'),
                'yield_of_platelets': data.get('yield_of_platelets'),
                'volume_of_acd_in_platelets': data.get('volume_of_acd_in_platelets'),
                'inventory_units_count': data.get('inventory_units_count', 1),
                'donation_reaction': data.get('donation_reaction', False),
            }
        )
        
        # Auto-generate Donation Code on Workflow if missing
        if not workflow.donation_code:
            import datetime
            from django.db.models import Max
            import re
            
            now = datetime.datetime.now()
            yy = now.strftime('%y') # e.g. 26
            hospital_id = "1077"    # Constant
            prefix = f"H{hospital_id}{yy}"
            
            # Find the max serial for this year/hospital prefix
            # donation_code format: H107726000001
            max_code = DonorWorkflow.objects.filter(
                donation_code__startswith=prefix
            ).aggregate(Max('donation_code'))['donation_code__max']
            
            if max_code:
                # Extract serial: H107726[000001]
                # The numeric part starts after prefix (length of prefix)
                serial_part = max_code[len(prefix):]
                try:
                    next_serial = int(serial_part) + 1
                except ValueError:
                    next_serial = 1
            else:
                next_serial = 1
                
            serial_str = str(next_serial).zfill(6) 
            
            workflow.donation_code = f"{prefix}{serial_str}"
            workflow.save(update_fields=['donation_code'])

            # Log this generation
            from .models import ModificationRequest
            ModificationRequest.objects.create(
                request_type=ModificationRequest.RequestType.DONATION,
                reference_code=workflow.donation_code,
                modification_details=f"Generated Donation Code: {workflow.donation_code}",
                created_by=user,
                status=ModificationRequest.Status.DONE
            )
        
        workflow.status = DonorWorkflow.Step.POST_DONATION
        workflow.save()
        return draw

    @staticmethod
    def submit_lab_results(workflow, viral_result, blood_group, user=None):
        from .models import LabResult
        
        # Create or update test result
        test, created = LabResult.objects.update_or_create(
            workflow=workflow,
            test_name='Viral Screening',
            defaults={
                'result_value': viral_result,
                'technician': user,
                'tested_at': timezone.now()
            }
        )
        
        if viral_result == 'Negative':
            workflow.status = DonorWorkflow.Step.COMPLETED
            # Trigger Inventory Release
            from inventory.services import InventoryService
            InventoryService.release_components(workflow, passed=True)
        else:
            workflow.status = DonorWorkflow.Step.DEFERRED
            from inventory.services import InventoryService
            InventoryService.release_components(workflow, passed=False)
            
        workflow.save()
        return test
