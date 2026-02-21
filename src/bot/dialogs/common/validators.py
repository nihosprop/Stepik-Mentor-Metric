import re


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