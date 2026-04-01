## This is a fork of Meal Planner with AI project.

This repository is a serverless refactor of my original Meal Planner web application project. While the original relied on Docker Compose for orchestration, this version is optimized for AWS Lambda using the AWS Lambda Web Adapter (LWA) and Amazon RDS.

- Backend: Django running in AWS Lambda (via Docker container images).
- Web Adapter: Allows the Django app to run on Lambda without code changes.
- Database: Amazon RDS (PostgreSQL).
- Deployment: Managed via AWS SAM.
- Frontend:
