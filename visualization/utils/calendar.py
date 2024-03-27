import calendar
import matplotlib.pyplot as plt

from constants import MONTH_NAMES, WEEK_DAYS

calendar.setfirstweekday(0)  # set 0 to get monday as first day of week


class DayNotInMonthError(ValueError):
    pass


class MplCalendar(object):
    def __init__(self, year: int, month: int):
        """
        Create a calendar object for the specified year and month

        @param year: Year represented by int
        @param month: Month represented by int
        """

        self.year = year
        self.month = month
        self.cal = calendar.monthcalendar(year, month)
        self.events = [[[] for _ in week] for week in self.cal]
        self.colors = [[None for _ in week] for week in self.cal]

    def _monthday_to_index(self, day: int) -> tuple[int, int]:
        """
        Convert a day of the month to a tuple of (week, weekday).he 2-d index of the day in the list of lists
        If the day is not in the month raise a DayNotInMonthError,which is a subclass of ValueError

        @param day: Day represented by int
        @return: A tuple of (week, weekday) where week is represented
        """

        for week_n, week in enumerate(self.cal):
            try:
                i = week.index(day)
                return week_n, i
            except ValueError:
                pass
        # couldn't find the day
        raise DayNotInMonthError("There aren't {} days in the month".format(day))

    def add_event(self, day: int, event_str: str) -> None:
        """
        Add an event string for the specified day

        @param day: Day represented by int
        @param event_str: String to be put in the calendar for the specified day

        @return: None
        """

        week, w_day = self._monthday_to_index(day)
        self.events[week][w_day].append(event_str)

    def _render(self, **kwargs) -> None:
        """
        Render the calendar figure

        @param kwargs: Parameters of the call
        @return: None
        """

        plot_defaults = dict(
            sharex=True,
            sharey=True,
            figsize=(20, 12),
            dpi=80,
        )
        plot_defaults.update(kwargs)
        f, axs = plt.subplots(
            len(self.cal), 7,
            **plot_defaults
        )

        # Iterate for each day of the month
        for week, ax_row in enumerate(axs):
            for week_day, ax in enumerate(ax_row):
                ax.set_xticks([])
                ax.set_yticks([])
                if self.colors[week][week_day] is not None:
                    ax.set_facecolor(self.colors[week][week_day])
                if self.cal[week][week_day] != 0:
                    ax.text(.95, .95,
                            str(self.cal[week][week_day]),
                            verticalalignment='top',
                            horizontalalignment='right')
                contents = "\n".join(self.events[week][week_day])
                ax.text(.01, .88, contents,
                        verticalalignment='top',
                        horizontalalignment='left',
                        fontsize=9)

        # use the titles of the first row as the weekdays
        for n, day in enumerate(WEEK_DAYS):
            axs[0][n].set_title(day)

        # Place subplots in a close grid
        f.subplots_adjust(hspace=0)
        f.subplots_adjust(wspace=0)
        f.suptitle(MONTH_NAMES[self.month - 1] + ' ' + str(self.year),
                   fontsize=20, fontweight='bold')
        plt.subplots_adjust(left=0.02, right=0.99, top=0.90, bottom=0.02)

    def show(self, **kwargs) -> None:
        """
        Display the calendar

        @param kwargs: Parameters of the call
        @return: None
        """

        self._render(**kwargs)
        plt.show()

    def save(self, filename: str, **kwargs) -> None:
        """
        Save the calendar to the specified image file.

        @param filename: String of the path to save the image.
        @param kwargs: Parameters of the call
        @return: None
        """
        self._render(**kwargs)
        plt.savefig(filename)
        plt.close()
