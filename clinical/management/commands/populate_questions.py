from django.core.management.base import BaseCommand
from clinical.models import Question

class Command(BaseCommand):
    help = 'Populates standard blood bank questions'

    def handle(self, *args, **kwargs):
        questions = [
            {
                "text_en": "Are you feeling well and healthy today?",
                "text_ar": "هل تشعر بصحة جيدة اليوم؟",
                "category": "General",
                "defer_if": "No",
                "days": 1
            },
            {
                "text_en": "Have you taken any antibiotics in the last 7 days?",
                "text_ar": "هل تناولت أي مضادات حيوية خلال الـ 7 أيام الماضية؟",
                "category": "Medical",
                "defer_if": "Yes",
                "days": 7
            },
            {
                "text_en": "Have you visited the dentist in the last 3 days?",
                "text_ar": "هل زرت طبيب الأسنان خلال الـ 3 أيام الماضية؟",
                "category": "Medical",
                "defer_if": "Yes",
                "days": 3
            },
            {
                "text_en": "Have you traveled outside the Kingdom in the last 28 days?",
                "text_ar": "هل سافرت خارج المملكة خلال الـ 28 يوماً الماضية؟",
                "category": "Travel",
                "defer_if": "Yes",
                "days": 28
            },
             {
                "text_en": "Have you ever had hepatitis, jaundice, or malaria?",
                "text_ar": "هل أصبت سابقاً بالالتهاب الكبدي، اليرقان، أو الملاريا؟",
                "category": "HighRisk",
                "defer_if": "Yes",
                "days": 0 # Permanent
            },
        ]

        for i, q in enumerate(questions):
            Question.objects.get_or_create(
                text_en=q['text_en'],
                defaults={
                    'text_ar': q['text_ar'],
                    'category': q['category'],
                    'defer_if_answer_is': q['defer_if'],
                    'deferral_days': q['days'],
                    'order': i + 1
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully populated questions'))
