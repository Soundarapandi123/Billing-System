from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from . import models
from .seed import seed_products
from .email_utils import send_invoice_email
import math


Base.metadata.create_all(bind=engine)
seed_products()
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/", response_class=HTMLResponse)
def billing_page(request: Request):
    return templates.TemplateResponse(
        "billing.html",
        {"request": request}
    )
@app.post("/generate-bill", response_class=HTMLResponse)
async def generate_bill(
    request: Request,
    background_tasks: BackgroundTasks,
    customer_email: str = Form(...),
    paid_amount: float = Form(...),
    d500: int = Form(0),
    d200: int = Form(0),
    d100: int = Form(0),
    d50: int = Form(0),
    d20: int = Form(0),
    d10: int = Form(0),
    d5: int = Form(0),
    d2: int = Form(0),
    d1: int = Form(0),
    db: Session = Depends(get_db)
):
    form = await request.form()
    product_ids = form.getlist("product_id")
    quantities = form.getlist("quantity")
    total_without_tax = 0.0
    total_tax = 0.0
    processed_items = []
    for pid, qty in zip(product_ids, quantities):
        if not pid or not qty:
            continue
        product = db.query(models.Product).filter(
            models.Product.product_id == pid.strip()
        ).first()
        if not product:
            continue
        qty = int(qty)
        if qty <= 0 or qty > product.available_stock:
            continue
        base_price = product.unit_price * qty
        tax_amount = base_price * (product.tax_percentage / 100)
        total_price = base_price + tax_amount
        total_without_tax += base_price
        total_tax += tax_amount
        processed_items.append({
            "product": product,
            "quantity": qty,
            "total_price": total_price
        })
        product.available_stock -= qty
    net_price = total_without_tax + total_tax
    rounded_price = math.floor(net_price)
    balance = paid_amount - rounded_price
    if balance < 0:
        balance = 0
    purchase = models.Purchase(
        customer_email=customer_email,
        total_without_tax=total_without_tax,
        total_tax=total_tax,
        net_price=net_price,
        rounded_price=rounded_price,
        paid_amount=paid_amount,
        balance_amount=balance
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    for item in processed_items:
        product = item["product"]
        purchase_item = models.PurchaseItem(
            purchase_id=purchase.id,
            product_id=product.product_id,
            product_name=product.name,
            quantity=item["quantity"],
            unit_price=product.unit_price,
            tax_percentage=product.tax_percentage,
            total_price=item["total_price"]
        )
        db.add(purchase_item)
    db.commit()
    db.refresh(purchase)
    balance_breakdown = {}
    remaining = int(balance)
    notes = [500, 200, 100, 50, 20, 10, 5, 2, 1]
    for note in notes:
        count = remaining // note
        balance_breakdown[note] = count
        remaining -= count * note   
    background_tasks.add_task(
        send_invoice_email,
        customer_email,
        purchase,
        balance_breakdown
    )
    return templates.TemplateResponse(
        "invoice.html",
        {
            "request": request,
            "purchase": purchase,
            "balance_breakdown": balance_breakdown
        }
    )

@app.get("/purchases", response_class=HTMLResponse)
def view_purchases(
    request: Request,
    email: str,
    db: Session = Depends(get_db)
):

    purchases = db.query(models.Purchase).filter(
        models.Purchase.customer_email == email
    ).all()

    return templates.TemplateResponse(
        "purchases.html",
        {
            "request": request,
            "purchases": purchases,
            "email": email
        }
    )

@app.get("/purchase/{purchase_id}", response_class=HTMLResponse)
def purchase_detail(
    request: Request,
    purchase_id: int,
    db: Session = Depends(get_db)
):

    purchase = db.query(models.Purchase).filter(
        models.Purchase.id == purchase_id
    ).first()

    return templates.TemplateResponse(
        "purchase_detail.html",
        {
            "request": request,
            "purchase": purchase
        }
    )