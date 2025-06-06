from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# --- Extract country or keyword from user message ---
def extract_country(message):
    # Basic keyword mapping (expand this later or use NLP)
    countries = ["Egypt", "Brazil", "India", "Colombia", "Morocco"]
    for country in countries:
        if country.lower() in message.lower():
            return country
    return None

# --- Call AIESEC API ---
def get_opportunity(country):
    url = f"https://gis-api.aiesec.org/v2/opportunities.json?programmes=1&status=open&locations[]={country}"
    res = requests.get(url)
    data = res.json().get('data', [])

    if not data:
        return f"Sorry, I couldn't find any volunteering opportunities in {country} right now."
    
    # Get first result
    opp = data[0]
    title = opp.get('title', 'Untitled')
    location = opp['location']['country']
    link = f"https://aiesec.org/opportunity/{opp['id']}"
    return f"🌍 *{title}* in {location}\nApply here: {link}"

# --- WhatsApp webhook ---
@app.route("/bot", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    country = extract_country(incoming_msg)

    if country:
        response = get_opportunity(country)
    else:
        response = ("👋 Hi! I'm your AIESEC assistant.\n"
                    "Ask me about volunteer opportunities like:\n"
                    "➡️ 'I want to volunteer in Brazil'\n"
                    "➡️ 'Any internships in Egypt?'")

    msg.body(response)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=10000)
