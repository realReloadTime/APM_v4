from django.middleware.csrf import CsrfViewMiddleware

class DisableCsrfForApi(CsrfViewMiddleware):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith('/api/'):
            return None
        return super().process_view(request, view_func, view_args, view_kwargs)
