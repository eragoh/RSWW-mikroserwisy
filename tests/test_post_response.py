import pytest
from unittest.mock import patch, AsyncMock
from frontend.app.api import post_response

@pytest.mark.asyncio
@patch('frontend.app.api.aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_post_response_success(mock_post):
    mock_post.return_value.__aenter__.return_value.status = 200
    mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value={'key': 'value'})

    response = await post_response('http://example.com', data={'key': 'value'})
    assert response == {'key': 'value'}

@pytest.mark.asyncio
@patch('frontend.app.api.aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_post_response_failure(mock_post):
    mock_post.return_value.__aenter__.return_value.status = 404

    response = await post_response('http://example.com', data={'key': 'value'})
    assert response == {'error': 'Bad request'}
