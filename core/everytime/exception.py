import sys
from functools import wraps
from selenium.common.exceptions import (NoSuchElementException, 
                                        WebDriverException, 
                                        NoSuchWindowException)
from core.everytime.transform import _selenium_error_transform

def exception_handler(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        
        except KeyboardInterrupt:
            sys.exit("Execution stopped by user (Ctrl+C).")
        
        except NoSuchElementException as e:
            # The login method should continue even if an element is not found
            raise _selenium_error_transform(e)
        
        except (WebDriverException, NoSuchWindowException) as e:
            sys.exit("Terminating due to ChromeDriver connection failure.")

        except Exception as e:
            sys.exit("Terminating due to an unknown error.")

    return wrapper
