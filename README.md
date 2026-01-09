# AZNU

## 🛠 How to use

1. Clone this repository

```bash
cd project_root
```

2. Create and activate virtual environment

```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Download necessary libraries

```bash
pip install fastapi uvicorn pika redis
```

4. Create database, message broker and Compliance Service

```bash
docker-compose up --build -d
```

5. Run Gateway, Logistics Service, Result Handler in separate terminals:

- terminal 1:

```bash
.\venv\Scripts\activate
cd gateway
uvicorn main:app --reload --port 8000
```

- terminal 2:

```bash
.\venv\Scripts\activate
cd logistics
python main.py
```

- terminal 3:

```bash
.\venv\Scripts\activate
cd logistics
python result_handler.py
```

6. Open **frontend/index.html** file in a browser, fill out the form and send a request.
