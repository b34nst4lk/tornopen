from functools import wraps


# Decorators
def tags(*tag_list):
    def decorator(func):
        func._openapi_tags = [*tag_list]

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def summary(summary_text):
    def decorator(func):
        func._openapi_summary = summary_text

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
