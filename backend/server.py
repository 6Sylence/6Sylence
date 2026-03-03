from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Stripe
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    role: str = "buyer"  # buyer or seller
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSession(BaseModel):
    session_id: str
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Category(BaseModel):
    category_id: str = Field(default_factory=lambda: f"cat_{uuid.uuid4().hex[:12]}")
    name: str
    icon: str
    color: str
    image_url: Optional[str] = None

class Product(BaseModel):
    product_id: str = Field(default_factory=lambda: f"prod_{uuid.uuid4().hex[:12]}")
    seller_id: str
    seller_name: str
    title: str
    description: str
    price: float
    original_price: Optional[float] = None
    category_id: str
    category_name: str
    images: List[str] = []  # base64 images
    stock: int = 0
    rating: float = 0.0
    review_count: int = 0
    featured: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
    title: str
    description: str
    price: float
    original_price: Optional[float] = None
    category_id: str
    images: List[str] = []
    stock: int = 0

class Review(BaseModel):
    review_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:12]}")
    product_id: str
    user_id: str
    user_name: str
    user_picture: Optional[str] = None
    rating: int  # 1-5
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReviewCreate(BaseModel):
    product_id: str
    rating: int
    comment: str

class CartItem(BaseModel):
    product_id: str
    quantity: int

class Cart(BaseModel):
    cart_id: str = Field(default_factory=lambda: f"cart_{uuid.uuid4().hex[:12]}")
    user_id: str
    items: List[CartItem] = []
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Order(BaseModel):
    order_id: str = Field(default_factory=lambda: f"ord_{uuid.uuid4().hex[:12]}")
    user_id: str
    items: List[dict] = []  # product details at time of order
    total: float
    status: str = "pending"  # pending, paid, shipped, delivered, cancelled
    shipping_address: Optional[dict] = None
    payment_session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaymentTransaction(BaseModel):
    transaction_id: str = Field(default_factory=lambda: f"txn_{uuid.uuid4().hex[:12]}")
    session_id: str
    user_id: str
    order_id: str
    amount: float
    currency: str = "eur"
    status: str = "initiated"  # initiated, paid, failed, expired
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== AUTH HELPERS ====================

async def get_current_user(request: Request) -> Optional[User]:
    """Get current user from session token"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        return None
    
    session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session:
        return None
    
    # Check expiry
    expires_at = session.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    
    user_doc = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    if not user_doc:
        return None
    
    return User(**user_doc)

async def require_auth(request: Request) -> User:
    """Require authentication"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

async def require_seller(request: Request) -> User:
    """Require seller role"""
    user = await require_auth(request)
    if user.role != "seller":
        raise HTTPException(status_code=403, detail="Seller access required")
    return user

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/session")
async def create_session(request: Request, response: Response):
    """Exchange session_id for session_token"""
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    # Call Emergent Auth to get user data
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        user_data = resp.json()
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data["email"]}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        # Update user data
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": user_data["name"], "picture": user_data.get("picture")}}
        )
    else:
        # Create new user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        new_user = {
            "user_id": user_id,
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "role": "buyer",
            "created_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(new_user)
    
    # Create session
    session_token = user_data.get("session_token", f"sess_{uuid.uuid4().hex}")
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.user_sessions.insert_one({
        "session_id": f"sess_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc)
    })
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return user_doc

