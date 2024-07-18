
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as Exceptions
# for log
import logging
from rich.console import Console
from rich.logging import RichHandler

class SeleniumDriverHelper:
    """
    Tool class to afford convenience.
    """

    def __init__(self, driver):

        # 配置浏览器 driver
        self.browser = driver

        # 配置日志
        self.logger = logging.getLogger(self.__class__.__name__)

    def sleepy_find_element(self, by, query, attempt_count: int = 30, sleep_duration: int = 3, fail_ok: bool = False):
        """
        Finds the web element using the locator and query.

        This function attempts to find the element multiple times with a specified
        sleep duration between attempts. If the element is found, the function returns the element.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.
            attempt_count (int, optional): The number of attempts to find the element. Default: 20.
            sleep_duration (int, optional): The duration to sleep between attempts. Default: 1.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: Web element or None if not found.
        """
        for _count in range(attempt_count):
            item = self.browser.find_elements(by, query)
            if len(item) > 0:
                item = item[0]
                self.logger.debug(f'Element {query} has found')
                break
            self.logger.debug(f'Element {query} is not present, attempt: {_count+1}')
            time.sleep(sleep_duration)
        else:
            if fail_ok:
                self.logger.debug(f'Element {query} is not found.')
                return None
            self.logger.error(f'Element {query} is not found.')
            raise Exceptions.NoSuchElementException(f'Element {query} is not found.')
        return item

    def wait_until_disappear(self, by, query, timeout_duration=60):
        """
        Waits until the specified web element disappears from the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is no longer present on the page.
        Once the element has disappeared, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.
            timeout_duration (int, optional): The total wait time before the timeout exception. Default: 15.

        Returns:
            None
        """
        self.logger.debug(f'Waiting element {query} to disappear.')
        try:
            WebDriverWait(
                self.browser,
                timeout_duration
            ).until_not(
                EC.presence_of_element_located((by, query))  # noqa
            )
            self.logger.debug(f'Element {query} disappeared.')
        except Exceptions.TimeoutException:
            self.logger.debug(f'Element {query} still here, something is wrong.')
            raise
        return

    def wait_until_appear(self, by, query, timeout_duration=60):
        """
        Waits until the specified web element appears on the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is present on the page.
        Once the element appears, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.
            timeout_duration (int, optional): The total wait time before the timeout exception. Default: 15.

        Returns:
            None
        """
        self.logger.debug(f'Waiting for element {query} to appear.')
        try:
            WebDriverWait(
                self.browser,
                timeout_duration
            ).until(
                EC.presence_of_element_located((by, query))  # noqa
            )
            self.logger.debug(f'Element {query} appeared.')
        except Exceptions.TimeoutException:
            self.logger.error(f'Element {query} did not appear within {timeout_duration} seconds.')
            raise
        return

    def find_or_fail(self, by, query, return_elements=False, fail_ok=False):
        """
        Finds a list of elements given query, if none of the items exists, throws an error

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            query (str): The query string to locate the element.

        Returns:
            selenium.webdriver.remote.webelement.WebElement: Web element or None if not found.
        """
        dom_element = self.browser.find_elements(by, query)
        if not dom_element:
            if not fail_ok:
                self.logger.error(f'{query} is not located. Please raise an issue with verbose=True')
            return None

        self.logger.debug(f'{query} is located.')
        if return_elements:
            return dom_element
        else:
            return dom_element[0]