import re


def check_tg_user_id(text: str) -> str:
    """
    Checks if the input string is a valid Telegram user ID.

    Args:
        text (str): The input string to be validated.
    Returns:
        str: The input string if it is a valid Telegram user ID.
    Raises:
        ValueError: If the input string is not a valid Telegram user ID.
    """
    cleaned_text = text.strip()

    if cleaned_text.isdecimal() and int(cleaned_text) >= 10000:
        return cleaned_text
    raise ValueError


def check_stepik_profile_link(link: str) -> str:
    match = re.search(
        r'\bhttps?://[^\s/]+/users/(\d+)(?:/profile)?/?\b',
        link,
        re.IGNORECASE,
    )

    if match:
        stepik_user_id = match.group(1)
        return stepik_user_id

    raise ValueError


def check_stepik_course_link(link: str) -> str:
    """
    Retrieves the course ID from the Stepik link.
    Accepts links like:
    - https://stepik.org/course/12345
    - https://stepik.org/course/12345/promo
    - https://stepik.org/course/12345/syllabus
    """
    match = re.search(
        r'\bhttps?://[^\s/]+/course/(\d+)(?:/[^/\s]*)?/?\b',
        link,
        re.IGNORECASE,
    )

    if match:
        stepik_course_id = match.group(1)
        return stepik_course_id

    raise ValueError
