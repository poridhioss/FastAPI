from fastapi import FastAPI, Query, Path
from enum import Enum
from typing import Optional, List
from datetime import datetime

app = FastAPI(
    title="FastAPI Fundamentals Lab",
    description="A comprehensive API demonstrating FastAPI fundamentals",
    version="1.0.0"
)

# Health check endpoint
@app.get("/ping")
def ping():
    """Simple health check endpoint"""
    return {"message": "pong", "timestamp": datetime.now().isoformat()}

# Basic greeting without parameters
@app.get("/hello")
def say_hello(name: str = "World"):
    """Basic greeting with default parameter"""
    return {"message": f"Hello, {name}!"}

# Path parameter example
@app.get("/hello/{name}")
def hello_name(name: str = Path(..., description="Name to greet")):
    """Greeting with path parameter"""
    return {"message": f"Hello, {name}!"}

# Enum for validation
class BlogType(str, Enum):
    short = 'short'
    story = 'story'
    howto = 'howto'
    tutorial = 'tutorial'
    news = 'news'

# Path parameter with enum validation
@app.get("/blog/type/{type}")
def get_blog_by_type(type: BlogType):
    """Get blogs by type using enum validation"""
    return {"message": f"Fetching {type.value} blogs", "blog_type": type}

# Integer path parameter with validation
@app.get("/user/{user_id}")
def get_user(user_id: int = Path(..., gt=0, description="User ID must be positive")):
    """Get user by ID with validation"""
    return {"user_id": user_id, "message": f"User {user_id} details"}

# Multiple path parameters
@app.get("/blogs/{blog_id}/comments/{comment_id}")
def get_comment(
    blog_id: int = Path(..., gt=0, description="Blog ID"),
    comment_id: int = Path(..., gt=0, description="Comment ID"),
    valid: bool = Query(True, description="Filter by valid comments"),
    username: Optional[str] = Query(None, description="Filter by username")
):
    """Get specific comment from a blog with query filters"""
    return {
        'blog_id': blog_id,
        'comment_id': comment_id,
        'valid': valid,
        'username': username,
        'message': f'Comment {comment_id} from blog {blog_id}'
    }

# Query parameters with defaults
@app.get("/blog/all")
def get_all_blogs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get all blogs with pagination"""
    return {
        "page": page,
        "page_size": page_size,
        "message": f"Showing {page_size} blogs on page {page}"
    }

# Optional query parameters
@app.get("/blog/search")
def search_blogs(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[BlogType] = Query(None, description="Filter by category"),
    author: Optional[str] = Query(None, description="Filter by author"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    published_after: Optional[str] = Query(None, description="Published after date (YYYY-MM-DD)")
):
    """Search blogs with multiple optional filters"""
    filters = {
        "query": q,
        "category": category,
        "author": author,
        "tags": tags,
        "published_after": published_after
    }
    # Remove None values
    active_filters = {k: v for k, v in filters.items() if v is not None}
    
    return {
        "message": "Blog search results",
        "filters_applied": active_filters,
        "total_filters": len(active_filters)
    }

# Complex path and query parameter combination
@app.get("/api/v1/users/{user_id}/posts/{post_id}")
def get_user_post(
    user_id: int = Path(..., gt=0, description="User ID"),
    post_id: int = Path(..., gt=0, description="Post ID"),
    include_comments: bool = Query(False, description="Include comments in response"),
    include_likes: bool = Query(False, description="Include likes count"),
    format: str = Query("json", regex="^(json|xml|csv)$", description="Response format")
):
    """Get a specific post from a user with various options"""
    return {
        "user_id": user_id,
        "post_id": post_id,
        "include_comments": include_comments,
        "include_likes": include_likes,
        "format": format,
        "message": f"Post {post_id} by user {user_id}"
    }

# String validation with regex
@app.get("/validate/email/{email}")
def validate_email(
    email: str = Path(..., regex=r'^[^@]+@[^@]+\.[^@]+$', description="Valid email address")
):
    """Validate email format using regex"""
    return {"email": email, "message": "Valid email format"}

# Numeric validation examples
@app.get("/products/{product_id}")
def get_product(
    product_id: int = Path(..., ge=1, le=999999, description="Product ID"),
    discount: Optional[float] = Query(None, ge=0.0, le=100.0, description="Discount percentage"),
    currency: str = Query("USD", regex="^[A-Z]{3}$", description="3-letter currency code")
):
    """Get product with price calculations"""
    return {
        "product_id": product_id,
        "discount": discount,
        "currency": currency,
        "message": f"Product {product_id} details"
    }

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "FastAPI Fundamentals Lab",
        "version": "1.0.0",
        "endpoints": {
            "health": "/ping",
            "greeting": "/hello",
            "blogs": "/blog/all",
            "search": "/blog/search",
            "documentation": "/docs"
        }
    }

# Additional endpoint for testing various parameter types
@app.get("/test/parameters")
def test_parameters(
    # String parameters
    name: str = Query(..., min_length=1, max_length=50, description="Name parameter"),
    
    # Numeric parameters
    age: int = Query(..., ge=0, le=150, description="Age parameter"),
    height: float = Query(..., gt=0, le=300, description="Height in cm"),
    
    # Boolean parameter
    is_active: bool = Query(True, description="Active status"),
    
    # List parameter
    hobbies: List[str] = Query([], description="List of hobbies"),
    
    # Optional parameters
    email: Optional[str] = Query(None, regex=r'^[^@]+@[^@]+\.[^@]+$', description="Email address"),
    phone: Optional[str] = Query(None, description="Phone number")
):
    """Test endpoint with various parameter types and validations"""
    return {
        "name": name,
        "age": age,
        "height": height,
        "is_active": is_active,
        "hobbies": hobbies,
        "email": email,
        "phone": phone,
        "message": "All parameters received successfully"
    }