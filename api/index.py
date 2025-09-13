from main import app

# Vercel expects a handler function for serverless
def handler(request, **kwargs):
    return app(request.environ, request.start_response)