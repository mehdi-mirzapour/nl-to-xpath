from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import services.sentence_segmentor.app as sent_router
import services.task_mapper.app as task_router
import services.xpath_extractor.app as xpath_router
import services.rag_html.app  as html_cut_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myfrontend.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(sent_router.router)
app.include_router(task_router.router)
app.include_router(xpath_router.router)
app.include_router(html_cut_router.router)

