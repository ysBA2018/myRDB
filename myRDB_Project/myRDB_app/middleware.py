from django.http import QueryDict


class HttpPostTunnelingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        '''
        if 'action_type' in request.POST.keys():
            if request.POST['action_type']=="update_session":
                if "trash_table_data" in request.POST.keys():
                    request.session['delete_list_table_data']=request.POST['trash_table_data']['data']
                if "trash_graph_data" in request.POST.keys():
                    request.session['delete_list_graph_data'] = request.POST['trash_graph_data']
                if "user_graph_data" in request.POST.keys():
                    request.session['user_data'] = request.POST['user_graph_data']
                if "user_table_data" in request.POST.keys():
                    request.session['table_data'] = request.POST['user_table_data']['data']
                return self.get_response(request)
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
