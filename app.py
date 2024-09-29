from flask import (
    Flask,
    render_template,
    request,
    Response,
    stream_with_context,
    jsonify,
)
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
from typing import Any, Dict

import requests
import io
import os
import google.generativeai as genai


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# WARNING: Do not share code with you API key hard coded in it.
# Get your Gemini API key from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize configuration
genai.configure(api_key=GOOGLE_API_KEY)
# The rate limits are low on this model, so you might
# need to switch to `gemini-pro`
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
"api code start"
REQUEST_HEADERS = {"User-Agent": "Chrome/103.0.5026.0"}
LOCATIONS_URL = "https://api.dineoncampus.com/v1/locations/status?site_id=5e6fcc641ca48e0cacd93b04&platform="
MENU_URL = "https://api.dineoncampus.com/v1/location/{location_id}/periods/{period_id}?platform=0&date={date_str}"

LOCATIONS = {
    "ETHEL'S",
    "THE EATERY",
    "PANERA BREAD",
    "TRUE BURGER",
    "THE PERCH",
    "FORBES STREET MARKET",
    "BUNSEN BREWER",
    "WICKED PIE",
    "SMOKELAND BBQ AT THE PETERSEN EVENTS CENTER",
    "THE MARKET AT TOWERS",
    "THE DELICATESSEN",
    "CAMPUS COFFEE & TEA CO - TOWERS",
    "PA TACO CO.",
    "FT. PITT SUBS",
    "CREATE",
    "POM & HONEY",
    "THE ROOST",
    "CATHEDRAL SUSHI",
    "BURRITO BOWL",
    "CHICK-FIL-A",
    "SHAKE SMART",
    "STEEL CITY KITCHEN",
    "SMOKELAND BBQ FOOD TRUCK",
    "CAMPUS COFFEE & TEA CO - SUTHERLAND",
    "THE MARKET AT SUTHERLAND",
    "PLATE TO PLATE AT SUTHERLAND MARKET",
    "EINSTEIN BROS. BAGELS - POSVAR",
    "EINSTEIN BROS. BAGELS - BENEDUM",
    "BOTTOM LINE BISTRO",
    "CAFE VICTORIA",
    "CAFE 1787",
    "CAMPUS COFFEE & TEA CO - PUBLIC HEALTH",
    "RXPRESSO",
    "SIDEBAR CAFE",
    "CAFE 1923",
    }

def get_locations() -> Dict[str, Any]:
    resp = requests.get(LOCATIONS_URL, headers=REQUEST_HEADERS)
    locations = resp.json()["locations"]
    return {location["name"].upper(): location for location in locations}

def get_location_menu(location: str, date: datetime = None) -> Any:
    location = location.upper()
    if location not in LOCATIONS:
        raise ValueError("Invalid Dining Location")
    
    if date is None:
        date = datetime.today()

    date_str = date.strftime("%y-%m-%d")
    location_id = get_locations()[location]["id"]
    
    periods_resp = requests.get(
        f"https://api.dineoncampus.com/v1/location/{location_id}/periods?platform=0&date={date_str}",
        headers=REQUEST_HEADERS,
    )
    
    periods = periods_resp.json()["periods"]
    if not periods:
        return {}

    period_id = periods[0]["id"]
    menu_resp = requests.get(
        MENU_URL.format(location_id=location_id, period_id=period_id, date_str=date_str),
        headers=REQUEST_HEADERS,
    )
    return menu_resp.json().get("menu", {})
"api code end"

chat_session = model.start_chat(history=[])
next_message = ""
next_image = ""


def allowed_file(filename):
    """Returns if a filename is supported via its extension"""
    _, ext = os.path.splitext(filename)
    return ext.lstrip('.').lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload_file():
    """Takes in a file, checks if it is valid,
    and saves it for the next request to the API
    """
    global next_image

    if "file" not in request.files:
        return jsonify(success=False, message="No file part")

    file = request.files["file"]

    if file.filename == "":
        return jsonify(success=False, message="No selected file")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Read the file stream into a BytesIO object
        file_stream = io.BytesIO(file.read())
        file_stream.seek(0)
        next_image = Image.open(file_stream)

        return jsonify(
            success=True,
            message="File uploaded successfully and added to the conversation",
            filename=filename,
        )
    return jsonify(success=False, message="File type not allowed")


@app.route("/", methods=["GET"])
def index():
    """Renders the main homepage for the app"""
    return render_template("index.html", chat_history=chat_session.history)


@app.route("/chat", methods=["POST"])
def chat():
    """Takes in the message the user wants to send to the Gemini API, saves it"""
    global next_message
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify(success=False, message="Invalid input"), 400

    next_message = data["message"]

    if next_message.lower() == "menu":
            eatery_menu = get_location_menu("THE EATERY")
            if not eatery_menu:
                return jsonify(success=False, message="Menu not available"), 404
            menu_output = f" Give me a summarized version of the menu, organized by station:\n{eatery_menu}"
            chat_session.send_message(menu_output +"Today's menu for THE EATERY" )
            #response_text = f"Error fetching menu: {str(e)}"
            #print("Received message:", next_message)  # For debugging
            #print("Chat history:", chat_session.history)
    return jsonify(success=True)


@app.route("/stream", methods=["GET"])
def stream():
    """
    Streams the response from the serve for
    both multi-modal and plain text requests
    """
    def generate():
        global next_message
        global next_image
        assistant_response_content = ""

        if next_image != "":
            # This only works with `gemini-1.5-pro-latest`
            response = chat_session.send_message([next_message, next_image],
                                                 stream=True)
            next_image = ""
        else:
            response = chat_session.send_message(next_message, stream=True)
            next_message = ""

        for chunk in response:
            assistant_response_content += chunk.text
            yield f"data: {chunk.text}\n\n"

    return Response(stream_with_context(generate()),
                    mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(port=5100)