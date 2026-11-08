import uvicorn
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from database import Base, SessionLocal, engine, get_db
from models import Category, Customer, Product

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    if db.query(Product).count() == 0:
        cat = Category(name="Деревья", slug="trees", description="Разные деревья")
        db.add(cat)
        db.commit()
        db.add_all([
           Product(category_id=cat.id, name="Яблоня Недзвецкого", slug="yablonya",
                    description="Декоративный вид", price=11200, stock=10,
                    height_cm=200, age_years=3,
                    image_url="/static/image/apple.jpg", is_active=True),

Product(category_id=cat.id, name="Клён сахарный", slug="klen-saharnyy",
                    description="Крупное тенистое дерево с яркой осенней окраской", price=18500, stock=7,
                    height_cm=250, age_years=4,
                    image_url="/static/image/maple_sugar.jpg", is_active=True),

Product(category_id=cat.id, name="Магнолия Суланжа", slug="magnoliya-sulanzha",
                    description="Раннецветущее дерево с крупными розовыми цветами", price=22400, stock=5,
                    height_cm=150, age_years=3,
                    image_url="/static/image/magnolia_soulangeana.jpg", is_active=True),

Product(category_id=cat.id, name="Сакура (вишня мелкопильчатая)", slug="sakura",
                    description="Декоративная вишня с обильным весенним цветением", price=19800, stock=8,
                    height_cm=180, age_years=3,
                    image_url="/static/image/sakura.jpg", is_active=True),

Product(category_id=cat.id, name="Красный дуб", slug="dub-krasnyy",
                    description="Быстрорастущий дуб с ярко-красной осенней листвой", price=15600, stock=12,
                    height_cm=220, age_years=4,
                    image_url="/static/image/oak_red.jpg", is_active=True),

Product(category_id=cat.id, name="Туя западная", slug="tuya-zapadnaya",
                    description="Вечнозелёное хвойное дерево для живой изгороди", price=8900, stock=25,
                    height_cm=120, age_years=3,
                    image_url="/static/image/thuja.jpg", is_active=True),

Product(category_id=cat.id, name="Багрянник канадский (Церцис)", slug="bagryannik-kanadskiy",
                    description="Дерево с розово-пурпурным цветением до распускания листьев", price=17200, stock=6,
                    height_cm=160, age_years=3,
                    image_url="/static/image/cercis_canadensis.jpg", is_active=True),

Product(category_id=cat.id, name="Гинкго билоба", slug="ginkgo-biloba",
                    description="Реликтовое дерево с уникальной веерной листвой", price=24500, stock=4,
                    height_cm=200, age_years=4,
                    image_url="/static/image/ginkgo.jpg", is_active=True),

Product(category_id=cat.id, name="Ликвидамбар смолоносный", slug="likvidambar",
                    description="Ароматное дерево с эффектной осенней окраской", price=16800, stock=9,
                    height_cm=210, age_years=3,
                    image_url="/static/image/liquidambar.jpg", is_active=True),

Product(category_id=cat.id, name="Падуб остролистный", slug="padub-ostrolistnyy",
                    description="Вечнозелёное дерево с красными ягодами зимой", price=13400, stock=11,
                    height_cm=140, age_years=3,
                    image_url="/static/image/ilex.jpg", is_active=True),

Product(category_id=cat.id, name="Тюльпанное дерево", slug="tyulpannoe-derevo",
                    description="Крупнолистное дерево с цветами, похожими на тюльпаны", price=21200, stock=5,
                    height_cm=230, age_years=4,
                    image_url="/static/image/maple.jpg", is_active=True),

Product(category_id=cat.id, name="Берёза повислая Пендула", slug="bereza-pendula",
                    description="Плакучая форма берёзы с ажурной кроной", price=14200, stock=10,
                    height_cm=200, age_years=3,
                    image_url="/static/image/birch.jpg", is_active=True),

Product(category_id=cat.id, name="Ель колючая (Голубая)", slug="el-golubaya",
                    description="Хвойное дерево с серебристо-голубой хвоей", price=18900, stock=6,
                    height_cm=160, age_years=4,
                    image_url="/static/image/spruce.jpg", is_active=True),
        ])
        db.commit()


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html",
                                      context={"is_auth": "user_email" in request.cookies})

