# AutoDine - AI-Powered Voice-Controlled Restaurant Ordering System

## 🍔 Overview

AutoDine is an innovative AI-powered restaurant ordering system that combines voice recognition, natural language processing, and real-time inventory management to create a seamless dining experience. The system features "Eldia," an intelligent voice assistant that can process customer orders, check ingredient availability, and manage the entire ordering workflow through natural conversation.

## ✨ Key Features

- **Voice-Controlled Ordering**: Real-time speech-to-text and text-to-speech capabilities
- **AI Assistant (Eldia)**: Intelligent conversation handling with OpenAI integration
- **Real-time Inventory Management**: Dynamic ingredient tracking and feasibility checking
- **Interactive Dashboard**: Live order updates and system status monitoring
- **Menu Customization**: Support for ingredient modifications and special requests
- **Multi-Modal Interface**: Web dashboard and voice interaction capabilities

## 🏗️ Architecture

The project consists of several interconnected components:

### Core Components

1. **Django Backend** (`smart_food_frenzy/`)
   - RESTful API endpoints for order processing
   - Database models for menu items, ingredients, and orders
   - Real-time inventory management
   - Server-Sent Events (SSE) for live updates

2. **Voice Assistant System** (`llm.py`, `playground/eldia.py`)
   - OpenAI GPT integration for natural language processing
   - Real-time speech recognition and synthesis
   - Function calling for order validation and placement

3. **Frontend Interface** (`smart_food_frenzy/static/`)
   - Interactive menu display
   - Real-time order dashboard
   - Responsive web design

## 🛠️ Technology Stack

### Backend
- **Django 5.1.7** - Web framework
- **SQLite** - Database
- **OpenAI API** - Natural language processing
- **RealtimeSTT** - Speech-to-text conversion
- **RealtimeTTS** - Text-to-speech synthesis

### Frontend
- **HTML5/CSS3** - User interface
- **JavaScript** - Real-time updates and interactivity
- **Server-Sent Events** - Live data streaming

### AI & Voice Processing
- **OpenAI GPT** - Conversation handling
- **Coqui TTS** - Text-to-speech engine
- **Faster Whisper** - Speech recognition
- **Azure Cognitive Services** - Speech processing

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Audio input/output devices
- Windows 10/11 (for some voice features)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AutoDine
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create an `api_keys.json` file in the root directory:
```json
{
    "openai_key": "your-openai-api-key-here"
}
```

### 4. Initialize Django Database
```bash
cd smart_food_frenzy
python manage.py migrate
python manage.py createsuperuser
```

### 5. Load Sample Data (Optional)
```bash
python manage.py loaddata sample_data.json
```

## 🎯 Usage

### Starting the System

1. **Start Django Server**
```bash
cd smart_food_frenzy
python manage.py runserver
```

2. **Launch Voice Assistant**
```bash
python llm.py
```

3. **Access Web Interface**
   - Open `http://localhost:8000` in your browser
   - Navigate to the dashboard for real-time order monitoring

### Voice Ordering Process

1. **Activate Eldia**: The voice assistant will greet you and ask for your order
2. **Place Order**: Speak naturally about what you'd like to order
3. **Customize**: Request modifications like "extra cheese" or "no onions"
4. **Confirmation**: Eldia will confirm your order and check ingredient availability
5. **Completion**: Once confirmed, your order is placed and processed

### Web Dashboard Features

- **Real-time Order Updates**: Live streaming of order status
- **Inventory Monitoring**: Current ingredient levels
- **Menu Display**: Interactive menu with customization options
- **Order History**: Track completed orders

## 📁 Project Structure

```
AutoDine/
├── smart_food_frenzy/          # Django backend
│   ├── restaurant/             # Main app
│   │   ├── models.py          # Database models
│   │   ├── views.py           # API endpoints
│   │   ├── templates/         # HTML templates
│   │   └── static/            # CSS, JS, images
│   ├── manage.py
│   └── settings.py
├── playground/                 # Development and testing
│   ├── eldia.py              # Voice assistant implementation
│   └── test_*.py             # Various test files
├── llm.py                     # Main LLM integration
├── utils.py                   # Utility functions
├── prompts.json              # AI system prompts
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔧 API Endpoints

### Core Endpoints

- `POST /check_feasible_items/` - Check ingredient availability
- `POST /order_items/` - Place new orders
- `GET /sse/` - Server-sent events for real-time updates
- `GET /menu/` - Display menu items
- `GET /ingredients_list` - Show current inventory

### LLM Control Endpoints

- `GET /llm_thinking/<str:set_thinking>` - Control thinking indicator
- `GET /llm_recording/<str:set_recording>` - Control recording indicator

## 🗄️ Database Models

### Core Models

- **MenuItem**: Available food items with descriptions and prices
- **Ingredient**: Individual ingredients with stock levels and costs
- **Order**: Customer orders with timestamps and completion status
- **OrderItem**: Individual items in orders with modifications
- **Inventory**: Real-time ingredient tracking

## 🎨 Customization

### Adding New Menu Items

1. Add the item to the database through Django admin
2. Update the system prompts in `prompts.json`
3. Add corresponding images to `static/images/`

### Modifying Voice Assistant

- Edit `prompts.json` for conversation behavior
- Modify `llm.py` for function calling logic
- Update `playground/eldia.py` for additional features

## 🧪 Testing

### Voice Assistant Testing
```bash
cd playground
python test_sr.py      # Speech recognition testing
python test_stt.py     # Speech-to-text testing
python test_request.py # API request testing
```

### Web Interface Testing
- Access `http://localhost:8000/menu/` for menu display
- Use `http://localhost:8000/ingredients_list` for inventory view

## 🔍 Troubleshooting

### Common Issues

1. **Audio Not Working**
   - Check microphone permissions
   - Verify audio drivers are installed
   - Test with `playground/test_sr.py`

2. **OpenAI API Errors**
   - Verify API key in `api_keys.json`
   - Check internet connection
   - Ensure sufficient API credits

3. **Django Server Issues**
   - Check if port 8000 is available
   - Verify database migrations
   - Check Django logs for errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT integration
- Coqui AI for TTS capabilities
- Django community for the web framework
- Contributors and testers

## 📞 Support

For support and questions:
Contact me at arielfayol1@gmail.com or fayol.ateufackzeudom@valpo.edu.

---

**AutoDine** - Revolutionizing restaurant ordering with AI-powered voice interaction! 🎤🍕
