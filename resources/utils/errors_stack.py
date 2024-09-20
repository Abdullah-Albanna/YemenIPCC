import inspect


def getStack():
    frame_info = inspect.stack()
    stack_trace = []

    for frame in frame_info:
        function_name = frame.function
        filename = frame.filename
        line_number = frame.lineno

        if function_name == "getStack":
            continue

        stack_trace.append(f"Function {function_name} in {filename}:{line_number}")

    return "\n".join(stack_trace)
