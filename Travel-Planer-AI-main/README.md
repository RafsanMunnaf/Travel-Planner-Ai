## ✈️ Travel-Planer-AI

An AI-powered multilingual travel assistant that helps users effortlessly build personalized travel itineraries through a natural language conversation. The assistant captures user preferences and generates a full trip plan — powered by real-time travel data and APIs like Booking.com. Supports both **English** and **Chinese (中文)** language modes.

---

### 🗺️ Project Overview

Travel-Planer-AI is your intelligent travel companion — combining **conversational AI**, **user-centric itinerary generation**, and **real-time travel data sources** to build complete, customized travel plans.

Inspired by platforms like **Lyila AI**, this system offers an intuitive, chat-first planning experience. The bot communicates in **English** and **Chinese**, collects trip details, and returns a structured itinerary with accommodation, activities, transport, and timelines — all tailored to user needs.

---

### 🧩 How It Works

#### 📌 Section 1: Conversational Preference Collection

- Multilingual (🇬🇧 English / 🇨🇳 中文) conversation interface.
- Gathers user details such as:
  - 🌍 Travel origin & destination  
  - 🗓️ Travel dates & duration  
  - 👥 Number of travelers  
  - 🎯 Travel type (leisure, business, solo, family, etc.)  
  - 💬 Language preference  
- Uses OpenAI to drive dynamic and friendly interaction.

#### 📌 Section 2: AI Travel Plan Generation

- AI generates a personalized itinerary:
  - ✈️ Flights & transport suggestions  
  - 🏨 Lodging options from APIs like Booking.com  
  - 🗺️ Activity recommendations based on traveler type & destination  
  - 🕒 Day-by-day schedule  
- Language toggle to view plan in **English** or **Chinese**.

---

### 🔑 Key Features

- ✅ Conversational UI with language choice (English & Chinese)
- ✅ Intelligent preference capture and summarization
- ✅ AI-generated travel plan with real-time suggestions
- ✅ Integration-ready for Booking.com, Skyscanner, TripAdvisor, etc.
- ✅ Modular codebase (ideal for web or app integration)

---

### 🛠 Tech Stack

- **Language**: Python  
- **AI**: OpenAI GPT-4  
- **Language Support**: English, Chinese (via GPT multilingual understanding)  
- **APIs**: Booking.com, Google Places, etc.  
- **Frontend**: Streamlit / (Optional: React or Flutter)  
- **Backend**: FastAPI / Flask  
- **Translation**: OpenAI GPT / DeepL API (optional)

---

### 🚀 Getting Started

#### Prerequisites

- Python 3.8+
- OpenAI API Key
- Booking.com or travel data API keys

#### Installation

    git clone https://github.com/your-username/Travel-Planer-AI.git
    cd Travel-Planer-AI
    pip install -r requirements.txt


#### Configure .env

    OPENAI_API_KEY=your-openai-key
    TRAVEL_API_KEY=your-booking-api-key
    LANGUAGE_MODE=EN|ZH


    
### 💡 Future Roadmap

- 🔄 Real-time price fetching for hotels & flights
- 📱 Mobile app integration
- 🧭 Map view of itinerary
- 🗃️ Save/share travel plans
- 🧳 Personal travel dashboard




### 📄 License

Licensed under the MIT License.
