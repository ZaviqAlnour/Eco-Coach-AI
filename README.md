# Eco-Coach AI
#### Description:

Eco-Coach AI is an AI-powered web application designed to help users minimize household waste and track their environmental impact in a simple and actionable way. The project combines AI technology with an intuitive web interface to provide personalized guidance for disposing of waste and promoting sustainable habits.

## Key Features:
- **User Authentication**: Secure registration and login system with session management.
- **Waste Logging**: Users can input items they wish to dispose of, along with quantities.
- **AI-Powered Recommendations**:
  - Proper disposal instructions for different types of waste: food, recyclables, hazardous, electronics, and more.
  - Personalized tips for reducing future waste.
  - Category classification for all logged items.
- **Environmental Impact Tracking**: Tracks CO₂ saved for each logged item and presents cumulative savings.
- **Visual Dashboard**: Displays statistics including weekly/monthly logs, category pie charts, and trends using Chart.js.
- **History and Search**: Full log of all items, searchable and filterable by category.

## AI Integration:
The application integrates the Qwen3-4B-Instruct-2507 AI model via the Bytez API. It generates structured responses that include disposal instructions, tips, and environmental impact metrics. In case the API is unavailable, a mock response system simulates realistic AI behavior to allow testing and demonstrations without an active API key.

## Tech Stack:
- **Backend**: Python 3.10+, Flask framework
- **Database**: SQLAlchemy with SQLite (upgradeable to PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Charting**: Chart.js
- **AI Integration**: Bytez API (Qwen3-4B-Instruct-2507)

## Project Goals:
The main goal of Eco-Coach AI is to provide actionable, real-time guidance for users to reduce waste effectively. By combining AI recommendations with visual analytics, users can make informed choices, measure their environmental impact, and adopt sustainable behaviors.

This project also demonstrates practical implementation of:
- Web development concepts (Flask routing, templates, session management)
- Database management (CRUD operations, ORM with SQLAlchemy)
- AI API integration and structured data handling
- Data visualization and responsive UI design

## Intended Audience:
Eco-conscious individuals, households, or anyone interested in reducing environmental footprint through smarter waste management.

## Conclusion:
Eco-Coach AI empowers users to take small but meaningful actions toward sustainability. By logging items, following AI recommendations, and tracking progress, users can lower waste generation, save energy, and contribute to a greener planet. The project showcases the intersection of AI, web development, and environmental responsibility, creating a practical, educational, and impactful solution.

**Made with 💚 to encourage sustainable living and waste reduction.**
