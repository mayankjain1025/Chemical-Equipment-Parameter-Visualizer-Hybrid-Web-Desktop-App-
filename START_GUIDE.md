# 🚀 How to Run the Chemical Equipment Visualizer

Follow these steps to start both the backend and frontend servers.

## 1. Start the Backend (Django)
The backend handles the database and data processing.

1.  Open a terminal (Command Prompt or PowerShell).
2.  Navigate to the project root:
    ```powershell
    cd c:\Users\HP\Downloads\project\project
    ```
3.  (Optional) Activate your virtual environment if you use one.
4.  Run the Django server:
    ```powershell
    python manage.py runserver
    ```
    ✅ You should see: `Starting development server at http://127.0.0.1:8000/`

## 2. Start the Frontend (React)
The frontend provides the user interface.

1.  Open a **new, separate** terminal window.
2.  Navigate to the frontend directory:
    ```powershell
    cd c:\Users\HP\Downloads\project\project\frontend
    ```
3.  Install dependencies (only needed the first time):
    ```powershell
    npm install
    ```
4.  Start the Vite development server:
    ```powershell
    npm run dev
    ```
    ✅ You should see: `Local: http://localhost:5173/`

## 3. Login
1.  Open your web browser and go to: **[http://localhost:5173](http://localhost:5173)**
2.  Log in with the test credentials:
    *   **Username**: `admin`
    *   **Password**: `admin123`

## 4. Start the Desktop App (PyQt5)
The desktop application provides a native interface for parsing and visualizing data.

1.  Open a **new, separate** terminal window.
2.  Navigate to the desktop app directory:
    ```powershell
    cd c:\Users\HP\Downloads\project\project\desktop_app
    ```
3.  Install dependencies (if not already installed):
    ```powershell
    pip install -r requirements.txt
    ```
4.  Run the application:
    ```powershell
    python main.py
    ```
5.  When prompted for credentials, use:
    *   **Username**: `admin`
    *   **Password**: `admin123`
