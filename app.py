from flask import Flask, render_template, url_for, request, jsonify, session
import os
import logging
import json
import ipinfo
from geopy import Nominatim
from datetime import datetime
import random
import string

# Function to generate a secret key for Flask session
def secret_key_generation(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

# Flask application setup
app = Flask(__name__)
# Set a secret key for the session
app.secret_key = secret_key_generation(32)

# Access token for IPinfo API
access_token = '48989a6b17352a'
handler = None
ip = None
details = None
location_info = None
geolocator = Nominatim(user_agent="YourApp", timeout=10)
location = None

# Load image paths from JSON files
json_path = os.path.join('static', 'paths.json')
with open(json_path, 'r') as json_file:
    image_paths = json.load(json_file)

json_path_pets = os.path.join('static', 'pets-information.json')
with open(json_path_pets, 'r') as json_file_pets:
    pets_information = json.load(json_file_pets)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Default image path
DEFAULT_IMAGE_PATH = 'static/assets/default/default.svg'

# Function to be executed before each request
@app.before_request
def before_request():
    try:
        global handler, ip, details, location_info
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails()
        ip = details.ip

        # Check if location information is already in the session
        if 'location' not in session:
            location_info = details.loc
            location = geolocator.reverse(location_info)
            # Store location information in the session
            session['location'] = {
                'coordinates': location_info,
                'address': location.address,
                'timestamp': datetime.now()
            }
            logging.info(f"Session started - IP: {ip}, Coordinates: {location_info}, User-Agent: {request.headers.get('User-Agent')}")
            logging.info(f"Approximate Address: {location.address}")
        else:
            # Retrieve location information from the session
            location_data = session['location']
            location_info = location_data['coordinates']
            location_address = location_data['address']
            logging.info(f"Session started - IP: {ip}, Coordinates: {location_info}, User-Agent: {request.headers.get('User-Agent')}")
            logging.info(f"Approximate Address (Cached): {location_address}")

    except Exception as e:
        logging.error(f"Error getting location information: {str(e)}")
        logging.info(f"Session started - IP: {ip}, User-Agent: {request.headers.get('User-Agent')}")

# Function to be executed after each request
@app.teardown_request
def teardown_request(exception=None):
    logging.info(f"Session ended - IP: {ip}, User-Agent: {request.headers.get('User-Agent')}")

# Route for the homepage
@app.route('/')
def index():
    try:
        image_rows = []
        image_folder = os.path.join('static', 'assets')
        # Get a list of image filenames
        image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg'))]
        # Split the list into rows of four
        image_rows = [image_files[i:i + 4] for i in range(0, len(image_files), 4)]

        return render_template('index.html', image_rows=image_rows)

    except Exception as e:
        logging.exception("An error occurred: %s", str(e))
        return render_template('error.html')

# Route for searching images
@app.route('/search')
def search():
    try:
        search_query = request.args.get('search_query', '').lower()
        # Filter image_paths based on the search query
        filtered_results = [entry for entry in image_paths if search_query in entry['name'].lower()]

        return jsonify(filtered_results)

    except Exception as e:
        logging.exception("An error occurred during search: %s", str(e))
        return jsonify(error=str(e))

# Route for displaying animal details
@app.route('/animal/<animal_name>')
def animal_details(animal_name):
    try:
        # Retrieve information for the selected animal
        selected_animal = next((pet for pet in pets_information if pet['Name'].lower() == animal_name.lower()), None)

        if selected_animal:
            # Construct the path based on the retrieved animal's name
            image_filename = f"{animal_name.lower()}.svg"
            image_path = url_for('static', filename=f'assets/{image_filename}')
            # Add the constructed path to the selected_animal dictionary
            selected_animal['path_large'] = image_path
            logging.info(f"Animal details retrieved for: {animal_name}")
            
            return render_template('animal_details.html', animal=selected_animal)
        else:
            # Log when the animal is not found
            logging.warning(f"Animal details not found for: {animal_name}")
            return render_template('animal_not_found.html', animal_name=animal_name)

    except Exception as e:
        # Log any unexpected exceptions
        logging.exception(f"Error in animal_details route for: {animal_name}, Error: {str(e)}")
        return render_template('error.html')  

# Run the Flask application if executed as the main script
if __name__ == '__main__':
    app.run(debug=True)