# Billing & Invoice Management System - FastAPI

## Features
- Product management
- Inventry Stock management
- Dynamic billing with tax calculation
- Cash denomination balance calculation
- Async invoice email sending
- Customer purchase history

## How to Run
1.Create virtual environment
2.Install dependencies
  pip install -r requirements.txt
3.Run Server
  uvicorn app.main:app --reload
4.Open browser
  http://127.0.001:8000/docs

## Notes
- SQLite used for simplicity
- Email sending handled asnchronously