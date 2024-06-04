import pytest
from unittest.mock import patch, AsyncMock
from frontend.app.api import get_response

@pytest.mark.asyncio
@patch('frontend.app.api.aiohttp.ClientSession.get', new_callable=AsyncMock)
async def test_get_response_success(mock_get):
    mock_get.return_value.__aenter__.return_value.status = 200
    mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value={'key': 'value'})
    
    response = await get_response('http://example.com')
    assert response == {'key': 'value'}

@pytest.mark.asyncio
@patch('frontend.app.api.aiohttp.ClientSession.get', new_callable=AsyncMock)
async def test_get_response_failure(mock_get):
    mock_get.return_value.__aenter__.return_value.status = 404
    
    response = await get_response('http://example.com')
    assert response == {'error': 'Bad request'}