@app.get("/catalog")
def catalog(request: Request, category: str | None = None,
            db: Session = Depends(get_db)):
    q = db.query(Product).filter(Product.is_active == True)  
    current = None
    if category:
        current = db.query(Category).filter(Category.slug == category).first()
        if current:
            q = q.filter(Product.category_id == current.id)
    return templates.TemplateResponse(
        request=request, name="catalog.html",
        context={"products": q.all(), "categories": db.query(Category).all(),
                 "current_category": current},
    )

@app.get("/product/{product_id}")
def product_page(product_id: int, request: Request, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        return RedirectResponse("/catalog", status_code=303)
    similar = (db.query(Product)
               .filter(Product.id != product.id, Product.is_active == True) 
               .filter(Product.category_id == product.category_id)
               .limit(4).all())
    return templates.TemplateResponse(
        request=request, name="product.html",
        context={"product": product, "similar": similar,
                 "category": db.get(Category, product.category_id)},
    )

def _cart(request: Request) -> list[int]:
    return [int(x) for x in request.cookies.get("cart", "").split(",") if x]

def _set_cart(response, ids: list[int]):
    response.set_cookie("cart", ",".join(map(str, ids)), path="/")
    return response

@app.get("/add-to-cart/{product_id}")
def add_to_cart(product_id: int, request: Request):
    ids = _cart(request) + [product_id]
    referer = request.headers.get("referer", "/cart")
    
    return _set_cart(RedirectResponse(referer, status_code=303), ids)

@app.get("/cart")
def cart_page(request: Request, db: Session = Depends(get_db)):
    ids = _cart(request)
    products = db.query(Product).filter(Product.id.in_(ids)).all() if ids else []
    return templates.TemplateResponse(
        request=request, name="corz.html",
        context={"products": products,
                 "total_price": sum(p.price for p in products)},
    )

@app.get("/clear-cart")
def clear_cart():
    return _set_cart(RedirectResponse("/cart", status_code=303), [])

def _login_response(email: str) -> RedirectResponse:
    resp = RedirectResponse("/account", status_code=303)
    resp.set_cookie("user_email", email, path="/")
    return resp

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.post("/register")
def register_user(request: Request,
                  full_name: str = Form(...), phone: str = Form(...),
                  email: str = Form(...), password: str = Form(...),
                  db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.email == email).first():
        return templates.TemplateResponse(
            request=request, name="register.html",
            context={"error": "Email занят"})
    db.add(Customer(full_name=full_name, phone=phone, email=email, password=password))
    db.commit()
    return _login_response(email)

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def login_user(request: Request, email: str = Form(...), password: str = Form(...),
               db: Session = Depends(get_db)):
    user = db.query(Customer).filter(Customer.email == email).first()
    if not user or user.password != password:
        return templates.TemplateResponse(
            request=request, name="login.html",
            context={"error": "Неверный логин или пароль"})
    return _login_response(email)

@app.get("/logout")
def logout_user():
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("user_email", path="/")
    return resp

@app.get("/account")
def account_page(request: Request, db: Session = Depends(get_db)):
    email = request.cookies.get("user_email")
    if not email:
        return RedirectResponse("/login", status_code=303)
    user = db.query(Customer).filter(Customer.email == email).first()
    return templates.TemplateResponse(request=request, name="account.html",
                                      context={"user": user})

@app.get("/search")
def search_page(
    request: Request, 
    q: str = "", 
    category: str = "", 
    min_price: str = "",
    max_price: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_active == True)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    current_category = None
    if category:
        current_category = db.query(Category).filter(Category.name == category).first()
        if current_category:
            query = query.filter(Product.category_id == current_category.id)
    if min_price and min_price.isdigit():
        query = query.filter(Product.price >= int(min_price))
    if max_price and max_price.isdigit():
        query = query.filter(Product.price <= int(max_price))
    products = query.all()
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        request=request, name="find.html",
        context={
            "products": products,
            "categories": categories,
            "q": q,
            "current_category": category,
            "min_price": min_price,
            "max_price": max_price
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)