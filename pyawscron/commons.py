"""
pyawscron.commons.py
~~~~~~~~~~~~~~~~~~~~

This module contains the implementation of the Commons class.

"""

import calendar
import datetime
import time

from typing import Iterator

from dateutil.relativedelta import relativedelta


class Commons:
    """A utility class that provides common functions for working with dates and times."""

    @staticmethod
    def python_to_aws_day_of_week(python_day_of_week: int) -> int:
        """
        Converts Python day of week (0-6, Monday-Sunday) to AWS day of week (1-7, Sunday-Saturday).

        Args:
            python_day_of_week (int): The Python day of week.

        Returns:
            int: The AWS day of week.
        """
        map = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 1}
        return map[python_day_of_week]

    @staticmethod
    def aws_to_python_day_of_week(aws_day_of_week: int) -> int:
        """
        Converts AWS day of week (1-7, Sunday-Saturday) to Python day of week (0-6, Monday-Sunday).

        Args:
            aws_day_of_week (int): The AWS day of week.

        Returns:
            int: The Python day of week.
        """
        map = {2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 1: 6}
        return map[aws_day_of_week]

    @staticmethod
    def array_find_first(sequence: Iterator[int], function):
        """
        Finds the first element in the sequence that satisfies the given function.

        Args:
            sequence (iterable): The sequence to search.
            function (callable): The function to apply to each element.

        Returns:
            Any: The first element that satisfies the function, or None if no such element is found.
        """
        for i in sequence:
            if function(i) is True:
                return i
        return None

    @staticmethod
    def array_find_last(sequence, function):
        """
        Finds the last element in the sequence that satisfies the given function.

        Args:
            sequence (iterable): The sequence to search.
            function (callable): The function to apply to each element.

        Returns:
            Any: The last element that satisfies the function, or None if no such element is found.
        """
        for seq in reversed(sequence):
            if function(seq) is True:
                return seq
        return None

    @staticmethod
    def get_days_of_month_from_days_of_week(year: int, month: int, days_of_week: list) -> list:
        """
        Gets the days of the month that correspond to the given days of the week.

        Args:
            year (int): The year.
            month (int): The month.
            days_of_week (list): The days of the week (e.g., ["MON", "TUE", "WED"]).

        Returns:
            list: The days of the month that correspond to the given days of the week.
        """
        days_of_month = []
        index = 0  # only for "#" use case
        no_of_days_in_month = calendar.monthrange(year, month)[1]
        for i in range(1, no_of_days_in_month + 1, 1):
            this_date = datetime.datetime(year, month, i, tzinfo=datetime.timezone.utc)
            # already after last day of month
            if this_date.month != month:
                break
            if days_of_week[0] == "L":
                if days_of_week[1] == Commons.python_to_aws_day_of_week(this_date.weekday()):
                    same_day_next_week = datetime.datetime.fromtimestamp(
                        int(this_date.timestamp()) + 7 * 24 * 3600,
                        tz=datetime.timezone.utc,
                    )
                    if same_day_next_week.month != this_date.month:
                        return [i]
            elif days_of_week[0] == "#":
                if days_of_week[1] == Commons.python_to_aws_day_of_week(this_date.weekday()):
                    index += 1
                if days_of_week[2] == index:
                    return [i]
            elif Commons.python_to_aws_day_of_week(this_date.weekday()) in days_of_week:
                days_of_month.append(i)
        return days_of_month

    @staticmethod
    def get_days_of_month_for_L(year: int, month: int, days_before: int) -> list:
        """
        Gets the days of the month for the "L" day of the week.

        Args:
            year (int): The year.
            month (int): The month.
            days_before (int): The number of days before the last day of the month.

        Returns:
            list: The days of the month for the "L" day of the week.

        Raises:
            Exception: If the calculation fails.
        """
        for i in range(31, 28 - 1, -1):
            this_date = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc) + relativedelta(days=i - 1)
            if this_date.month == month:
                return [i - days_before]
        raise Exception("get_days_of_month_for_L - should not happen")

    @staticmethod
    def get_days_of_month_for_W(year: int, month: int, day: int) -> list:
        """
        Gets the days of the month for the "W" day of the week.

        Args:
            year (int): The year.
            month (int): The month.
            day (int): The day of the week.

        Returns:
            list: The days of the month for the "W" day of the week.

        Raises:
            Exception: If the calculation fails.
        """
        offset = Commons.array_find_first([0, 1, -1, 2, -2], lambda c: Commons.is_weekday(year, month, day + c))
        if offset is None:
            raise Exception("get_days_of_month_for_W, offset is None which should never happen")
        result = day + offset

        last_day_of_month = calendar.monthrange(year, month)[1]
        if result > last_day_of_month:
            return []
        return [result]

    @staticmethod
    def is_weekday(year: int, month: int, day: int) -> bool:
        """
        Checks if the given date is a weekday.

        Args:
            year (int): The year.
            month (int): The month.
            day (int): The day.

        Returns:
            bool: True if the date is a weekday, False otherwise.
        """
        if day < 1 or day > 31:
            return False
        this_date = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc) + relativedelta(days=day - 1)
        if not (this_date.month == month and this_date.year == year):
            return False
        # pyhthon: Mon:0 Friday:4
        return this_date.weekday() >= 0 and this_date.weekday() <= 4

    @staticmethod
    def current_milli_time() -> int:
        """
        Gets the current time in milliseconds.

        Returns:
            int: The current time in milliseconds.
        """
        return round(time.time() * 1000)

    @staticmethod
    def datetime_to_millisec(dt_obj: datetime.datetime) -> float:
        """
        Converts a datetime object to milliseconds.

        Args:
            dt_obj (datetime.datetime): The datetime object.

        Returns:
            float: The datetime in milliseconds.
        """
        return dt_obj.timestamp() * 1000

    @staticmethod
    def is_day_in_month(year: int, month: int, test_day: int) -> bool:
        """
        Checks if the given day is valid for the given year and month.

        Args:
            year (int): The year.
            month (int): The month.
            test_day (int): The day to test.

        Returns:
            bool: True if the day is valid, False otherwise.
        """
        try:
            datetime.datetime(year, month, test_day, tzinfo=datetime.timezone.utc)
            return True
        except ValueError as e:
            if str(e) == "day is out of range for month":
                return False
        return False
