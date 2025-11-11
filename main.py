import uvicorn
from fastapi import FastAPI

from use_cases.api.Books import router_books


app = FastAPI(title='Book API')

app.include_router(router_books)

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)