from flask import Flask, request, jsonify, current_app
from datetime import datetime, timedelta
import re
import threading
import time

app = Flask(__name__)

START_HOUR = 9
END_HOUR = 12 #18 termino de labores del bot
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

def send_response(user_id, response):
    with current_app.app_context():
        user_last_activity[user_id] = datetime.now()
        return jsonify({'response': response})

def handle_greeting(user_id):
    if not within_working_hours():
        response = "Lo siento, en este momento no podemos responder. Nuestro horario de atención es de 9:00 AM a 6:00 PM. Te contactaremos a primera hora del siguiente día hábil."
    else:
        user_state[user_id] = {'stage': 'ask_name'}
        user_last_activity[user_id] = datetime.now()
        response = "¡Hola! Soy María del equipo de AccesPack. Bienvenido(a) al proceso de reclutamiento, ¿Cómo te llamas? (solo tu primer nombre)"
    return send_response(user_id, response)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    user_id = data['user_id']
    message = data['message'].strip().lower()

    if user_id not in user_state:
        return handle_greeting(user_id)

    user_last_activity[user_id] = datetime.now()

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
    
    return send_response(user_id, 'No entiendo tu mensaje. Por favor, responde las preguntas anteriores.')

def validate_name(user_id, message):
    if re.match(r"^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$", message):
        user_state[user_id]['name'] = message
        user_state[user_id]['stage'] = 'ask_age'
        return send_response(user_id, "¿Cuántos años tienes?")
    else:
        return send_response(user_id, "Disculpa, tu nombre solo puede contener letras. Por favor, intenta de nuevo.")

def validate_age(user_id, message):
    if message.isdigit():
        age = int(message)
        if 18 <= age <= 99:
            user_state[user_id]['age'] = age
            user_state[user_id]['stage'] = 'ask_email'
            return send_response(user_id, "Por favor ingresa tu Email")
        else:
            return send_response(user_id, "Disculpa, debes tener entre 18 y 99 años. Por favor, proporciona una edad válida.")
    else:
        return send_response(user_id, "Disculpa, tu edad solo puede contener números. Por favor, intenta de nuevo.")

def validate_email(user_id, message):
    if re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", message):
        user_state[user_id]['email'] = message
        user_state[user_id]['stage'] = 'ask_location'
        return send_response(user_id, "¿De dónde eres? (Opciones: Ciudad de México, Estado de México, Querétaro, Monterrey, Puebla)")
    else:
        return send_response(user_id, "Disculpa, puedes proporcionar tu email, el dato que ingresaste no es correcto.")

def validate_location(user_id, message):
    if message in valid_states:
        user_state[user_id]['location'] = valid_states[message]
        user_state[user_id]['stage'] = 'ask_municipality'
        return send_response(user_id, "¿De qué alcaldía o municipio eres?")
    else:
        return send_response(user_id, "Una disculpa, en tu lugar de residencia no contamos con sucursal. En próximas aperturas estaremos en contacto contigo. ¡Ten un excelente día!")

def validate_municipality(user_id, message):
    user_state[user_id]['municipality'] = message
    user_state[user_id]['stage'] = 'ask_car_year'
    return send_response(user_id, "¿Qué año es tu automóvil?(Opciones: 2005 a actualidad)")

def validate_car_year(user_id, message):
    if "no tengo automovil" in message:
        response = "Lamentablemente, no es posible laborar si no cuentas con vehículo. ¡Gracias por tu interés!"
        user_state[user_id]['stage'] = 'end'
        return send_response(user_id, response)
    
    if message.isdigit():
        car_year = int(message)
        current_year = datetime.now().year
        if 2005 <= car_year <= current_year:
            user_state[user_id]['car_year'] = car_year
            user_state[user_id]['stage'] = 'ask_car_model'
            return send_response(user_id, "¿Qué modelo es? (Opciones: Sedan, Hatchback, Camioneta, Otro)")
        else:
            return send_response(user_id, f"Disculpa, el año de tu automóvil debe ser entre 2005 y {current_year}. Por favor, proporciona un año válido.")
    else:
        return send_response(user_id, "Disculpa, puedes proporcionar el año de tu automóvil, el dato que ingresaste no es correcto.")

def validate_car_model(user_id, message):
    if message in valid_car_models:
        user_state[user_id]['car_model'] = message
        user_state[user_id]['stage'] = 'ask_hologram'
        return send_response(user_id, "¿Qué engomado tienes? (Opciones: 00, 0, 1, 2)")
    elif message == "otro":
        user_state[user_id]['stage'] = 'ask_other_car_model'
        return send_response(user_id, "Por favor, especifica el modelo de tu automóvil.")
    else:
        return send_response(user_id, "Disculpa, opción de modelo no válida. Por favor, elige entre Sedan, Hatchback, Camioneta o Otro.")

def validate_other_car_model(user_id, message):
    user_state[user_id]['car_model'] = message
    user_state[user_id]['stage'] = 'ask_hologram'
    return send_response(user_id, "¿Qué engomado tienes? (Opciones: 00, 0, 1, 2)")

def validate_hologram(user_id, message):
    if message in valid_holograms:
        user_state[user_id]['hologram'] = message
        user_state[user_id]['stage'] = 'ask_work_days'
        return send_response(user_id, "¿Cuántos días te gustaría trabajar? (Opciones: 3 a 4 días, 5 a 6 días)")
    else:
        return send_response(user_id, "Disculpa, el engomado de tu auto debe ser 00, 0, 1 o 2. Por favor, intenta de nuevo.")

def validate_work_days(user_id, message):
    if message in valid_work_days:
        user_state[user_id]['work_days'] = message
        user_state[user_id]['stage'] = 'ask_immediate_availability'
        return send_response(user_id, "¿Tienes disponibilidad inmediata? (Opciones: Si, No)")
    else:
        return send_response(user_id, "Disculpa, solo puedes elegir entre 3 a 4 días o 5 a 6 días. Por favor, intenta de nuevo.")

def validate_immediate_availability(user_id, message):
    if message.lower() == 'sí' or message.lower() == 'si':
        response = "¡Gracias, en breve uno de nuestros reclutadores te contactará!"
        send_response(user_id, response)
        return finish_conversation(user_id, message)
    else:
        response = "¿En cuánto tiempo te puedes integrar al equipo?"
        user_state[user_id]['stage'] = 'ask_join_time'
        return send_response(user_id, response)


def finish_conversation(user_id, message):
    response = "¡Gracias, en breve uno de nuestros reclutadores te contactará!"
    return send_response(user_id, response)


def check_inactivity():
    while True:
        now = datetime.now()
        for user_id, last_activity in list(user_last_activity.items()):
            if now - last_activity > INACTIVITY_LIMIT:
                if user_state[user_id]['stage'] == 'end':
                    continue
                if now - last_activity > FOLLOWUP_TIME:
                    user_state[user_id]['stage'] = 'end'
                    send_response(user_id, "Lamentablemente, como no recibimos respuesta, finalizaremos la conversación por ahora. ¡Gracias por tu interés!")
                else:
                    send_response(user_id, "¿Sigues ahí? Por favor, responde a la pregunta anterior para continuar.")
        time.sleep(60)

threading.Thread(target=check_inactivity, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
