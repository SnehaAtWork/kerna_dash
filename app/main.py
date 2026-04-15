from app.core.exceptions import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)