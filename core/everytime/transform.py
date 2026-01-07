def _selenium_error_transform(error):
    # Convert the exception to a string
    error_message = str(error)
    
    if "(Session info:" in error_message:
        # Handle specific case if needed
        return error_message.split("\n  (Session info: ")[0]
    
    return error_message