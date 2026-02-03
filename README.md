# ⚗️ Chemical Equipment Parameter Visualizer

A full-stack application to visualize and analyze chemical equipment parameters from CSV data.

## 🚀 Features

- **CSV Upload**: Drag-and-drop interface for uploading equipment data.
- **Data Analysis**: Automatic calculation of flowrate, pressure, and temperature averages.
- **Visualization**: Interactive charts for equipment type distribution.
- **History**: Keeps track of the last 5 uploaded files.
- **PDF Reports**: Generate downloadable summary reports.
- **Cross-Platform**: Web (React) and Desktop (PyQt5) interfaces.

## 📋 Data Requirements

The application expects CSV files with the following columns (case-insensitive):
- **Equipment Name**
- **Type** (e.g., Pump, Server, Sensor)
- **Flowrate** (Numeric)
- **Pressure** (Numeric)
- **Temperature** (Numeric)

Example row:
```csv
Pump-01,Centrifugal Pump,150.5,25.3,45.2
```

---

## 🛠️ Project Setup

### 1. Django Backend

A robust REST API powered by Django Rest Framework and Pandas.

**Prerequisites**: Python 3.8+

```bash
# Navigate to project root
cd project

# Install dependencies (create a virtualenv recommended)
pip install -r requirements.txt

# Create database and apply migrations
python manage.py migrate

# Create a superuser for authentication
python manage.py createsuperuser

# Start the server
python manage.py runserver
```
*Server runs at http://127.0.0.1:8000*

### 2. React Frontend

Modern web interface built with Vite, React, and Chart.js.

**Prerequisites**: Node.js 16+

```bash
# Navigate to frontend directory
cd project/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
*Web App runs at http://localhost:5173*

*Note: You will be prompted to enter the superuser credentials created in the backend step.*

### 3. Desktop Application

Native GUI client built with PyQt5 and Matplotlib.

**Prerequisites**: Python 3.8+

```bash
# Navigate to desktop app directory
cd project/desktop_app

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## 🔐 Authentication

The API uses **Basic Authentication**.
- **Web App**: Prompts for credentials on first load.
- **Desktop App**: Prompts for credentials on launch.

Use the superuser account created during backend setup.

---

## 📄 API Endpoints

- `POST /api/upload/`: Upload CSV file.
- `GET /api/files/`: List recent uploads.
- `GET /api/report/<id>/`: Download PDF summary report.
