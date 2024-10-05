# health_advice/ussd_handler.py
from .models import USSDSession, HealthTip, FirstAidProcedure
from django.http import  HttpResponse

class USSDHandler:

    def handle_request(self, session_id, phone_number, text):
        session, created = USSDSession.objects.get_or_create(
            session_id=session_id,
            defaults={'phone_number': phone_number, 'current_menu': 'main'}
        )

        if created or text == '':
            # New session or initial request
            response = self.get_main_menu()
            session.current_menu = 'main'
        else:
            # Existing session
            response = self.process_menu_choice(session, text)

        session.last_response = response
        session.save()

        return  HttpResponse(response)

    def get_main_menu(self):
        return "CON Welcome to Health Advice USSD Service\n" \
               "1. Health Tips\n" \
               "2. First Aid Procedures\n" \
               "3. Consult Healthcare Professional"

    def process_menu_choice(self, session, text):
        if session.current_menu == 'main':
            if text == '1':
                session.current_menu = 'health_tips'
                return "CON Enter a keyword for health tip:"
            elif text == '2':
                session.current_menu = 'first_aid'
                return "CON Enter a keyword for first aid procedure:"
            elif text == '3':
                session.current_menu = 'consult'
                return "CON Enter your health concern:"
            else:
                return "END Invalid choice. Please try again."

        elif session.current_menu == 'health_tips':
            tip = HealthTip.objects.filter(keyword__icontains=text).first()
            if tip:
                return f"END Health Tip: {tip.content}"
            else:
                return "END Sorry, no health tip found for that keyword."

        elif session.current_menu == 'first_aid':
            procedure = FirstAidProcedure.objects.filter(keyword__icontains=text).first()
            if procedure:
                return f"END First Aid Procedure: {procedure.steps}"
            else:
                return "END Sorry, no first aid procedure found for that keyword."

        elif session.current_menu == 'consult':
            # In a real system, you'd queue this for a healthcare professional
            return "END Thank you. A healthcare professional will contact you soon."

        return "END An error occurred. Please try again."