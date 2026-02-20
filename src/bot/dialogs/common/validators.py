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