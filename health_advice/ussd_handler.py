from django.http import HttpResponse
from .models import USSDSession, HealthTip, FirstAidProcedure
import logging

# Set up logging
logger = logging.getLogger(__name__)

class USSDHandler:
    def handle_request(self, session_id, phone_number, text):
        logger.info(f"Received request: session_id={session_id}, phone_number={phone_number}, text='{text}'")
        
        session, created = USSDSession.objects.get_or_create(
            session_id=session_id,
            defaults={'phone_number': phone_number, 'current_menu': 'main'}
        )

        # Parse the USSD input
        input_list = text.split('*') if text else []
        current_input = input_list[-1] if input_list else ''

        if created or not input_list:
            # New session or initial request
            response = self.get_main_menu()
            session.current_menu = 'main'
        else:
            # Existing session
            response = self.process_menu_choice(session, current_input, input_list)

        session.last_response = response
        session.save()

        logger.info(f"Sending response: {response}")
        return HttpResponse(response)

    def get_main_menu(self):
        return "CON Welcome to Health Advice USSD Service\n" \
               "1. Health Tips\n" \
               "2. First Aid Procedures\n" \
               "3. Consult Healthcare Professional"

    def process_menu_choice(self, session, current_input, full_input):
        logger.info(f"Processing menu choice: current_menu={session.current_menu}, current_input='{current_input}', full_input={full_input}")
        
        if session.current_menu == 'main':
            if current_input == '1':
                session.current_menu = 'health_tips'
                return self.get_health_tips_menu()
            elif current_input == '2':
                session.current_menu = 'first_aid'
                return self.get_first_aid_menu()
            elif current_input == '3':
                session.current_menu = 'consult'
                return "CON Enter your health concern:"
            else:
                return "END Invalid choice. Please try again."

        elif session.current_menu == 'health_tips':
            return self.handle_health_tip_selection(current_input)

        elif session.current_menu == 'first_aid':
            return self.handle_first_aid_selection(current_input)

        elif session.current_menu == 'consult':
            # In a real system, you'd queue this for a healthcare professional
            return "END Thank you. A healthcare professional will contact you soon regarding: " + current_input

        return "END An error occurred. Please try again."

    def get_health_tips_menu(self):
        tips = HealthTip.objects.all()
        if not tips:
            return "END No health tips available at the moment."

        menu = "CON Select a health tip:\n"
        for i, tip in enumerate(tips, 1):
            menu += f"{i}. {tip.keyword}\n"
        logger.info(f"Generated health tips menu: {menu}")
        return menu

    def handle_health_tip_selection(self, text):
        logger.info(f"Handling health tip selection: text='{text}'")
        tips = HealthTip.objects.all()
        
        if text == '':
            return self.get_health_tips_menu()
        
        try:
            tip_index = int(text) - 1
            if 0 <= tip_index < len(tips):
                selected_tip = tips[tip_index]
                return f"END Health Tip: {selected_tip.content}"
            else:
                return "END Invalid selection. Please try again."
        except ValueError:
            logger.error(f"Invalid input for health tip selection: '{text}'")
            return "END Invalid input. Please enter a number."

    def get_first_aid_menu(self):
        procedures = FirstAidProcedure.objects.all()
        if not procedures:
            return "END No first aid procedures available at the moment."

        menu = "CON Select a first aid procedure:\n"
        for i, procedure in enumerate(procedures, 1):
            menu += f"{i}. {procedure.keyword}\n"
        logger.info(f"Generated first aid menu: {menu}")
        return menu

    def handle_first_aid_selection(self, text):
        logger.info(f"Handling first aid selection: text='{text}'")
        procedures = FirstAidProcedure.objects.all()
        
        if text == '':
            return self.get_first_aid_menu()
        
        try:
            procedure_index = int(text) - 1
            if 0 <= procedure_index < len(procedures):
                selected_procedure = procedures[procedure_index]
                return f"END First Aid Procedure for {selected_procedure.keyword}:\n{selected_procedure.steps}"
            else:
                return "END Invalid selection. Please try again."
        except ValueError:
            logger.error(f"Invalid input for first aid selection: '{text}'")
            return "END Invalid input. Please enter a number."

# Initialize sample data
def initialize_sample_data():
    # Clear existing data
    HealthTip.objects.all().delete()
    FirstAidProcedure.objects.all().delete()

    # Add sample health tips
    HealthTip.objects.create(keyword="Exercise", content="Regular exercise can improve your overall health and reduce the risk of chronic diseases.")
    HealthTip.objects.create(keyword="Nutrition", content="A balanced diet rich in fruits, vegetables, and whole grains can boost your immune system.")
    HealthTip.objects.create(keyword="Sleep", content="Aim for 7-9 hours of sleep per night to improve mental and physical health.")

    # Add sample first aid procedures
    FirstAidProcedure.objects.create(keyword="Burns", steps="1. Cool the burn with running water for at least 10 minutes.\n2. Cover with a clean, dry dressing.\n3. Seek medical help if severe.")
    FirstAidProcedure.objects.create(keyword="Cuts", steps="1. Clean the wound with soap and water.\n2. Apply pressure to stop bleeding.\n3. Cover with a sterile bandage.\n4. Seek medical help if deep or won't stop bleeding.")
    FirstAidProcedure.objects.create(keyword="Choking", steps="1. Encourage coughing.\n2. If conscious, perform back blows and abdominal thrusts.\n3. If unconscious, start CPR.\n4. Call emergency services.")

    logger.info("Sample data initialized successfully")