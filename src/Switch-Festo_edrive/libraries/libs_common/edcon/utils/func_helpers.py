"""Helper functions used to call other functions."""

import time
from collections.abc import Callable
from edcon.utils.logging import Logging


def func_sequence(func: Callable[[bool], None],
                  arg_list: list = True, delay: float = 0.1):
    """Performs a toggling sequence on a provided toggle function

    Parameter:
        func (Callable): function that is called sequentially with arg from arg_list
        delay (float): delay to use between calls of func
    """
    for arg in arg_list:
        func(arg)

        # Wait for trigger
        time.sleep(delay)


def wait_until(condition: Callable[[], bool] = None,
               error_condition: Callable[[], bool] = None,
               timeout: float = 0.0,
               info_string: Callable[[], str] = None,
               error_string: Callable[[], str] = None) -> bool:
    """Waits until provided condition is satisfied

    Parameter:
        condition (Callable): boolean condition function
        error_condition (Callable): boolean error condition function which terminates waiting
        timeout (float): Time that should be waited for condition to be satisfied (in seconds)
        info_string (Callable): optional callback for string to print during wait process
        error_string (Callable): optional callback for string to print in error case

    Returns:
        bool: True if succesful, False otherwise
    """
    start_time = time.time()
    while timeout == 0.0 or not time.time() - start_time > timeout:
        if condition and condition():
            return True
        if error_condition and error_condition():
            if error_string:
                Logging.logger.error(error_string())
            return False
        if info_string:
            Logging.logger.info(info_string())
    Logging.logger.error(f"Cancelled due to timeout after {timeout} s")
    if error_string:
        Logging.logger.error(error_string())
    return False


def wait_for(duration: float,
             error_condition: Callable[[], bool] = None,
             info_string: Callable[[], str] = None,
             error_string: Callable[[], str] = None) -> bool:
    """Waits for provided duration

    Parameter:
        duration (float): time that should be waited for
        error_condition (Callable): boolean error condition function which terminates waiting
        info_string (Callable): optional callback for string to print during wait process
        error_string (Callable): optional callback for string to print in error case

    Returns:
        bool: True if succesful, False otherwise
    """
    start_time = time.time()
    while duration == 0.0 or not time.time() - start_time > duration:
        if error_condition and error_condition():
            if error_string:
                Logging.logger.error(error_string())
            return False
        if info_string:
            Logging.logger.info(info_string())
    Logging.logger.info(f"Duration of {duration} seconds passed")
    return True
