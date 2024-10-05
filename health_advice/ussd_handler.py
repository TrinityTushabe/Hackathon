from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
from .models import USSDSession, HealthTip, FirstAidProcedure, HealthcareProfessional, DisasterVictim, Donation
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

        input_list = text.split('*') if text else []
        current_input = input_list[-1] if input_list else ''

        if created or not input_list:
            response = self.get_main_menu()
            session.current_menu = 'main'
        else:
            response = self.process_menu_choice(session, current_input, input_list)

        session.last_response = response
        session.save()

        logger.info(f"Sending response: {response}")
        return response

    def get_main_menu(self):
        return "CON Welcome to Health and Donation USSD Service\n" \
               "1. Health Tips\n" \
               "2. First Aid Procedures\n" \
               "3. Consult Healthcare Professional\n" \
               "4. Make a Donation\n" \
               "5. Register as Disaster Victim"

    def process_menu_choice(self, session, current_input, full_input):
        logger.info(f"Processing menu choice: current_menu={session.current_menu}, current_input='{current_input}', full_input={full_input}")
        
        try:
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
                elif current_input == '4':
                    session.current_menu = 'donation_type'
                    return "CON Select donation type:\n1. Airtime\n2. Mobile Money"
                elif current_input == '5':
                    session.current_menu = 'register_victim'
                    return "CON Enter your full name:"
                else:
                    return "END Invalid choice. Please try again."

            elif session.current_menu == 'health_tips':
                return self.handle_health_tip_selection(current_input)

            elif session.current_menu == 'first_aid':
                return self.handle_first_aid_selection(current_input)

            elif session.current_menu == 'consult':
                return "END Thank you. A healthcare professional will contact you soon regarding: " + current_input

            elif session.current_menu == 'donation_type':
                if current_input in ['1', '2']:
                    session.current_menu = 'donation_amount'
                    return "CON Enter the amount to donate:"
                else:
                    return "END Invalid choice. Please try again."

            elif session.current_menu == 'donation_amount':
                try:
                    amount = Decimal(current_input)
                    session.current_menu = 'donation_recipient'
                    return "CON Enter recipient's phone number:"
                except (InvalidOperation, ValueError):
                    return "END Invalid amount. Please try again."

            elif session.current_menu == 'donation_recipient':
                donation_type = 'AIRTIME' if full_input[-3] == '1' else 'MONEY'
                amount = Decimal(full_input[-2])
                recipient_phone = current_input
                
                self.process_donation(session.phone_number, recipient_phone, amount, donation_type)
                return f"END Thank you for your {donation_type.lower()} donation of {amount} to {recipient_phone}."

            elif session.current_menu == 'register_victim':
                if len(full_input) == 2:  # This is the name input
                    session.current_menu = 'register_victim_location'
                    return "CON Enter your location:"
                elif len(full_input) == 3:  # This is the location input
                    name = full_input[-2]
                    location = current_input
                    DisasterVictim.objects.create(phone_number=session.phone_number, name=name, location=location)
                    return "END You have been registered as a disaster victim. You will be notified of any donations."

            return "END An error occurred. Please try again."

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return "END An error occurred. Please try again."

    def get_health_tips_menu(self):
        tips = HealthTip.objects.all()
        if not tips:
            return "END No health tips available at the moment."

        menu = "CON Select a health tip:\n"
        for i, tip in enumerate(tips, 1):
            menu += f"{i}. {tip.keyword}\n"
        return menu

    def handle_health_tip_selection(self, text):
        tips = HealthTip.objects.all()
        
        try:
            tip_index = int(text) - 1
            if 0 <= tip_index < len(tips):
                selected_tip = tips[tip_index]
                return f"END Health Tip: {selected_tip.content}"
            else:
                return "END Invalid selection. Please try again."
        except ValueError:
            return "END Invalid input. Please enter a number."

    def get_first_aid_menu(self):
        procedures = FirstAidProcedure.objects.all()
        if not procedures:
            return "END No first aid procedures available at the moment."

        menu = "CON Select a first aid procedure:\n"
        for i, procedure in enumerate(procedures, 1):
            menu += f"{i}. {procedure.keyword}\n"
        return menu

    def handle_first_aid_selection(self, text):
        procedures = FirstAidProcedure.objects.all()
        
        try:
            procedure_index = int(text) - 1
            if 0 <= procedure_index < len(procedures):
                selected_procedure = procedures[procedure_index]
                return f"END First Aid Procedure for {selected_procedure.keyword}:\n{selected_procedure.steps}"
            else:
                return "END Invalid selection. Please try again."
        except ValueError:
            return "END Invalid input. Please enter a number."

    def process_donation(self, donor_phone, recipient_phone, amount, donation_type):
        Donation.objects.create(
            donor_phone=donor_phone,
            recipient_phone=recipient_phone,
            amount=amount,
            donation_type=donation_type
        )
        logger.info(f"Processed donation: {donor_phone} donated {amount} {donation_type} to {recipient_phone}")
        # In a real system, you would integrate with mobile money and airtime APIs here

# Initialize sample data
def initialize_sample_data():
    # Clear existing data
    HealthTip.objects.all().delete()
    FirstAidProcedure.objects.all().delete()
    HealthcareProfessional.objects.all().delete()
    DisasterVictim.objects.all().delete()

    # Add sample health tips
    HealthTip.objects.create(keyword="Exercise", content="Regular exercise can improve your overall health and reduce the risk of chronic diseases.")
    HealthTip.objects.create(keyword="Nutrition", content="A balanced diet rich in fruits, vegetables, and whole grains can boost your immune system.")
    HealthTip.objects.create(keyword="Sleep", content="Aim for 7-9 hours of sleep per night to improve mental and physical health.")

    # Add sample first aid procedures
    FirstAidProcedure.objects.create(keyword="Burns", steps="1. Cool the burn with running water for at least 10 minutes.\n2. Cover with a clean, dry dressing.\n3. Seek medical help if severe.")
    FirstAidProcedure.objects.create(keyword="Cuts", steps="1. Clean the wound with soap and water.\n2. Apply pressure to stop bleeding.\n3. Cover with a sterile bandage.\n4. Seek medical help if deep or won't stop bleeding.")
    FirstAidProcedure.objects.create(keyword="Choking", steps="1. Encourage coughing.\n2. If conscious, perform back blows and abdominal thrusts.\n3. If unconscious, start CPR.\n4. Call emergency services.")

    # Add sample healthcare professionals
    HealthcareProfessional.objects.create(name="Dr. John Smith", phone_number="+1234567890", specialty="General Practitioner")
    HealthcareProfessional.objects.create(name="Dr. Jane Doe", phone_number="+9876543210", specialty="Emergency Medicine")

    # Add sample disaster victims
    DisasterVictim.objects.create(phone_number="+1112223333", name="Alice Johnson", location="Flood Zone A")
    DisasterVictim.objects.create(phone_number="+4445556666", name="Bob Williams", location="Earthquake Area B")

    logger.info("Sample data initialized successfully")