import time
import logging

logger = logging.getLogger(__name__)


class RequestLogMiddleware:
    """
    Custom middleware — sits in the request/response cycle.
    
    Django's middleware chain (simplified):
    Request → Middleware1 → Middleware2 → View → Middleware2 → Middleware1 → Response
    
    Each middleware can:
    - Process the request before it reaches the view
    - Process the response before it goes to the browser
    - Short-circuit the chain (return a response early)
    """
    
    def __init__(self, get_response):
        """
        Called once when the server starts.
        get_response is a callable — either the next middleware or the view.
        """
        self.get_response = get_response

    def __call__(self, request):
        """Called on every request."""
        
        # ─── CODE HERE RUNS BEFORE THE VIEW ───
        start_time = time.time()
        
        # Pass request to the next middleware/view and get response
        response = self.get_response(request)
        
        # ─── CODE HERE RUNS AFTER THE VIEW ───
        duration = (time.time() - start_time) * 1000  # ms
        
        # Log every request: method, path, status code, duration
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        logger.debug(
            f"[{request.method}] {request.path} "
            f"→ {response.status_code} | {duration:.1f}ms | user={user}"
        )
        
        return response