"""
Example: How to integrate security middleware into FastAPI application.

This example shows how to properly configure SecureMultipartMiddleware
to protect against DoS attacks via malicious multipart forms.
"""
from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import JSONResponse

# Import security components
from services.api.config import APIConfig
from services.api.middleware import SecureMultipartMiddleware

# Create FastAPI application
app = FastAPI(
    title="Secure API Example",
    description="API with security middleware enabled",
)

# Add security middleware
app.add_middleware(SecureMultipartMiddleware)


# Optional: Add custom request size middleware
@app.middleware("http")
async def enforce_request_size_limits(request: Request, call_next):
    """
    Additional middleware to enforce overall request size limits.
    
    This complements SecureMultipartMiddleware by checking total
    request size before processing.
    """
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            size = int(content_length)
            if size > APIConfig.MAX_REQUEST_SIZE:
                return JSONResponse(
                    {
                        "error": "Request too large",
                        "detail": f"Request exceeds maximum size of {APIConfig.MAX_REQUEST_SIZE} bytes",
                        "max_allowed": APIConfig.MAX_REQUEST_SIZE,
                    },
                    status_code=413,
                )
        except ValueError:
            pass  # Invalid Content-Length header, let request proceed
    
    response = await call_next(request)
    return response


# Example endpoint with file upload
@app.post("/upload")
async def upload_file(file: UploadFile):
    """
    Example file upload endpoint.
    
    Security is automatically enforced by middleware:
    - SecureMultipartMiddleware checks form size
    - enforce_request_size_limits checks total request size
    """
    # Process file
    contents = await file.read()
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
        "status": "uploaded",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "security": "enabled"}


if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=APIConfig.REQUEST_TIMEOUT,
    )
