import os

import uvicorn
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from database import Base, SessionLocal, engine, get_db
from models import Category, Customer, Product

Base.metadata.create_all(bind=engine)
db = SessionLocal()
if db.query(Product).count() == 0:
    category = Category(name="Деревья", slug="trees", description="Разные деревья")
    db.add(category)
    db.commit()

    products = [
        Product(category_id=category.id,
                name="Яблоня Недзвецкого", 
                slug="yablonya", 
                description="Декоративный вид", 
                price=11200, stock=10, height_cm=200, 
                age_years=3, 
                image_url="/static/image/apple.jpg", 
                is_active=True),
        Product(category_id=category.id, 
                name="Ель обыкновенная", 
                slug="el", 
                description="Классический лесной вид", 
                price=21800, 
                stock=15, 
                height_cm=150, 
                age_years=4, 
                image_url="/static/image/spruce.jpg", 
                is_active=True),
        Product(category_id=category.id, 
                name="Берёза повислая", 
                slug="bereza", 
                description="Светолюбивое дерево", 
                price=8900,
                stock=8, 
                height_cm=300, 
                age_years=5, 
                image_url="/static/image/birch.jpg", 
                is_active=True),
        Product(category_id=category.id, 
                name="Клён Глобозум", 
                slug="klen", 
                description="Крупное дерево", 
                price=12100, 
                stock=5, 
                height_cm=300, 
                age_years=5, 
                image_url="/static/image/maple.jpg", 
                is_active=True),
    ]
    db.add_all(products)
    db.commit()
db.close()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

cart_list = []

REDIRECT_PAGE = """
<html>
    <head><meta http-equiv="refresh" content="0; url=/"></head>
    <body>Переход...</body>
</html>
"""

@app.get("/")
def home_page(request: Request): 
    user_email = request.cookies.get("user_email")
    return templates.TemplateResponse(request=request, name="index.html", context={"is_auth": user_email is not None})

@app.get("/catalog")
def catalog_page(request: Request, db: Session = Depends(get_db)):
    all_products = db.query(Product).all()
    return templates.TemplateResponse(request=request, name="catalog.html", context={"products": all_products})

@app.get("/add-to-cart/{product_id}")
def add_to_cart(product_id: int):
    cart_list.append(product_id)
    return RedirectResponse("/cart", status_code=303)

@app.get("/cart")
def cart_page(request: Request, db: Session = Depends(get_db)):
    products_in_cart = []
    total_price = 0
    
    for pid in cart_list:
        product = db.query(Product).filter(Product.id == pid).first()
        if product:
            products_in_cart.append(product)
            total_price = total_price + product.price
            
    return templates.TemplateResponse(
        request=request, 
        name="corz.html", 
        context={"products": products_in_cart, "total_price": total_price}
    )

@app.get("/clear-cart")
def clear_cart():
    cart_list.clear() 
    return RedirectResponse("/cart", status_code=303)

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.post("/register")
def register_user(
    full_name: str = Form(...), phone: str = Form(...), email: str = Form(...), password: str = Form(...),
    db: Session = Depends(get_db), request: Request = None
):
    if db.query(Customer).filter(Customer.email == email).first():
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Email занят"})
    
    db.add(Customer(full_name=full_name, phone=phone, email=email, password=password))
    db.commit()
    
    response = HTMLResponse(REDIRECT_PAGE)
    response.set_cookie(key="user_email", value=email, path="/")
    return response

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def login_user(
    email: str = Form(...), password: str = Form(...),
    db: Session = Depends(get_db), request: Request = None
):
    user = db.query(Customer).filter(Customer.email == email).first()
    if not user or user.password != password:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Неверный логин или пароль"})
    
    response = HTMLResponse(REDIRECT_PAGE)
    response.set_cookie(key="user_email", value=email, path="/")
    return response

@app.get("/logout")
def logout_user():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("user_email", path="/")
    return response

@app.get("/account")
def account_page(request: Request, db: Session = Depends(get_db)):
    user_email = request.cookies.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    user = db.query(Customer).filter(Customer.email == user_email).first()
    return templates.TemplateResponse(request=request, name="account.html", context={"user": user})

@app.get("/search")
def search_page(request: Request):
    return templates.TemplateResponse(request=request, name="find.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)