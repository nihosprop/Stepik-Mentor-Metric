import asyncio
import html
import json
import logging
import re

import aiohttp

from aiohttp import (
    ClientOSError,
    ClientPayloadError,
    ClientTimeout,
    ServerTimeoutError,
)
from pydantic import SecretStr

logger = logging.getLogger(__name__)


class GeminiCommentEvaluator:
    def __init__(
        self, api_key: SecretStr, session: aiohttp.ClientSession
    ) -> None:
        self._api_key = api_key.get_secret_value()
        self._session = session
        self._url = (
            f'https://generativelanguage.googleapis.com/'
            f'v1beta/models/'
            f'gemini-2.5-flash-lite:generateContent?key={self._api_key}'
        )

    async def is_meaningful_question(self, text: str) -> bool:
        clean_text = await self._clean_html_tags(text.strip())

        if len(set(clean_text.lower())) < 4 or clean_text.lower() in [
            'спасибо',
            'благодарю',
            'отлично',
        ]:
            logger.warning(f'Short or Non-Text comment: {clean_text}')
            return False

        payload = {
            'systemInstruction': {
                'parts': [
                    {
                        'text': (
                            'Ты —'
                            ' эксперт-классификатор комментариев на учебной'
                            ' платформе Stepik. '
                            'Твоя задача — найти только те сообщения,'
                            ' которые требуют ответа наставника. '
                            'Верни is_question:'
                            ' true ТОЛЬКО если в тексте есть: '
                            '1. Конкретный вопрос по учебному'
                            ' материалу или коду. '
                            '2. Просьба объяснить ошибку или помочь'
                            ' с решением. '
                            '3. Другие просьбы о помощи. '
                            'Верни is_question: false (ШУМ), если это: '
                            "1. Благодарность ('спасибо', 'курс супер'). "
                            '2. Просто утверждение о прогрессе'
                            " ('я решил', 'прошел половину', 'иду дальше'). "
                            '3. Дружеская беседа, шутки или личные планы,'
                            ' не содержащие вопросов. '
                            '4. Обсуждение авторов или других курсов без'
                            ' просьбы о помощи.'
                        )
                    }
                ]
            },
            'contents': [{'parts': [{'text': clean_text}]}],
            'generationConfig': {
                'temperature': 0.0,
                'maxOutputTokens': 180,
                'responseMimeType': 'application/json',
                'responseSchema': {
                    'type': 'OBJECT',
                    'properties': {
                        'reasoning': {
                            'type': 'STRING',
                            'description': 'Краткое обоснование в одно'
                            ' предложение(максимум 10 слов)',
                        },
                        'is_question': {
                            'type': 'BOOLEAN',
                            'description': 'true, если нужен ответ ментора',
                        },
                    },
                    'required': ['reasoning', 'is_question'],
                },
            },
        }

        max_retries = 5
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                async with self._session.post(
                    self._url, json=payload, timeout=ClientTimeout(total=20)
                ) as resp:
                    if resp.status == 503:
                        error = await resp.json()
                        raise ServerTimeoutError(f'Gemini API 503: {error}')
                    elif resp.status != 200:
                        error = await resp.json()
                        logger.error(f'Gemini API {resp.status}: {error}')
                        logger.warning('Finds the comment helpful.')
                        return True

                    result = await resp.json()

                    if 'candidates' not in result:
                        logger.error(
                            f'Gemini API Error, no candidates: {result}'
                        )
                        logger.warning('Finds the comment helpful.')
                        return True

                    content_text = result['candidates'][0]['content']['parts'][
                        0
                    ]['text']
                    data = json.loads(content_text)

                    ai_reasoning = data.get(
                        'reasoning', 'No reasoning provided'
                    )

                    usage = result.get('usageMetadata', {})
                    in_tok = usage.get('promptTokenCount', 0)
                    out_tok = usage.get('candidatesTokenCount', 0)
                    _sum_tok = in_tok + out_tok
                    logger.info(
                        f'{_sum_tok=}, {in_tok=}, {out_tok=}, {clean_text=},'
                        f' {ai_reasoning=}'
                    )
                    ai_evaluation = bool(data.get('is_question', True))
                    logger.info(f'{ai_evaluation=}')

                    return ai_evaluation

            except (
                TimeoutError,
                ServerTimeoutError,
                ClientOSError,
                ClientPayloadError,
            ) as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    logger.warning(
                        f'Gemini API timeout/connection error'
                        f' (attempt {attempt + 1}/{max_retries}): '
                        f'{type(e).__name__}. Retrying in {delay}s...'
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f'Gemini evaluation failed after {max_retries}'
                        f' attempts for text="{clean_text[:50]}...":'
                        f' {type(e).__name__}: {e}'
                    )
                    return True

            except Exception as e:
                logger.error(
                    f'Gemini evaluation failed for'
                    f' text="{clean_text[:50]}...": {type(e).__name__}: {e}'
                )
                return True
        return True

    @staticmethod
    async def _clean_html_tags(raw_html: str) -> str:
        if not raw_html:
            return ''

        code_blocks = {}

        def save_code(match: re.Match[str]) -> str:
            block_id_str = f'__CODE_BLOCK_{len(code_blocks)}__'
            code_blocks[block_id_str] = match.group(0)
            return block_id_str

        pattern = re.compile(r'<pre><code>(.*?)</code></pre>', re.DOTALL)
        temp_text = pattern.sub(save_code, raw_html)

        clean_text = re.sub(r'<[^>]+>', '', temp_text)

        for block_id, code_block in code_blocks.items():
            clean_text = clean_text.replace(block_id, code_block)

        clean_text = html.unescape(clean_text)

        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
