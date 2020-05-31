from fastapi import Request
from config.settings import app, templates
from .models import Loan

## CONTROLLERS
@app.post("/loan/")
async def loan_generator(loan: Loan):
    return await loan.payment_plan()

@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,})
