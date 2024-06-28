from datetime import datetime, timedelta
import re

START_HOUR = 9
END_HOUR = 18 
INACTIVITY_LIMIT = timedelta(minutes=5)
FOLLOWUP_TIME = timedelta(minutes=3)

user_state = {}
user_last_activity = {}

valid_states = {
    "ciudad de méxico": "Ciudad de México",
    "estado de méxico": "Estado de México",
    "querétaro": "Querétaro",
    "puebla": "Puebla",
    "monterrey": "Monterrey"
}

valid_car_models = ["sedan", "hatchback", "camioneta"]
valid_holograms = ["00", "0", "1", "2"]
valid_work_days = ["3 a 4 días", "5 a 6 días"]

def within_working_hours():
    current_hour = datetime.now().hour
    return START_HOUR <= current_hour < END_HOUR

def send_response(response):
    print(response)

def get_user_input():
    return input("> ").strip().lower()

def handle_greeting(user_id):
    if not within_working_hours():
        response = "Lo siento, en este momento no podemos responder. Nuestro horario de atención es de 9:00 AM a 6:00 PM. Te contactaremos a primera hora del siguiente día hábil."
    else:
        user_state[user_id] = {'stage': 'ask_name'}
        user_last_activity[user_id] = datetime.now()
        response = "¡Hola! Soy María del equipo de AccesPack. Bienvenido(a) al proceso de reclutamiento, ¿Cómo te llamas? (solo tu primer nombre)"
    send_response(response)
    return get_user_input()

def validate_name(user_id, message):
    if re.match(r"^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$", message):
        user_state[user_id]['name'] = message
        user_state[user_id]['stage'] = 'ask_age'
        send_response("¿Cuántos años tienes?")
    else:
        send_response("Disculpa, tu nombre solo puede contener letras. Por favor, intenta de nuevo.")
    return get_user_input()

def validate_age(user_id, message):
    if message.isdigit():
        age = int(message)
        if 18 <= age <= 99:
            user_state[user_id]['age'] = age
            user_state[user_id]['stage'] = 'ask_email'
            send_response("Por favor ingresa tu Email")
        else:
            send_response("Disculpa, debes tener entre 18 y 35 años. Por favor, proporciona una edad válida.")
    else:
        send_response("Disculpa, tu edad solo puede contener números. Por favor, intenta de nuevo.")
    return get_user_input()

def validate_email(user_id, message):
    if re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", message):
        user_state[user_id]['email'] = message
        user_state[user_id]['stage'] = 'ask_location'
        send_response("¿De dónde eres? (Opciones: Ciudad de México, Estado de México, Querétaro, Monterrey, Puebla)")
    else:
        send_response("Disculpa, puedes proporcionar tu email, el dato que ingresaste no es correcto.")
    return get_user_input()

def validate_location(user_id, message):
    if message in valid_states:
        user_state[user_id]['location'] = valid_states[message]
        user_state[user_id]['stage'] = 'ask_municipality'
        send_response("¿De qué alcaldía o municipio eres?")
    else:
        send_response("Una disculpa, en tu lugar de residencia no contamos con sucursal. En próximas aperturas estaremos en contacto contigo. ¡Ten un excelente día!")
    return get_user_input()

def validate_municipality(user_id, message):
    user_state[user_id]['municipality'] = message
    user_state[user_id]['stage'] = 'ask_car_year'
    send_response("¿Qué año es tu automóvil? (Opciones: 2005 a actualidad)")
    return get_user_input()

