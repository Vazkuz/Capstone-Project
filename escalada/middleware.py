class PruebaMiddleware:
    # Se llama al inicializar el middleware
    def __init__(self, get_response):
        self.get_response = get_response
    
    # Se llama una vez cada que recargas la página
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        pass