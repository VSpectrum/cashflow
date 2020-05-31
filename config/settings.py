from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
      

## SETTINGS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)  # allowing api to be publicly accessible by anyone (domain-name restrictions to be applied here)
templates = Jinja2Templates(directory="templates")
