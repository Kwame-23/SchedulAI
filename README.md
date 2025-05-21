

# SchedulAi

**SchedulAi** is a hybrid algorithmic and AI-powered web application for academic timetabling and resource allocation. Designed to alleviate the administrative burden on university registries, it automatically generates conflict-free semester schedules that satisfy both hard constraints (e.g., no room or lecturer overlaps) and soft constraints (e.g., preferred teaching times).

## 🚀 Features

- AI-powered timetable generation using Greedy and Genetic Algorithms
- Real-time schedule editing with drag-and-drop functionality
- Conflict detection and resolution with suggestions
- Dynamic analytics dashboard (room utilization, lecturer workload, anomaly detection)
- Export to Excel/CSV for integration with platforms like MyCamu
- Multi-role access: Registry, Department Heads, Lecturers

## 🏗 Architecture

SchedulAi follows a **microservices architecture**:
- **Frontend**: Flask + Jinja2 + Bootstrap + Chart.js
- **Backend**: Flask + Flask-SocketIO
- **Database**: MySQL
- **Scheduler Engine**: Greedy Heuristic & Genetic Algorithm via PyGAD
- **Deployment**: Dockerized on AWS EC2 (https://github.com/Malottey1/schedulaiapp.git)

## 📦 Installation

*  1. Clone the repo:
   ```bash
   git clone https://github.com/kwame23/schedulai.git
   cd schedulai


* 2. Set up virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

* 3. Configure `.env` with DB credentials and Flask settings.

* 4. Initialize MySQL database using provided schema in `/db`.

* 5. Run the app:

   ```bash
   flask run
   ```

## 📊 Usage

* Access the dashboard at `http://http://13.51.156.245`
* Navigate through data input → scheduling → validation → analytics
* Use the drag-and-drop matrix to manually adjust sessions
* Export the final timetable to CSV

## 🧠 Algorithms

* **Greedy Heuristic**: Prioritizes high-enrollment sessions and large rooms
* **Genetic Algorithm**: Evolves candidate timetables using crossover/mutation
* **Conflict Checker**: Detects overlaps in time/space
* **Feasibility Engine**: Offers suggestions and validates user modifications

## 🛠 Technologies

* **Frontend**: HTML, CSS (Bootstrap), JavaScript (jQuery, Chart.js)
* **Backend**: Python (Flask, Flask-SocketIO, PyGAD)
* **Database**: MySQL with SQLAlchemy (for analytics)
* **Analytics**: Pandas, NumPy, Seaborn, Matplotlib, Scikit-learn (KMeans)

## 👨‍👩‍👧‍👦 Contributors

* Malcolm Clottey
* Kwame Frimpong Afriyie-Buabeng

Supervised by **Dr. Eric Ocran**
Ashesi University · May 2025

## 📄 License

This project is for academic use under Ashesi University's Applied Project guidelines.

---


