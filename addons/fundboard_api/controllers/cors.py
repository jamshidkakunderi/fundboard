from functools import wraps


def cors(origin=None, methods=None, headers=None,
         max_age=None, attach_to_all=True,
         automatic_options=True, provide_automatic_options=None,
         vary_header=True, resources=None, intercept_exceptions=True,
         always_send=True, path_regex=None):

    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = methods
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return wrapped_function

    return decorator
