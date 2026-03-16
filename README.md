# Capstone

This project sets up a web app with Python Flask backend, Vue.js frontend, Tailwind CSS, and Docker containerization.

## Setup

1. Ensure Docker and Docker Compose are installed.

2. Clone the repository.

3. Run `docker-compose up --build -d` to start the services.

4. The backend will be available at http://localhost:5000

5. The frontend that doesn't live update will be available at http://localhost:8080

6. The development frontend is at http://localhost:5173

7. The database is PostgreSQL, accessible internally.

## Database Setup

Initialize and seed the database with sample data:

### Initialize Database
Creates all tables from the models:
```bash
docker-compose run --rm web python init_db.py
```

### Seed Database
Populates tables with realistic sample data using Faker:
```bash
docker-compose run --rm web python seed_db.py
```

### Reset Database
To reset and repopulate the database:
```bash
docker-compose run --rm web python init_db.py
docker-compose run --rm web python seed_db.py
```

## Architecture

### Backend MVC Structure
- **Models** (`backend/models/`): Database models using SQLAlchemy
  - User, Equipment, Review, Message, Rental, Event, Request, RentalHasEquipment
- **Services** (`backend/services/`): Business logic layer
  - UserService, EquipmentService, ReviewService, MessageService, RentalService, EventService, RequestService
- **Routes** (`backend/routes/`): REST API endpoints using Flask blueprints
  - Available at `/api/{resource}` endpoints

### API Endpoints
- `/api/users/` - User CRUD operations
- `/api/equipment/` - Equipment management
- `/api/reviews/` - Reviews for equipment and users
- `/api/messages/` - User messaging
- `/api/rentals/` - Rental transactions
- `/api/events/` - Event management
- `/api/requests/` - Equipment requests

### Frontend Services
- `src/services/api.js` - Generic HTTP client for API calls
- `src/services/userService.js` - User API service layer

## Development

For frontend development with hot reload and Tailwind watching:

**Using Docker dev server:**
```bash
cd /root/capstone/Capstone
docker-compose up frontend-dev
```
Frontend will be available at http://localhost:5173 with HMR enabled.

## Project Structure

```
Capstone/
├── backend/
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Business logic layer
│   ├── routes/          # REST API routes
│   ├── app.py           # Flask application factory
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   ├── requirements.txt  # Python dependencies
│   ├── init_db.py       # Database initialization script
│   ├── seed_db.py       # Database seeding script
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── views/       # Page components
│   │   ├── services/    # API service layer
│   │   ├── router.js    # Vue Router configuration
│   │   └── App.vue      # Root component
│   ├── package.json     # Node dependencies
│   ├── vite.config.js   # Vite configuration
│   ├── tailwind.config.js # Tailwind configuration
│   ├── postcss.config.js  # PostCSS configuration
│   └── Dockerfile
└── docker-compose.yml   # Docker Compose configuration
```

## Backend

- Located in `backend/`
- Uses Flask with SQLAlchemy ORM
- Dependencies in `requirements.txt`
- MVC architecture with service layer

## Frontend

- Located in `frontend/`
- Uses Vue.js 3 with Vue Router and Tailwind CSS
- Vite build tool for fast development
- Dependencies in `package.json`

## Docker

- `docker-compose.yml` - Orchestrates all services (db, backend, frontend, frontend-dev)
- `backend/Dockerfile` - Python Flask application
- `frontend/Dockerfile` - Node.js build + Nginx serving

## Stack

- **Backend**: Python 3.9, Flask 2.3.3, SQLAlchemy 3.0.5, PostgreSQL 13
- **Frontend**: Vue.js 3.4.0, Vite 5.0.0, Tailwind CSS 3.4.0
- **Database**: PostgreSQL 13
- **Containerization**: Docker & Docker Compose
- **Testing Data**: Faker 18.13.0