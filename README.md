# Polish History Data Project

A comprehensive data pipeline that collects, processes, and visualizes historical events from Polish cities.


## Features

- **Web Scraping**: Collects historical event data from Warsaw and Poznań sources
- **Data Processing**: Cleans and normalizes event data
- **Machine Learning**: Categorizes events using ML models and keyword rules
- **Database Storage**: PostgreSQL backend with persistent storage
- **Web Visualization**: Interactive timeline interface via Flask

## Prerequisites

- Docker and Docker Compose installed
- (Optional) Google Sheets API credentials if using that integration

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/polish-history-data.git
   cd polish-history-data
   ```

2. **Set up credentials** (if using Google Sheets)
   - Place your `credentials.json` in `google_sheet/` directory

3. **Build and run**
   ```bash
   docker compose up --build
   ```

4. **Access the application**
   - Open http://localhost:5000 in your browser
   - Or click the link in terminal if this one won't work 

## Troubleshooting

- View application logs:
  ```bash
  docker compose logs app
  ```
  
- View database logs:
  ```bash
  docker compose logs db
  ```

- Common issues:
  - Ensure port 5000 is available
  - Verify Google Sheets credentials path if used
  - Check Docker has sufficient resources
