from datetime import datetime


class DateTimeTool:
    @staticmethod
    def answer(question: str):
        now = datetime.now()
        return (
            f"The current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')} local time. "
            f"The day is {now.strftime('%A')} and the date is {now.strftime('%d %B %Y')}."
        )
