#!/usr/bin/env python3
"""
Backend API Testing Suite for Amazon-like Marketplace
Tests all major API endpoints without authentication requirements
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://marketplace-hub-381.preview.emergentagent.com/api"
TIMEOUT = 30

class BackendTester:
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.session = requests.Session()
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_endpoint(self, method, endpoint, expected_status=200, description="", **kwargs):
        """Generic test method for API endpoints"""
        self.results["total_tests"] += 1
        url = f"{BASE_URL}{endpoint}"
        
        try:
            self.log(f"Testing {method} {endpoint} - {description}")
            
            if method.upper() == "GET":
                response = self.session.get(url, timeout=TIMEOUT, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, timeout=TIMEOUT, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            # Check status code
            if response.status_code != expected_status:
                error = f"Expected status {expected_status}, got {response.status_code}"
                self.log(f"❌ FAILED: {error}", "ERROR")
                self.log(f"Response: {response.text[:200]}", "ERROR")
                self.results["failed"] += 1
                self.results["errors"].append(f"{endpoint}: {error}")
                return None
                
            # Try to parse JSON
            try:
                data = response.json()
                self.log(f"✅ PASSED: Status {response.status_code}")
                self.results["passed"] += 1
                return data
            except json.JSONDecodeError as e:
                error = f"Invalid JSON response: {str(e)}"
                self.log(f"❌ FAILED: {error}", "ERROR")
                self.results["failed"] += 1
                self.results["errors"].append(f"{endpoint}: {error}")
                return None
                
        except requests.exceptions.RequestException as e:
            error = f"Request failed: {str(e)}"
            self.log(f"❌ FAILED: {error}", "ERROR")
            self.results["failed"] += 1
            self.results["errors"].append(f"{endpoint}: {error}")
            return None
            
    def test_categories_api(self):
        """Test Categories API"""
        self.log("=" * 50)
        self.log("TESTING CATEGORIES API")
        self.log("=" * 50)
        
        categories = self.test_endpoint(
            "GET", "/categories",
            description="Get all categories (should return 14 categories)"
        )
        
        if categories:
            category_count = len(categories)
            self.log(f"Categories returned: {category_count}")
            
            if category_count == 14:
                self.log("✅ Category count validation PASSED (14 categories)")
            else:
                self.log(f"⚠️  Expected 14 categories, got {category_count}")
                
            # Check category structure
            if categories and isinstance(categories, list):
                sample_category = categories[0]
                required_fields = ["category_id", "name", "icon", "color"]
                missing_fields = [field for field in required_fields if field not in sample_category]
                
                if not missing_fields:
                    self.log("✅ Category structure validation PASSED")
                else:
                    self.log(f"⚠️  Missing fields in category: {missing_fields}")
                    
                # Print sample categories
                self.log("Sample categories:")
                for i, cat in enumerate(categories[:3]):
                    self.log(f"  {i+1}. {cat.get('name')} (ID: {cat.get('category_id')})")
                    
        return categories
        
    def test_products_api(self, categories=None):
        """Test Products API"""
        self.log("=" * 50)
        self.log("TESTING PRODUCTS API")
        self.log("=" * 50)
        
        # Test 1: Get all products
        products_data = self.test_endpoint(
            "GET", "/products",
            description="Get all products with total count"
        )
        
        if products_data:
            products = products_data.get("products", [])
            total = products_data.get("total", 0)
            
            self.log(f"Products returned: {len(products)}")
            self.log(f"Total count: {total}")
            
            if isinstance(products, list) and isinstance(total, int):
                self.log("✅ Products API structure validation PASSED")
            else:
                self.log("❌ Invalid products API response structure")
                
            # Print sample products
            if products:
                self.log("Sample products:")
                for i, product in enumerate(products[:3]):
                    self.log(f"  {i+1}. {product.get('title')} - €{product.get('price')}")
                    
        # Test 2: Get featured products
        featured_data = self.test_endpoint(
            "GET", "/products?featured=true",
            description="Get only featured products"
        )
        
        if featured_data:
            featured_products = featured_data.get("products", [])
            self.log(f"Featured products returned: {len(featured_products)}")
            
            # Validate all returned products are featured
            non_featured = [p for p in featured_products if not p.get("featured")]
            if not non_featured:
                self.log("✅ Featured products filter validation PASSED")
            else:
                self.log(f"❌ Found {len(non_featured)} non-featured products in featured results")
                
        # Test 3: Filter by category (if categories available)
        if categories and len(categories) > 0:
            test_category = "cat_electronica"
            category_data = self.test_endpoint(
                "GET", f"/products?category_id={test_category}",
                description=f"Filter products by category {test_category}"
            )
            
            if category_data:
                category_products = category_data.get("products", [])
                self.log(f"Products in {test_category}: {len(category_products)}")
                
                # Validate all products belong to the category
                wrong_category = [p for p in category_products if p.get("category_id") != test_category]
                if not wrong_category:
                    self.log("✅ Category filter validation PASSED")
                else:
                    self.log(f"❌ Found {len(wrong_category)} products with wrong category")
                    
        # Test 4: Get single product (if products exist)
        if products_data and products_data.get("products"):
            test_product_id = products_data["products"][0].get("product_id")
            if test_product_id:
                single_product = self.test_endpoint(
                    "GET", f"/products/{test_product_id}",
                    description=f"Get single product {test_product_id}"
                )
                
                if single_product:
                    if single_product.get("product_id") == test_product_id:
                        self.log("✅ Single product API validation PASSED")
                    else:
                        self.log("❌ Single product API returned wrong product")
                        
                # Test 5: Get reviews for the product
                reviews = self.test_endpoint(
                    "GET", f"/products/{test_product_id}/reviews",
                    description=f"Get reviews for product {test_product_id}"
                )
                
                if reviews is not None:  # Could be empty array
                    self.log(f"Reviews for product: {len(reviews)}")
                    self.log("✅ Product reviews API validation PASSED")
                    
        return products_data
        
    def test_seed_api(self):
        """Test Seed Data API"""
        self.log("=" * 50)
        self.log("TESTING SEED DATA API")
        self.log("=" * 50)
        
        seed_result = self.test_endpoint(
            "POST", "/seed",
            description="Seed sample products (creates 16 sample products)",
            json={}
        )
        
        if seed_result:
            message = seed_result.get("message", "")
            self.log(f"Seed result: {message}")
            
            if "16" in message or "product" in message.lower():
                self.log("✅ Seed API validation PASSED")
            else:
                self.log(f"⚠️  Unexpected seed message: {message}")
                
        return seed_result
        
    def test_product_search(self):
        """Test Product Search Functionality"""
        self.log("=" * 50)
        self.log("TESTING PRODUCT SEARCH")
        self.log("=" * 50)
        
        # Test search functionality
        search_terms = ["iPhone", "Samsung", "MacBook"]
        
        for term in search_terms:
            search_data = self.test_endpoint(
                "GET", f"/products?search={term}",
                description=f"Search products for '{term}'"
            )
            
            if search_data:
                search_results = search_data.get("products", [])
                self.log(f"Search results for '{term}': {len(search_results)}")
                
                # Validate search results contain the term
                if search_results:
                    matching_results = []
                    for product in search_results:
                        title = product.get("title", "").lower()
                        description = product.get("description", "").lower()
                        if term.lower() in title or term.lower() in description:
                            matching_results.append(product)
                            
                    match_ratio = len(matching_results) / len(search_results)
                    self.log(f"Search relevance: {match_ratio:.2%} ({len(matching_results)}/{len(search_results)})")
                    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("🚀 Starting Backend API Tests")
        self.log(f"Base URL: {BASE_URL}")
        
        try:
            # Test 1: Categories API
            categories = self.test_categories_api()
            
            # Test 2: Seed Data (run first to ensure we have products)
            self.test_seed_api()
            
            # Test 3: Products API (after seeding)
            products_data = self.test_products_api(categories)
            
            # Test 4: Search functionality
            self.test_product_search()
            
        except KeyboardInterrupt:
            self.log("Tests interrupted by user")
        except Exception as e:
            self.log(f"Unexpected error during testing: {str(e)}", "ERROR")
            self.results["errors"].append(f"Unexpected error: {str(e)}")
            
        finally:
            self.print_summary()
            
    def print_summary(self):
        """Print test results summary"""
        self.log("=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        self.log(f"Total Tests: {self.results['total_tests']}")
        self.log(f"Passed: {self.results['passed']}")
        self.log(f"Failed: {self.results['failed']}")
        
        success_rate = (self.results['passed'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        self.log(f"Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            self.log("\n❌ FAILED TESTS:")
            for error in self.results['errors']:
                self.log(f"  - {error}")
        else:
            self.log("\n✅ ALL TESTS PASSED!")
            
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)