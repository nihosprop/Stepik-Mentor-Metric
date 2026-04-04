import asyncio
import logging

from dataclasses import dataclass
from typing import Any

import aiohttp

from aiohttp import ClientResponseError, ClientSession
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


@dataclass
class StepikAPIClient:
    client_id: str
    client_secret: str
    redis_cache: Redis
    session: ClientSession
    base_url: str = 'https://stepik.org/api'

    async def reset_stepik_token(self) -> None:
        await self.redis_cache.delete('stepik_token')
        logger.info('Stepik token cleared of Redis')

    async def _get_access_token(self) -> str:
        """
        Get token.
        First it tries to take it from Redis, if not, it asks the API.
        """
        cached_token = await self.redis_cache.get('stepik_token')
        if cached_token:
            logger.debug('Stepik token from Redis cache')
            return cached_token

        url = 'https://stepik.org/oauth2/token/'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        try:
            async with self.session.post(url, data=data) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(
                        f'Error receiving token: {resp.status} {text}'
                    )

                response_json = await resp.json()
                access_token = response_json.get('access_token')
                expires_in = response_json.get('expires_in', 36000)

                if not access_token:
                    raise RuntimeError('Token not found in API response')

                # We save with TTL a little less than real (reserve 5 minutes)
                await self.redis_cache.set(
                    'stepik_token', access_token, ex=max(expires_in - 300, 60)
                )
                logger.info('New Stepik token received and saved')
                return access_token

        except Exception as e:
            logger.error(
                f'Critical error when updating token: {e}', exc_info=True
            )
            raise

    # OPT: Ruff(too-many-arguments)-(6 > 5)
    async def make_api_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        expected_status_codes: list[int] | None = None,
        attempts: int = 3,
    ) -> dict[str, Any] | None:
        if expected_status_codes is None:
            expected_status_codes = [200, 201]

        endpoint = endpoint.lstrip('/')
        url = (
            endpoint
            if endpoint.startswith('http')
            else f'{self.base_url}/{endpoint.lstrip("/")}'
        )

        token = await self._get_access_token()
        headers = {'Authorization': f'Bearer {token}'}

        try:
            async with self.session.request(
                method, url, headers=headers, params=params, json=json_data
            ) as response:
                # Retry logic for expired token (401)
                if response.status == 401 and attempts > 1:
                    logger.warning(
                        f'401 Unauthorized.'
                        f' Repeat request for a new token.'
                        f' Attempts left: {attempts - 1}'
                    )
                    return await self.make_api_request(
                        method=method,
                        endpoint=endpoint,
                        params=params,
                        json_data=json_data,
                        expected_status_codes=expected_status_codes,
                        attempts=attempts - 1,
                    )

                # Processing 429 (Rate Limit)
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                    logger.warning(f'Rate limited. Wait {retry_after} sec.')
                    await asyncio.sleep(retry_after)
                    return await self.make_api_request(
                        method=method,
                        endpoint=endpoint,
                        params=params,
                        json_data=json_data,
                        expected_status_codes=expected_status_codes,
                        attempts=attempts,
                    )

                if response.status in (502, 503, 504) and attempts > 1:
                    retry_after = int(
                        response.headers.get(
                            'Retry-After', 2 ** (3 - attempts)
                        )
                    )
                    logger.warning(
                        f'Server error {response.status}. '
                        f'Retrying in'
                        f' {retry_after}s (attempts left: {attempts - 1})'
                    )
                    await asyncio.sleep(retry_after)
                    return await self.make_api_request(
                        method=method,
                        endpoint=endpoint,
                        params=params,
                        json_data=json_data,
                        expected_status_codes=expected_status_codes,
                        attempts=attempts - 1,
                    )

                if response.status not in expected_status_codes:
                    body_text = await response.text()
                    if response.status == 404:
                        logger.info(f'Resource not found: {url}')
                        return None
                    logger.error(f'API Fail {response.status}: {body_text}')
                    raise ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=body_text,
                    )

                if response.status == 204:
                    return None
                return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f'Network error when requesting {url}: {e}')
            raise

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        res = await self.make_api_request('GET', f'users/{user_id}')
        if res and res.get('users'):
            return res['users'][0]
        return None

    @staticmethod
    def get_link_to_user(user_id: int) -> str:
        """Generates a direct link to the user's profile."""
        return f'https://stepik.org/users/{user_id}/profile'

    async def get_course(self, course_id: int) -> dict[str, Any] | None:
        res = await self.make_api_request('GET', f'courses/{course_id}')
        if res and res.get('courses'):
            return res['courses'][0]
        return None

    async def get_username(self, user_id: int) -> str | None:
        user = await self.get_user(user_id)
        return user.get('full_name') if user else None

    async def get_course_title(self, course_id: int) -> str | None:
        res = await self.make_api_request('GET', f'courses/{course_id}')
        if res and res.get('courses'):
            return res['courses'][0].get('title')
        return None

    async def get_step_data(self, target_id: int) -> dict[str, Any] | None:
        return await self.make_api_request('GET', f'steps/{target_id}')

    async def get_comment_data(self, comment_id: int) -> dict[str, Any] | None:
        res = await self.make_api_request('GET', f'comments/{comment_id}')
        return res if res and res.get('comments') else None

    # --- Specific logic ---
    async def get_comments(
        self, course_id: int, page: int = 1, limit: int = 20
    ) -> dict[str, Any] | None:
        """
        Retrieves the latest course comments.
        Important: Stepik defaults to 20 elements per page.
        """
        params = {
            'page': page,
            'page_size': limit,
            'course': course_id,
            'sort': 'time',
            'order': 'desc',
        }

        comments = await self.make_api_request(
            'GET', 'comments', params=params
        )
        return comments

    async def get_comment_url_context(self, comment_id: int) -> str:
        """
        Generates a link to the comment.
        """
        comment_payload = await self.get_comment_data(comment_id)
        if not comment_payload:
            return f'https://stepik.org/discussion/comments/{comment_id}/'

        comment = comment_payload['comments'][0]
        target_id = comment.get('target')  # This is the step ID

        step_payload = await self.get_step_data(target_id)
        if not step_payload or not step_payload.get('steps'):
            return f'https://stepik.org/discussion/comments/{comment_id}/'

        step = step_payload['steps'][0]
        lesson_id = step.get('lesson')
        step_pos = step.get('position')

        return (
            f'https://stepik.org/lesson/{lesson_id}/step/'
            f'{step_pos}?discussion={comment_id}'
        )

    async def get_comment_url(self, comment_id: int) -> str:
        try:
            comment_data = await self.get_comment_data(comment_id)
            if not comment_data or not comment_data.get('comments'):
                return f'https://stepik.org/discussion/comments/{comment_id}/'

            comment = comment_data['comments'][0]
            parent_id = comment.get('parent')
            thread_type = comment.get('thread', 'discussion')

            target_id = comment.get('target')
            if not target_id:
                return f'https://stepik.org/discussion/comments/{comment_id}/'

            step_data = await self.get_step_data(target_id)
            if not step_data or not step_data.get('steps'):
                return f'https://stepik.org/discussion/comments/{comment_id}/'

            step = step_data['steps'][0]
            lesson_id = step.get('lesson')
            step_position = step.get('position', 1)
            unit_id = step.get('unit')

            base_url = (
                f'https://stepik.org/lesson/{lesson_id}/step/{step_position}?'
            )

            params = []

            if thread_type == 'solutions':
                if parent_id:
                    params.append(f'discussion={parent_id}')
                    params.append(f'reply={comment_id}')
                else:
                    params.append(f'discussion={comment_id}')
                params.append('thread=solutions')

            else:
                discussion_param = parent_id if parent_id else comment_id
                params.append(f'discussion={discussion_param}')
                if parent_id:
                    params.append(f'reply={comment_id}')

            if unit_id:
                params.append(f'unit={unit_id}')

            query_string = '&'.join(params)
            return f'{base_url}{query_string}'

        except Exception as e:
            logging.error(
                f'Error generating URL for comment {comment_id}: {str(e)}',
                exc_info=True,
            )
            return f'https://stepik.org/discussion/comments/{comment_id}/'