def validate_car_year(user_id, message):
    if "no tengo automovil" in message:
        response = "Lamentablemente, no es posible laborar si no cuentas con vehículo. ¡Gracias por tu interés!"
        user_state[user_id]['stage'] = 'end'
        send_response(response)
        return None
    
    if message.isdigit():
        car_year = int(message)
        current_year = datetime.now().year
        if 2005 <= car_year <= current_year:
            user_state[user_id]['car_year'] = car_year
            user_state[user_id]['stage'] = 'ask_car_model'
            send_response("¿Qué modelo es? (Opciones: Sedan, Hatchback, Camioneta, Otro)")
        else:
            send_response(f"Disculpa, el año de tu automóvil debe ser entre 2005 y {current_year}. Por favor, proporciona un año válido.")
    else:
        send_response("Disculpa, puedes proporcionar el año de tu automóvil, el dato que ingresaste no es correcto.")
    return get_user_input()

def validate_car_model(user_id, message):
    if message in valid_car_models:
        user_state[user_id]['car_model'] = message
        user_state[user_id]['stage'] = 'ask_hologram'
        send_response("¿Qué engomado tienes? (Opciones: 00, 0, 1, 2)")
    elif message == "otro":
        user_state[user_id]['stage'] = 'ask_other_car_model'
        send_response("Por favor, especifica el modelo de tu automóvil.")
    else:
        send_response("Disculpa, opción de modelo no válida. Por favor, elige entre Sedan, Hatchback, Camioneta o Otro.")
    return get_user_input()

def validate_other_car_model(user_id, message):
    user_state[user_id]['car_model'] = message
    user_state[user_id]['stage'] = 'ask_hologram'
    send_response("¿Qué engomado tienes? (Opciones: 00, 0, 1, 2)")
    return get_user_input()

def validate_hologram(user_id, message):
    if message in valid_holograms:
        user_state[user_id]['hologram'] = message
        user_state[user_id]['stage'] = 'ask_work_days'
        send_response("¿Cuántos días te gustaría trabajar? (Opciones: 3 a 4 días, 5 a 6 días)")
    else:
        send_response("Disculpa, el engomado de tu auto debe ser 00, 0, 1 o 2. Por favor, intenta de nuevo.")
    return get_user_input()

def validate_work_days(user_id, message):
    if message in valid_work_days:
        user_state[user_id]['work_days'] = message
        user_state[user_id]['stage'] = 'ask_immediate_availability'
        send_response("¿Tienes disponibilidad inmediata? (Opciones: Sí, No)")
    else:
        send_response("Disculpa, solo puedes elegir entre 3 a 4 días o 5 a 6 días. Por favor, intenta de nuevo.")
    return get_user_input()

def validate_immediate_availability(user_id, message):
    if message.lower() == 'sí' or message.lower() == 'si':
        response = "¡Gracias, en breve uno de nuestros reclutadores te contactará!"
        user_state[user_id]['stage'] = 'end'
        send_response(response)
        return None
    else:
        user_state[user_id]['stage'] = 'ask_join_time'
        send_response("¿En cuánto tiempo te puedes integrar al equipo?")
        return get_user_input()

def finish_conversation(user_id, message):
    response = "¡Gracias, en breve uno de nuestros reclutadores te contactará!"
    print(response)
    return None  

def handle_conversation(user_id, message):
    stage = user_state[user_id]['stage']
    handlers = {
        'ask_name': validate_name,
        'ask_age': validate_age,
        'ask_email': validate_email,
        'ask_location': validate_location,
        'ask_municipality': validate_municipality,
        'ask_car_year': validate_car_year,
        'ask_car_model': validate_car_model,
        'ask_other_car_model': validate_other_car_model,
        'ask_hologram': validate_hologram,
        'ask_work_days': validate_work_days,
        'ask_immediate_availability': validate_immediate_availability,
        'ask_join_time': finish_conversation
    }
    if stage in handlers:
        return handlers[stage](user_id, message)
    else:
        send_response('No entiendo tu mensaje. Por favor, responde las preguntas anteriores.')
        return get_user_input()

if __name__ == '__main__':
    user_id = "dummy_user_id"
    user_input = handle_greeting(user_id)
    while user_state[user_id]['stage'] != 'end':
        user_input = handle_conversation(user_id, user_input)
        if user_input is None:
            break
