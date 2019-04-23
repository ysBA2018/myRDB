from django.http import QueryDict


class HttpPostTunnelingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        '''
            Matchin POST Requests on CRUD-Methods
        '''
        if 'X_METHODOVERRIDE' in request.POST.keys():
            http_method = request.POST['X_METHODOVERRIDE']
            if http_method.lower() == 'put':
                request.method = 'PUT'
                request.META['REQUEST_METHOD'] = 'PUT'
                request.PUT = QueryDict(request.body)
            if http_method.lower() == 'patch':
                request.method = 'PATCH'
                request.META['REQUEST_METHOD'] = 'PATCH'
                request.PATCH = QueryDict(request.body)
            if http_method.lower() == 'delete':
                request.method = 'DELETE'
                request.META['REQUEST_METHOD'] = 'DELETE'
                request.DELETE = QueryDict(request.body)
            if http_method.lower() == 'create':
                request.method = 'CREATE'
                request.META['REQUEST_METHOD'] = 'CREATE'
                request.CREATE = QueryDict(request.body)

                #TODO: Beim verlassen von Profile zu Compare oder RightAnalysis <- hier sessionvariablen wie table_data oder user_data anpassen auf templatevariablen
        return self.get_response(request)
