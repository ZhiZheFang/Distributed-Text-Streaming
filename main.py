from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request, Response
from uuid import uuid4
from streamer import Streamer

# Create fastAPI server
app = FastAPI()

def initCookie(response: Response, session_id: str = "", urlId: int = 0, offset: int = 0):
    # Generate a new session ID if not found in cookies
    response.set_cookie(key="session_id", value=session_id)
    response.set_cookie(key="url_id", value=urlId)
    response.set_cookie(key="offset", value=offset)
    print('created new cookie with session_id=' + session_id)

@app.get("/stream")
async def stream_text(request: Request, response: Response, urlId: int = 0):
    """
    This endpoint streams text data asynchronously.
    It uses FastAPI's StreamingResponse, which supports asynchronous generators.
    """

    session_id = request.cookies.get("session_id")
    offset = 0

    if session_id is None:
        # initialize cookie to store streaming status
        session_id = str(uuid4())
        initCookie(response, session_id, urlId, offset)
    else:
        # identified cookie, which means there was a previous interrupted session need to recover
        if urlId == request.cookies.get("url_id"):
            offset = request.cookies.get("offset")
            if offset is None:
                offset = 0

    # start streamming
    streamer = Streamer()
    return StreamingResponse(streamer.start_stream(response, urlId, offset, session_id), media_type="text/plain")