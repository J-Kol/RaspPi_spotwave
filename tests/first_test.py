#import sys
#from pathlib import Path
#
#sys.path.append(str(Path(__file__).resolve().parent.parent))
#
#import pytest
#from main import example_func
#
#@pytest.mark.asyncio
#async def fastapi(): #to activate: test_fastapi
#    result = await example_func(7, "Sam")
#    assert result == {"name": "Sam", "id": 7}
#