# RamBook Exchange

**For Rams. By Rams.**

## Project Overview

RamBook Exchange is a web application designed for students at Winston-Salem State University (WSSU). The platform allows students to buy, sell, and trade textbooks with other students. It also includes a contactless textbook return system to make the return process more convenient.

This is an unofficial student software engineering project and is not an official WSSU bookstore service.

## Project Features

- Student registration and login
- Browse and search available textbooks
- List textbooks for sale or trade
- View textbook details
- Send purchase or trade requests
- Manage textbook listings through a student dashboard
- Schedule textbook returns
- Generate return confirmation codes
- Track textbook return status
- Bookstore administration interface for managing returns

Some features are still being integrated and tested.

## Technologies Used

**Frontend**
- HTML
- CSS
- JavaScript

**Backend**
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Gunicorn

**Database**
- SQLite for local development
- PostgreSQL for cloud deployment

**Development and Deployment Tools**
- Visual Studio Code
- Git and GitHub
- Docker
- Render

## Project Structure

```text
RamBook-Exchange/
│
├── app.py
├── requirements.txt
├── README.md
├── Dockerfile
├── .dockerignore
│
├── templates/
│   ├── index.html
│   ├── marketplace.html
│   ├── add_book.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── book_details.html
│   ├── return_books.html
│   ├── return_status.html
│   └── bookstore_admin.html
│
└── static/
    └── style.css
```

## How to Run the Project Locally

**1. Clone the repository**

```bash
git clone https://github.com/nyasiaA/RamBook-Exchange.git
```

**2. Open the project folder**

```bash
cd RamBook-Exchange
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Start the Flask application**

```bash
python app.py
```

**5. Open the website**

Visit:

http://127.0.0.1:5000

The application uses SQLite by default when no PostgreSQL database URL is configured.

## Database Configuration

The application uses Flask-SQLAlchemy to manage database models and database operations.

The database includes the following models:

- Student
- Textbook
- ExchangeRequest
- BookReturn

PostgreSQL is configured through the `DATABASE_URL` environment variable for cloud deployment. The application uses the psycopg2 PostgreSQL driver.

The application can also use SQLite for local development.

## Docker Setup

Docker is used to package the application and its dependencies into a container.

**Build the Docker image:**

```bash
docker build -t rambook-exchange .
```

**Run the Docker container:**

```bash
docker run -d -p 10000:10000 --name rambook-test rambook-exchange
```

**Open the Docker application:**

http://localhost:10000

The Docker image was successfully built, and the application was tested running inside a container.

## Cloud Deployment

The application is deployed using Render.

Deployment configuration includes:

- GitHub repository integration
- Gunicorn application server
- PostgreSQL database connection
- Environment variable configuration
- Automatic deployment from the main branch

The deployed application can be accessed through its Render service URL.

## Team Responsibilities

**Person 1 – Frontend Development**
- Designed the website layout and navigation
- Created HTML pages
- Styled the website using CSS
- Worked on frontend and backend integration

**Person 2 – Backend Development**
- Developed Flask routes
- Implemented student registration and login
- Created textbook listing and exchange functionality
- Developed return scheduling and tracking logic
- Created database models

**Person 3 – Database and Deployment**
- Configured PostgreSQL database connectivity
- Configured the psycopg2 database driver
- Created Docker configuration files
- Built and tested the Docker image
- Tested the application inside a Docker container
- Configured and verified cloud deployment through Render
- Updated project documentation

## Testing and Verification

The project has undergone application and deployment testing, including:

- Flask application startup
- Homepage and marketplace page loading
- Automated application tests
- PostgreSQL deployment configuration
- Docker image build
- Docker container startup
- Homepage and marketplace testing inside Docker

Additional integration and security testing may still be required.

## Current Project Status

The Flask application is deployed through Render, PostgreSQL connectivity is configured, and Docker containerization has been completed and tested.

Frontend and backend integration and additional application testing are ongoing.

## GitHub Repository

https://github.com/nyasiaA/RamBook-Exchange

## Disclaimer

RamBook Exchange is an academic software engineering project. It is not affiliated with or officially endorsed by Winston-Salem State University.