@api_router.get("/auth/me")
async def get_me(request: Request):
    """Get current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user.model_dump()

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out"}

@api_router.post("/auth/become-seller")
async def become_seller(request: Request):
    """Upgrade user to seller"""
    user = await require_auth(request)
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {"role": "seller"}}
    )
    return {"message": "You are now a seller", "role": "seller"}

# ==================== CATEGORIES ====================

DEFAULT_CATEGORIES = [
    {"category_id": "cat_electronica", "name": "Electrónica", "icon": "laptop-outline", "color": "#3498db"},
    {"category_id": "cat_moda", "name": "Moda", "icon": "shirt-outline", "color": "#e74c3c"},
    {"category_id": "cat_hogar", "name": "Hogar y Cocina", "icon": "home-outline", "color": "#2ecc71"},
    {"category_id": "cat_deportes", "name": "Deportes", "icon": "basketball-outline", "color": "#f39c12"},
    {"category_id": "cat_belleza", "name": "Belleza", "icon": "sparkles-outline", "color": "#9b59b6"},
    {"category_id": "cat_juguetes", "name": "Juguetes", "icon": "game-controller-outline", "color": "#e91e63"},
    {"category_id": "cat_libros", "name": "Libros", "icon": "book-outline", "color": "#795548"},
    {"category_id": "cat_alimentacion", "name": "Alimentación", "icon": "nutrition-outline", "color": "#4caf50"},
    {"category_id": "cat_mascotas", "name": "Mascotas", "icon": "paw-outline", "color": "#ff9800"},
    {"category_id": "cat_jardin", "name": "Jardín", "icon": "leaf-outline", "color": "#8bc34a"},
    {"category_id": "cat_bebes", "name": "Bebés", "icon": "happy-outline", "color": "#ffb6c1"},
    {"category_id": "cat_informatica", "name": "Informática", "icon": "desktop-outline", "color": "#607d8b"},
    {"category_id": "cat_coche", "name": "Coche y Moto", "icon": "car-outline", "color": "#263238"},
    {"category_id": "cat_bricolaje", "name": "Bricolaje", "icon": "hammer-outline", "color": "#ff5722"},
]

@api_router.get("/categories")
async def get_categories():
    """Get all categories"""
    categories = await db.categories.find({}, {"_id": 0}).to_list(100)
    if not categories:
        # Seed default categories
        for cat in DEFAULT_CATEGORIES:
            await db.categories.insert_one(cat.copy())
        categories = await db.categories.find({}, {"_id": 0}).to_list(100)
    return categories

# ==================== PRODUCTS ====================

@api_router.get("/products")
async def get_products(
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    seller_id: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """Get products with filters"""
    query = {}
    if category_id:
        query["category_id"] = category_id
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    if featured:
        query["featured"] = True
    if seller_id:
        query["seller_id"] = seller_id
    
    products = await db.products.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.products.count_documents(query)
    
    return {"products": products, "total": total}

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get single product"""
    product = await db.products.find_one({"product_id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@api_router.post("/products")
async def create_product(product: ProductCreate, request: Request):
    """Create a new product (seller only)"""
    user = await require_seller(request)
    
    # Get category name
    category = await db.categories.find_one({"category_id": product.category_id}, {"_id": 0})
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    product_data = Product(
        seller_id=user.user_id,
        seller_name=user.name,
        title=product.title,
        description=product.description,
        price=product.price,
        original_price=product.original_price,
        category_id=product.category_id,
        category_name=category["name"],
        images=product.images,
        stock=product.stock
    )
    
    await db.products.insert_one(product_data.model_dump())
    return product_data.model_dump()

@api_router.put("/products/{product_id}")
async def update_product(product_id: str, updates: dict, request: Request):
    """Update a product (owner only)"""
    user = await require_seller(request)
    
    product = await db.products.find_one({"product_id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["seller_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Not your product")
    
    # Only allow certain fields to be updated
    allowed_fields = ["title", "description", "price", "original_price", "images", "stock", "featured"]
    update_data = {k: v for k, v in updates.items() if k in allowed_fields}
    
    await db.products.update_one({"product_id": product_id}, {"$set": update_data})
    return {"message": "Product updated"}

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, request: Request):
    """Delete a product (owner only)"""
    user = await require_seller(request)
    
    product = await db.products.find_one({"product_id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["seller_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Not your product")
    
    await db.products.delete_one({"product_id": product_id})
    return {"message": "Product deleted"}

# ==================== REVIEWS ====================

@api_router.get("/products/{product_id}/reviews")
async def get_reviews(product_id: str):
    """Get reviews for a product"""
    reviews = await db.reviews.find({"product_id": product_id}, {"_id": 0}).to_list(100)
    return reviews

@api_router.post("/reviews")
async def create_review(review: ReviewCreate, request: Request):
    """Create a review"""
    user = await require_auth(request)
    
    # Check if product exists
    product = await db.products.find_one({"product_id": review.product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user already reviewed
    existing = await db.reviews.find_one({
        "product_id": review.product_id,
        "user_id": user.user_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this product")
    
    review_data = Review(
        product_id=review.product_id,
        user_id=user.user_id,
        user_name=user.name,
        user_picture=user.picture,
        rating=min(5, max(1, review.rating)),
        comment=review.comment
    )
    
    await db.reviews.insert_one(review_data.model_dump())
    
    # Update product rating
    all_reviews = await db.reviews.find({"product_id": review.product_id}, {"_id": 0}).to_list(1000)
    avg_rating = sum(r["rating"] for r in all_reviews) / len(all_reviews)
    await db.products.update_one(
        {"product_id": review.product_id},
        {"$set": {"rating": round(avg_rating, 1), "review_count": len(all_reviews)}}
    )
    
    return review_data.model_dump()

# ==================== CART ====================

@api_router.get("/cart")
async def get_cart(request: Request):
    """Get user's cart with product details"""
    user = await require_auth(request)
    
    cart = await db.carts.find_one({"user_id": user.user_id}, {"_id": 0})
    if not cart:
        return {"items": [], "total": 0}
    
    # Get product details for each item
    items_with_details = []
    total = 0
    
    for item in cart.get("items", []):
        product = await db.products.find_one({"product_id": item["product_id"]}, {"_id": 0})
        if product:
            item_total = product["price"] * item["quantity"]
            items_with_details.append({
                "product_id": product["product_id"],
                "title": product["title"],
                "price": product["price"],
                "image": product["images"][0] if product.get("images") else None,
                "quantity": item["quantity"],
                "item_total": item_total,
                "stock": product["stock"]
            })
            total += item_total
    
    return {"items": items_with_details, "total": round(total, 2)}

@api_router.post("/cart/add")
async def add_to_cart(request: Request):
    """Add item to cart"""
    user = await require_auth(request)
    body = await request.json()
    product_id = body.get("product_id")
    quantity = body.get("quantity", 1)
    
    # Check product exists and has stock
    product = await db.products.find_one({"product_id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["stock"] < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")
    
    cart = await db.carts.find_one({"user_id": user.user_id})
    
    if cart:
        # Check if product already in cart
        item_found = False
        for item in cart.get("items", []):
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                item_found = True
                break
        
        if not item_found:
            cart["items"].append({"product_id": product_id, "quantity": quantity})
        
        await db.carts.update_one(
            {"user_id": user.user_id},
            {"$set": {"items": cart["items"], "updated_at": datetime.now(timezone.utc)}}
        )
    else:
        # Create new cart
        new_cart = {
            "cart_id": f"cart_{uuid.uuid4().hex[:12]}",
            "user_id": user.user_id,
            "items": [{"product_id": product_id, "quantity": quantity}],
            "updated_at": datetime.now(timezone.utc)
        }
        await db.carts.insert_one(new_cart)
    
    return {"message": "Added to cart"}

@api_router.post("/cart/update")
async def update_cart_item(request: Request):
    """Update cart item quantity"""
    user = await require_auth(request)
    body = await request.json()
    product_id = body.get("product_id")
    quantity = body.get("quantity", 0)
    
    cart = await db.carts.find_one({"user_id": user.user_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    if quantity <= 0:
        # Remove item
        cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
    else:
        # Update quantity
        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] = quantity
                break
    
    await db.carts.update_one(
        {"user_id": user.user_id},
        {"$set": {"items": cart["items"], "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": "Cart updated"}

@api_router.delete("/cart/clear")
async def clear_cart(request: Request):
    """Clear user's cart"""
    user = await require_auth(request)
    await db.carts.delete_one({"user_id": user.user_id})
    return {"message": "Cart cleared"}

# ==================== ORDERS & PAYMENT ====================

@api_router.post("/checkout/create-session")
async def create_checkout_session(request: Request):
    """Create Stripe checkout session"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    user = await require_auth(request)
    body = await request.json()
    origin_url = body.get("origin_url")
    
    if not origin_url:
        raise HTTPException(status_code=400, detail="origin_url required")
    
    # Get cart
    cart_data = await db.carts.find_one({"user_id": user.user_id})
    if not cart_data or not cart_data.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total from server side
    total = 0.0
    order_items = []
    
    for item in cart_data["items"]:
        product = await db.products.find_one({"product_id": item["product_id"]}, {"_id": 0})
        if product:
            item_total = product["price"] * item["quantity"]
            total += item_total
            order_items.append({
                "product_id": product["product_id"],
                "title": product["title"],
                "price": product["price"],
                "quantity": item["quantity"],
                "seller_id": product["seller_id"]
            })
    
    if total <= 0:
        raise HTTPException(status_code=400, detail="Invalid cart total")
    
    # Create order
    order = Order(
        user_id=user.user_id,
        items=order_items,
        total=round(total, 2),
        status="pending"
    )
    await db.orders.insert_one(order.model_dump())
    
    # Create Stripe checkout session
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/cart"
    
    checkout_request = CheckoutSessionRequest(
        amount=round(total, 2),
        currency="eur",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "order_id": order.order_id,
            "user_id": user.user_id
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create payment transaction
    transaction = PaymentTransaction(
        session_id=session.session_id,
        user_id=user.user_id,
        order_id=order.order_id,
        amount=round(total, 2),
        currency="eur",
        status="initiated"
    )
    await db.payment_transactions.insert_one(transaction.model_dump())
    
    # Update order with session ID
    await db.orders.update_one(
        {"order_id": order.order_id},
        {"$set": {"payment_session_id": session.session_id}}
    )
    
    return {"checkout_url": session.url, "session_id": session.session_id, "order_id": order.order_id}

@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, request: Request):
    """Get checkout status and update order"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    user = await require_auth(request)
    
    # Get transaction
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction["user_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Not your transaction")
    
    # Don't reprocess if already paid
    if transaction["status"] == "paid":
        return {"status": "paid", "order_id": transaction["order_id"]}
    
    # Check Stripe status
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    checkout_status = await stripe_checkout.get_checkout_status(session_id)
    
    if checkout_status.payment_status == "paid":
        # Update transaction
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"status": "paid"}}
        )
        
        # Update order
        await db.orders.update_one(
            {"order_id": transaction["order_id"]},
            {"$set": {"status": "paid"}}
        )
        
        # Clear cart
        await db.carts.delete_one({"user_id": user.user_id})
        
        # Update product stock
        order = await db.orders.find_one({"order_id": transaction["order_id"]}, {"_id": 0})
        if order:
            for item in order.get("items", []):
                await db.products.update_one(
                    {"product_id": item["product_id"]},
                    {"$inc": {"stock": -item["quantity"]}}
                )
        
        return {"status": "paid", "order_id": transaction["order_id"]}
    elif checkout_status.status == "expired":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"status": "expired"}}
        )
        await db.orders.update_one(
            {"order_id": transaction["order_id"]},
            {"$set": {"status": "cancelled"}}
        )
        return {"status": "expired", "order_id": transaction["order_id"]}
    
    return {"status": "pending", "order_id": transaction["order_id"]}

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        logger.info(f"Webhook received: {webhook_response.event_type}")
        return {"received": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"received": True}

# ==================== ORDERS ====================

@api_router.get("/orders")
async def get_orders(request: Request):
    """Get user's orders"""
    user = await require_auth(request)
    orders = await db.orders.find({"user_id": user.user_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return orders

@api_router.get("/orders/{order_id}")
async def get_order(order_id: str, request: Request):
    """Get single order"""
    user = await require_auth(request)
    order = await db.orders.find_one({"order_id": order_id, "user_id": user.user_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ==================== SELLER DASHBOARD ====================

@api_router.get("/seller/products")
async def get_seller_products(request: Request):
    """Get seller's products"""
    user = await require_seller(request)
    products = await db.products.find({"seller_id": user.user_id}, {"_id": 0}).to_list(1000)
    return products

@api_router.get("/seller/orders")
async def get_seller_orders(request: Request):
    """Get orders containing seller's products"""
    user = await require_seller(request)
    
    # Find orders with seller's products
    orders = await db.orders.find(
        {"items.seller_id": user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return orders

@api_router.get("/seller/stats")
async def get_seller_stats(request: Request):
    """Get seller statistics"""
    user = await require_seller(request)
    
    products = await db.products.find({"seller_id": user.user_id}, {"_id": 0}).to_list(1000)
    total_products = len(products)
    total_stock = sum(p.get("stock", 0) for p in products)
    avg_rating = sum(p.get("rating", 0) for p in products) / total_products if total_products > 0 else 0
    
    # Count orders
    orders = await db.orders.find({"items.seller_id": user.user_id, "status": "paid"}, {"_id": 0}).to_list(1000)
    total_orders = len(orders)
    total_revenue = sum(
        sum(item["price"] * item["quantity"] for item in order["items"] if item.get("seller_id") == user.user_id)
        for order in orders
    )
    
    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "avg_rating": round(avg_rating, 1),
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2)
    }

# ==================== SEED DATA ====================

@api_router.post("/seed")
async def seed_data():
    """Seed sample products"""
    # Clear existing products
    await db.products.delete_many({})
    
    # Create sample seller
    seller_id = "seller_demo123"
    existing_seller = await db.users.find_one({"user_id": seller_id})
    if not existing_seller:
        await db.users.insert_one({
            "user_id": seller_id,
            "email": "demo@marketplace.com",
            "name": "Tienda Oficial",
            "role": "seller",
            "created_at": datetime.now(timezone.utc)
        })
    
    sample_products = [
        {"title": "iPhone 15 Pro Max", "description": "El último smartphone de Apple con chip A17 Pro y cámara de 48MP", "price": 1299.99, "original_price": 1499.99, "category_id": "cat_electronica", "category_name": "Electrónica", "stock": 50, "featured": True, "rating": 4.8, "review_count": 234},
        {"title": "Samsung Galaxy S24 Ultra", "description": "Smartphone Android con S Pen integrado y cámara de 200MP", "price": 1199.99, "original_price": 1399.99, "category_id": "cat_electronica", "category_name": "Electrónica", "stock": 35, "featured": True, "rating": 4.7, "review_count": 189},
        {"title": "MacBook Pro 14\"", "description": "Portátil profesional con chip M3 Pro y pantalla Liquid Retina XDR", "price": 2199.99, "original_price": 2499.99, "category_id": "cat_informatica", "category_name": "Informática", "stock": 20, "featured": True, "rating": 4.9, "review_count": 156},
        {"title": "Camiseta Nike Dri-FIT", "description": "Camiseta deportiva con tecnología de absorción de humedad", "price": 34.99, "original_price": 49.99, "category_id": "cat_deportes", "category_name": "Deportes", "stock": 200, "rating": 4.5, "review_count": 89},
        {"title": "Zapatillas Adidas Ultraboost", "description": "Zapatillas de running con tecnología Boost para máximo confort", "price": 159.99, "original_price": 189.99, "category_id": "cat_deportes", "category_name": "Deportes", "stock": 75, "featured": True, "rating": 4.6, "review_count": 312},
        {"title": "Vestido Elegante Zara", "description": "Vestido de fiesta con diseño exclusivo y tela premium", "price": 79.99, "original_price": 99.99, "category_id": "cat_moda", "category_name": "Moda", "stock": 45, "rating": 4.4, "review_count": 67},
        {"title": "Robot Aspirador Roomba i7+", "description": "Aspirador inteligente con vaciado automático y mapeo avanzado", "price": 699.99, "original_price": 899.99, "category_id": "cat_hogar", "category_name": "Hogar y Cocina", "stock": 30, "featured": True, "rating": 4.7, "review_count": 445},
        {"title": "Cafetera Nespresso Vertuo", "description": "Cafetera de cápsulas con tecnología Centrifusion", "price": 149.99, "original_price": 199.99, "category_id": "cat_hogar", "category_name": "Hogar y Cocina", "stock": 60, "rating": 4.5, "review_count": 234},
        {"title": "LEGO Star Wars Millennium Falcon", "description": "Set de construcción con 7541 piezas para coleccionistas", "price": 799.99, "original_price": 849.99, "category_id": "cat_juguetes", "category_name": "Juguetes", "stock": 15, "rating": 4.9, "review_count": 89},
        {"title": "PlayStation 5 Digital", "description": "Consola de última generación con SSD ultra rápido", "price": 449.99, "original_price": 499.99, "category_id": "cat_juguetes", "category_name": "Juguetes", "stock": 25, "featured": True, "rating": 4.8, "review_count": 567},
        {"title": "Perfume Chanel No. 5", "description": "Fragancia icónica con notas florales y elegantes", "price": 129.99, "original_price": 159.99, "category_id": "cat_belleza", "category_name": "Belleza", "stock": 80, "rating": 4.7, "review_count": 234},
        {"title": "Set de Maquillaje MAC", "description": "Kit completo de maquillaje profesional con 24 colores", "price": 89.99, "original_price": 119.99, "category_id": "cat_belleza", "category_name": "Belleza", "stock": 55, "rating": 4.6, "review_count": 178},
        {"title": "Libro: El Poder del Ahora", "description": "Best-seller de Eckhart Tolle sobre mindfulness", "price": 14.99, "original_price": 19.99, "category_id": "cat_libros", "category_name": "Libros", "stock": 150, "rating": 4.8, "review_count": 1234},
        {"title": "Pack Café Premium", "description": "Selección de 3 variedades de café de origen", "price": 24.99, "original_price": 34.99, "category_id": "cat_alimentacion", "category_name": "Alimentación", "stock": 100, "rating": 4.5, "review_count": 89},
        {"title": "Cama para Perro Premium", "description": "Cama ortopédica con memoria de forma para mascotas", "price": 69.99, "original_price": 89.99, "category_id": "cat_mascotas", "category_name": "Mascotas", "stock": 40, "rating": 4.6, "review_count": 156},
        {"title": "Set de Herramientas Bosch", "description": "Kit profesional con 108 piezas para bricolaje", "price": 199.99, "original_price": 249.99, "category_id": "cat_bricolaje", "category_name": "Bricolaje", "stock": 35, "rating": 4.7, "review_count": 234},
    ]
    
    for product in sample_products:
        product["product_id"] = f"prod_{uuid.uuid4().hex[:12]}"
        product["seller_id"] = seller_id
        product["seller_name"] = "Tienda Oficial"
        product["images"] = []
        product["created_at"] = datetime.now(timezone.utc)
        await db.products.insert_one(product)
    
    return {"message": f"Seeded {len(sample_products)} products"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
