# Polish History Data Project

This project scrapes historical event data from two Polish cities (Warsaw and Poznan), stores it in a PostgreSQL database, categorizes events with machine learning and keyword rules, and serves the data via a Flask web application.

---

## Prerequisites

- **Docker** and **Docker Compose** installed on the machine.  
  Download: https://docs.docker.com/get-docker/

- (Optional) Internet connection for the first build to download images and dependencies.

---

## Setup and Running

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo

2. Prepare Google Sheets credentials

    Place your Google Sheets API credentials file at google_sheet/credentials.json.

    Make sure this file exists before running (see .gitignore — this file is not pushed for security).

If you don’t have credentials or don’t use Google Sheets integration, this can be skipped.
3. Build and start the project with Docker Compose

docker compose up --build

This command will:

    Start a PostgreSQL 17 database with your configured user and database.

    Run the scraping and import scripts to fetch and load data into the database.

    Train the ML model (if needed).

    Launch the Flask web server exposing the timeline app on port 5000.

4. Access the web application

Open your browser and go to:

http://localhost:5000

You should see the timeline visualization of historical events.
Stopping the application

Press Ctrl+C in the terminal running Docker Compose, or run:

docker compose down
