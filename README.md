# 🌱 GreenEvents

> An eco-friendly event management platform built with Django

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.0+-green.svg)](https://www.djangoproject.com/)

## 📖 Overview

GreenEvents is a sustainable event management platform designed to help organizers plan, manage, and execute eco-friendly events. The platform promotes environmental responsibility by providing tools to track carbon footprints, minimize waste, and encourage sustainable practices throughout the event lifecycle.

## ✨ Features

- **Event Creation & Management**: Create and manage events with sustainability metrics
- **Carbon Footprint Tracking**: Monitor and reduce the environmental impact of your events
- **Sustainable Vendor Directory**: Connect with eco-conscious vendors and suppliers
- **Attendee Management**: Efficient registration and communication system
- **Green Metrics Dashboard**: Real-time analytics on sustainability metrics
- **Resource Optimization**: Smart tools for minimizing waste and resource usage
- **Community Features**: Share best practices and connect with other eco-conscious organizers

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- PostgreSQL (or SQLite for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/niketbhatt2002/GreenEvents.git
   cd GreenEvents
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and navigate to `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`

## 📁 Project Structure

```
Event-Organiser/
├── events/                 # Event management app
├── users/                  # User authentication and profiles
├── analytics/             # Sustainability metrics and reporting
├── vendors/               # Vendor management
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
├── media/                 # User-uploaded files
├── greenevents/           # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── requirements.txt
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/greenevents
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
```

## 🧪 Testing

Run the test suite with:

```bash
python manage.py test
```

For coverage report:

```bash
coverage run --source='.' manage.py test
coverage report
```

## 🌍 Sustainability Metrics

GreenEvents tracks the following environmental metrics:

- **Carbon Emissions**: Total CO2 equivalent emissions
- **Waste Reduction**: Percentage of waste diverted from landfills
- **Digital vs. Physical**: Ratio of digital materials to printed materials
- **Local Sourcing**: Percentage of locally sourced products/services
- **Renewable Energy**: Amount of renewable energy used

## 🛠️ Technology Stack

- **Backend**: Django 4.x
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: PostgreSQL / SQLite
- **Authentication**: Django Auth
- **API**: Django REST Framework (if applicable)
- **Task Queue**: Celery (if applicable)
- **Cache**: Redis (if applicable)

## 🤝 Contributing

We welcome contributions to make GreenEvents even better! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guidelines for Python code
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape GreenEvents
- Inspired by the global movement towards sustainable event management
- Built with Django and the amazing Python community

## 📞 Contact

For questions, suggestions, or collaboration opportunities:

- GitHub: [@niketbhatt2002](https://github.com/niketbhatt2002)
- Project Link: [https://github.com/niketbhatt2002/GreenEvents](https://github.com/niketbhatt2002/GreenEvents)


<div align="center">
Made with 💚 for a sustainable future
</div>
