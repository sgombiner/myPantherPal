# myPantherPal
https://devpost.com/software/my-panther-pal
- Gemini AI interfaced with PittAPI, React, and Flask. Made in Python, HTML, and JavaScript
- Secured 2nd place in "Best Pitt Inspired Demo powered by Gemini API" at SteelHacks 2024, surpassing 25 competing teams, sponsored by Google.
# Chat Application with File Upload and Menu Fetching

This project is a web-based chat application that allows users to interact with a generative AI model. Users can send messages, upload images, and retrieve menus from dining locations on campus.

## Features

- **Real-time Chat**: Users can send messages to the AI model and receive streamed responses.
- **File Upload**: Users can upload images, which are processed and stored for conversation context.
- **Menu Fetching**: Users can request dining menus from various locations, specifically "THE EATERY" with the key word: menu.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (with AJAX for asynchronous requests)
- **Backend**: Python (Flask), PIL (Python Imaging Library), Google Gemini API
- **Dependencies**:
  - Flask
  - Pillow
  - Requests
  - Werkzeug
  - Google Generative AI SDK

### Prerequisites

- Python 3.x
- Flask
- Required Python libraries 
- Google API Key for the Gemini API

# Project Setup Guide

## 1. Create a Virtual Environment

### macOS/Linux:
```bash
python -m venv venv  
source venv/bin/activate
```

## 2. Install Required Dependencies

Run this command to install all the necessary packages:

```bash
pip install -r requirements.txt
```

## 3. Configure Environment Variables

Duplicate the example `.env` file:

```bash
cp .env.example .env
```

Open the `.env` file and add your API key.

## 4. Start the Application

Launch the app with:

```bash
flask run
```

## 5. Access the App

Open your browser and visit: [http://localhost:5000](http://localhost:5000) (ensure port 5000 not in use).

Enjoy trying out my app! 

### Demo

https://github.com/user-attachments/assets/b836e05c-8062-40fb-a54a-2a20d9530f8d




