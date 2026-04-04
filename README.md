## This is a fork of Meal Planner with AI project.

A full-stack serverless web application that allows users to search for recipes based on ingredients.

## Tech Stack
* **Frontend:** React, JavaScript, Vite (Deployed via AWS Amplify)  https://github.com/kacper32332/Meal-Planner-frontend
* **Backend:** Django, Django REST Framework, PostgreSQL
* **Infrastructure:** AWS Lambda (Docker/Web Adapter), API Gateway, Secrets Manager
* **CI/CD:** GitHub Actions & AWS SAM

## Architecture Overview
This application uses a Serverless containerized architecture. The React frontend communicates with an AWS API Gateway, which routes requests to a Django Docker container running inside AWS Lambda. The backend connects to an AWS RDS PostgreSQL database.

## Running Locally (Development)
You can run the entire stack locally using Docker Compose.

**1. Clone this repository and frontend repository and have them placed in the same parent directory**
\`\`\`bash
git clone https://github.com/kacper32332/Meal-Planner-with-AI.git
git clone https://github.com/kacper32332/Meal-Planner-frontend.git
\`\`\`

**2. Set up your environment variables**
Create a `.env` file in the `Meal-Planner-with-AI/` directory:
\`\`\`env
DJANGO_SECRET_KEY=local-dev-secret
DATABASE_URL=postgres://postgres:postgres@db:5432/postgres
\`\`\`

**3. Boot up the application**
\`\`\`bash
docker compose up --build
\`\`\`
* Frontend runs on `http://localhost:5173`
* Backend API runs on `http://localhost:8000`