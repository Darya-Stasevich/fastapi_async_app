import uvicorn
from fastapi import FastAPI

from storage_app.authentication.views import authentication_views
from storage_app.users.views import api_users
from storage_app.articles.views import api_articles

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication_views.router)
app.include_router(api_users.router)
app.include_router(api_articles.router)

if __name__ == "__main__":
    uvicorn.run('main:app', port=8000, reload=True)
