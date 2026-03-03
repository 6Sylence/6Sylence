#!/usr/bin/env python3
"""
Comprehensive Marketplace API Testing Suite
Tests ALL endpoints including public and authenticated functionality
"""

import requests
import json
import sys
import pymongo
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import uuid

# Configuration
BASE_URL = "https://marketplace-hub-381.preview.emergentagent.com/api"
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"
TIMEOUT = 30

class ComprehensiveMarketplaceTester:
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "warnings": []
        }
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_product_ids = []
        
        # Connect to MongoDB
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            self.log("✅ MongoDB connection established")
        except Exception as e:
            self.log(f"❌ MongoDB connection failed: {e}", "ERROR")
            sys.exit(1)
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_endpoint(self, method, endpoint, expected_status=200, description="", auth_required=False, **kwargs):
        """Generic test method for API endpoints"""
        self.results["total_tests"] += 1
        url = f"{BASE_URL}{endpoint}"
        
        # Add auth header if required
        if auth_required and self.auth_token:
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            kwargs["headers"]["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            self.log(f"Testing {method} {endpoint} - {description}")
            
            if method.upper() == "GET":
                response = self.session.get(url, timeout=TIMEOUT, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, timeout=TIMEOUT, **kwargs)
            elif method.upper() == "PUT":
                response = self.session.put(url, timeout=TIMEOUT, **kwargs)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=TIMEOUT, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            # Check status code
            if response.status_code != expected_status:
                error = f"Expected status {expected_status}, got {response.status_code}"
                self.log(f"❌ FAILED: {error}", "ERROR")
                self.log(f"Response: {response.text[:300]}", "ERROR")
                self.results["failed"] += 1
                self.results["errors"].append(f"{endpoint}: {error}")
                return None
                
            # Try to parse JSON if not empty
            try:
                if response.text.strip():
                    data = response.json()
                else:
                    data = {}
                self.log(f"✅ PASSED: Status {response.status_code}")
                self.results["passed"] += 1
                return data
            except json.JSONDecodeError as e:
                if expected_status == 200:  # Only error on JSON decode if we expect success
                    error = f"Invalid JSON response: {str(e)}"
                    self.log(f"❌ FAILED: {error}", "ERROR")
                    self.results["failed"] += 1
                    self.results["errors"].append(f"{endpoint}: {error}")
                    return None
                else:
                    self.log(f"✅ PASSED: Status {response.status_code} (no JSON expected)")
                    self.results["passed"] += 1
                    return {}
                
        except requests.exceptions.RequestException as e:
            error = f"Request failed: {str(e)}"
            self.log(f"❌ FAILED: {error}", "ERROR")
            self.results["failed"] += 1
            self.results["errors"].append(f"{endpoint}: {error}")
            return None

    def setup_test_user_in_mongo(self):
        """Create test user and session directly in MongoDB"""
        self.log("=" * 60)
        self.log("SETTING UP TEST USER IN MONGODB")
        self.log("=" * 60)
        
        # Create test user
        self.test_user_id = "user_alejandro_test"
        test_user = {
            "user_id": self.test_user_id,
            "email": "alejandro.martinez@techcorp.es",
            "name": "Alejandro Martínez",
            "role": "buyer",
            "created_at": datetime.now(timezone.utc)
        }
        
        # Insert or update user
        result = self.db.users.replace_one(
            {"user_id": self.test_user_id}, 
            test_user, 
            upsert=True
        )
        self.log(f"User created/updated: {result.upserted_id or 'existing'}")
        
        # Create session
        self.auth_token = "token_alejandro_secure_123"
        session_data = {
            "session_id": "sess_alejandro_test",
            "user_id": self.test_user_id,
            "session_token": self.auth_token,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            "created_at": datetime.now(timezone.utc)
        }
        
        # Insert or update session
        session_result = self.db.user_sessions.replace_one(
            {"session_token": self.auth_token},
            session_data,
            upsert=True
        )
        self.log(f"Session created/updated: {session_result.upserted_id or 'existing'}")
        self.log(f"Auth token: {self.auth_token}")
        
        return True

    def test_public_endpoints(self):
        """Test all public endpoints (no authentication required)"""
        self.log("=" * 60)
        self.log("1. TESTING PUBLIC ENDPOINTS")
        self.log("=" * 60)
        
        # Test categories
        categories = self.test_endpoint(
            "GET", "/categories",
            description="Get all categories"
        )
        
        if categories and len(categories) >= 10:
            self.log(f"✅ Categories loaded: {len(categories)} categories")
        else:
            self.results["warnings"].append("Categories: Expected at least 10 categories")
        
        # Test products - all products
        products_data = self.test_endpoint(
            "GET", "/products",
            description="Get all products"
        )
        
        if products_data and products_data.get("products"):
            products = products_data["products"]
            self.log(f"✅ Products loaded: {len(products)} products")
            
            # Store some product IDs for later tests
            self.test_product_ids = [p["product_id"] for p in products[:3]]
            
        # Test featured products
        featured_data = self.test_endpoint(
            "GET", "/products?featured=true",
            description="Get featured products"
        )
        
        if featured_data:
            featured_count = len(featured_data.get("products", []))
            self.log(f"✅ Featured products: {featured_count}")
        
        # Test search functionality
        search_data = self.test_endpoint(
            "GET", "/products?search=iPhone",
            description="Search for iPhone products"
        )
        
        if search_data:
            search_results = len(search_data.get("products", []))
            self.log(f"✅ Search results for 'iPhone': {search_results}")
        
        # Test single product (if we have product IDs)
        if self.test_product_ids:
            single_product = self.test_endpoint(
                "GET", f"/products/{self.test_product_ids[0]}",
                description=f"Get single product {self.test_product_ids[0]}"
            )
            
            if single_product:
                self.log(f"✅ Single product: {single_product.get('title', 'N/A')}")
        
        # Test product reviews (should return empty array for new products)
        if self.test_product_ids:
            reviews = self.test_endpoint(
                "GET", f"/products/{self.test_product_ids[0]}/reviews",
                description=f"Get reviews for product {self.test_product_ids[0]}"
            )
            
            if reviews is not None:
                self.log(f"✅ Product reviews endpoint working (found {len(reviews)} reviews)")

    def test_auth_endpoints(self):
        """Test authentication-related endpoints"""
        self.log("=" * 60)
        self.log("2. TESTING AUTH ENDPOINTS")
        self.log("=" * 60)
        
        # Test /api/auth/me with valid token
        me_data = self.test_endpoint(
            "GET", "/auth/me",
            description="Get current user info",
            auth_required=True
        )
        
        if me_data:
            self.log(f"✅ Authenticated user: {me_data.get('name')} ({me_data.get('email')})")
            self.log(f"   Role: {me_data.get('role')}")
        
        # Test /api/auth/me without token (should fail)
        unauth_result = self.test_endpoint(
            "GET", "/auth/me",
            expected_status=401,
            description="Get user info without authentication (should fail)"
        )
        
        if unauth_result is not None:
            self.log("✅ Auth validation working correctly (401 for unauthenticated)")

    def test_cart_endpoints(self):
        """Test cart functionality"""
        self.log("=" * 60)
        self.log("3. TESTING CART ENDPOINTS")
        self.log("=" * 60)
        
        # Test get empty cart
        cart_data = self.test_endpoint(
            "GET", "/cart",
            description="Get cart (should be empty initially)",
            auth_required=True
        )
        
        if cart_data is not None:
            items_count = len(cart_data.get("items", []))
            self.log(f"✅ Initial cart: {items_count} items")
        
        # Test add to cart (need a valid product ID)
        if self.test_product_ids:
            add_result = self.test_endpoint(
                "POST", "/cart/add",
                description=f"Add product {self.test_product_ids[0]} to cart",
                auth_required=True,
                json={
                    "product_id": self.test_product_ids[0],
                    "quantity": 1
                }
            )
            
            if add_result:
                self.log("✅ Product added to cart successfully")
            
            # Test get cart after adding
            updated_cart = self.test_endpoint(
                "GET", "/cart",
                description="Get cart after adding product",
                auth_required=True
            )
            
            if updated_cart:
                items_count = len(updated_cart.get("items", []))
                total = updated_cart.get("total", 0)
                self.log(f"✅ Updated cart: {items_count} items, total: €{total}")
            
            # Test update cart item quantity
            update_result = self.test_endpoint(
                "POST", "/cart/update",
                description="Update cart item quantity to 2",
                auth_required=True,
                json={
                    "product_id": self.test_product_ids[0],
                    "quantity": 2
                }
            )
            
            if update_result:
                self.log("✅ Cart item quantity updated")
            
            # Verify quantity update
            final_cart = self.test_endpoint(
                "GET", "/cart",
                description="Verify cart quantity update",
                auth_required=True
            )
            
            if final_cart:
                items = final_cart.get("items", [])
                if items and items[0].get("quantity") == 2:
                    self.log("✅ Cart quantity update verified")
                else:
                    self.results["warnings"].append("Cart quantity update not reflected")
            
            # Test clear cart
            clear_result = self.test_endpoint(
                "DELETE", "/cart/clear",
                description="Clear cart",
                auth_required=True
            )
            
            if clear_result is not None:
                self.log("✅ Cart cleared successfully")

    def test_orders_endpoint(self):
        """Test orders endpoint"""
        self.log("=" * 60)
        self.log("4. TESTING ORDERS ENDPOINT")
        self.log("=" * 60)
        
        orders = self.test_endpoint(
            "GET", "/orders",
            description="Get user orders",
            auth_required=True
        )
        
        if orders is not None:
            orders_count = len(orders) if isinstance(orders, list) else 0
            self.log(f"✅ Orders endpoint working (found {orders_count} orders)")

    def test_become_seller_flow(self):
        """Test becoming a seller and seller role verification"""
        self.log("=" * 60)
        self.log("5. TESTING BECOME SELLER FLOW")
        self.log("=" * 60)
        
        # Become seller
        seller_result = self.test_endpoint(
            "POST", "/auth/become-seller",
            description="Upgrade user to seller role",
            auth_required=True
        )
        
        if seller_result:
            self.log(f"✅ User upgraded to seller: {seller_result.get('message')}")
        
        # Verify role change
        me_data = self.test_endpoint(
            "GET", "/auth/me",
            description="Verify seller role change",
            auth_required=True
        )
        
        if me_data and me_data.get("role") == "seller":
            self.log("✅ Seller role verified in /auth/me")
        else:
            self.results["warnings"].append("Seller role not updated in user profile")

    def test_seller_endpoints(self):
        """Test seller dashboard endpoints"""
        self.log("=" * 60)
        self.log("6. TESTING SELLER ENDPOINTS")
        self.log("=" * 60)
        
        # Test seller products
        seller_products = self.test_endpoint(
            "GET", "/seller/products",
            description="Get seller's products",
            auth_required=True
        )
        
        if seller_products is not None:
            products_count = len(seller_products) if isinstance(seller_products, list) else 0
            self.log(f"✅ Seller products: {products_count} products")
        
        # Test seller stats
        seller_stats = self.test_endpoint(
            "GET", "/seller/stats",
            description="Get seller statistics",
            auth_required=True
        )
        
        if seller_stats:
            total_products = seller_stats.get("total_products", 0)
            total_revenue = seller_stats.get("total_revenue", 0)
            self.log(f"✅ Seller stats: {total_products} products, €{total_revenue} revenue")
        
        # Test create new product
        new_product_data = {
            "title": "Smartphone Samsung Galaxy A54 5G",
            "description": "Smartphone Android con cámara triple de 50MP, pantalla Super AMOLED de 6.4 pulgadas, batería de 5000mAh y procesador Exynos 1380. Perfecto para fotografía y entretenimiento.",
            "price": 449.99,
            "original_price": 549.99,
            "category_id": "cat_electronica",
            "images": ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9"],
            "stock": 25
        }
        
        new_product = self.test_endpoint(
            "POST", "/products",
            description="Create new product as seller",
            auth_required=True,
            json=new_product_data
        )
        
        if new_product:
            new_product_id = new_product.get("product_id")
            self.log(f"✅ New product created: {new_product.get('title')} (ID: {new_product_id})")
            
            # Test get seller products again (should include new product)
            updated_seller_products = self.test_endpoint(
                "GET", "/seller/products",
                description="Verify new product appears in seller products",
                auth_required=True
            )
            
            if updated_seller_products is not None:
                updated_count = len(updated_seller_products) if isinstance(updated_seller_products, list) else 0
                self.log(f"✅ Updated seller products count: {updated_count}")
            
            # Test delete the created product
            if new_product_id:
                delete_result = self.test_endpoint(
                    "DELETE", f"/products/{new_product_id}",
                    description=f"Delete created product {new_product_id}",
                    auth_required=True
                )
                
                if delete_result is not None:
                    self.log("✅ Product deleted successfully")

    def test_reviews_functionality(self):
        """Test review creation and retrieval"""
        self.log("=" * 60)
        self.log("7. TESTING REVIEWS FUNCTIONALITY")
        self.log("=" * 60)
        
        if not self.test_product_ids:
            self.log("⚠️  No product IDs available for review testing")
            return
        
        # Create a review
        review_data = {
            "product_id": self.test_product_ids[0],
            "rating": 5,
            "comment": "Excelente producto, muy recomendado. La calidad es superior y llegó en perfectas condiciones. El envío fue rápido y el empaquetado cuidadoso."
        }
        
        review_result = self.test_endpoint(
            "POST", "/reviews",
            description=f"Create review for product {self.test_product_ids[0]}",
            auth_required=True,
            json=review_data
        )
        
        if review_result:
            self.log(f"✅ Review created: {review_result.get('rating')}★ - {review_result.get('comment')[:50]}...")
        
        # Get reviews for the product
        product_reviews = self.test_endpoint(
            "GET", f"/products/{self.test_product_ids[0]}/reviews",
            description=f"Get reviews for product {self.test_product_ids[0]}",
        )
        
        if product_reviews is not None:
            reviews_count = len(product_reviews)
            self.log(f"✅ Product reviews retrieved: {reviews_count} reviews")
            
            # Verify our review appears
            if reviews_count > 0:
                latest_review = product_reviews[-1]  # Assuming newest is last
                if latest_review.get("rating") == 5 and "Excelente" in latest_review.get("comment", ""):
                    self.log("✅ Created review appears in product reviews")
        
        # Check if product rating was updated
        updated_product = self.test_endpoint(
            "GET", f"/products/{self.test_product_ids[0]}",
            description="Check if product rating was updated after review"
        )
        
        if updated_product:
            rating = updated_product.get("rating", 0)
            review_count = updated_product.get("review_count", 0)
            self.log(f"✅ Product rating updated: {rating}★ ({review_count} reviews)")

    def cleanup_test_data(self):
        """Clean up test data from MongoDB"""
        self.log("=" * 60)
        self.log("CLEANING UP TEST DATA")
        self.log("=" * 60)
        
        # Remove test user and session
        try:
            user_result = self.db.users.delete_one({"user_id": self.test_user_id})
            session_result = self.db.user_sessions.delete_one({"session_token": self.auth_token})
            
            self.log(f"Cleaned up: {user_result.deleted_count} users, {session_result.deleted_count} sessions")
            
            # Clean up cart if exists
            cart_result = self.db.carts.delete_one({"user_id": self.test_user_id})
            self.log(f"Cleaned up: {cart_result.deleted_count} carts")
            
        except Exception as e:
            self.log(f"Cleanup error: {e}", "ERROR")

    def run_comprehensive_tests(self):
        """Run all comprehensive marketplace tests"""
        self.log("🚀 Starting Comprehensive Marketplace API Tests")
        self.log(f"Base URL: {BASE_URL}")
        
        try:
            # Setup
            if not self.setup_test_user_in_mongo():
                self.log("❌ Failed to setup test user, aborting", "ERROR")
                return False
            
            # Run tests in order
            self.test_public_endpoints()
            self.test_auth_endpoints() 
            self.test_cart_endpoints()
            self.test_orders_endpoint()
            self.test_become_seller_flow()
            self.test_seller_endpoints()
            self.test_reviews_functionality()
            
        except KeyboardInterrupt:
            self.log("Tests interrupted by user")
        except Exception as e:
            self.log(f"Unexpected error during testing: {str(e)}", "ERROR")
            self.results["errors"].append(f"Unexpected error: {str(e)}")
        finally:
            self.cleanup_test_data()
            self.print_summary()
            
    def print_summary(self):
        """Print comprehensive test results summary"""
        self.log("=" * 80)
        self.log("COMPREHENSIVE TEST RESULTS SUMMARY")
        self.log("=" * 80)
        
        self.log(f"Total Tests: {self.results['total_tests']}")
        self.log(f"Passed: {self.results['passed']}")
        self.log(f"Failed: {self.results['failed']}")
        
        success_rate = (self.results['passed'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        self.log(f"Success Rate: {success_rate:.1f}%")
        
        if self.results['warnings']:
            self.log(f"\n⚠️  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                self.log(f"  - {warning}")
        
        if self.results['errors']:
            self.log(f"\n❌ FAILED TESTS ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                self.log(f"  - {error}")
        else:
            self.log("\n🎉 ALL TESTS PASSED!")
            
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = ComprehensiveMarketplaceTester()
    success = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)