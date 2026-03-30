from fastapi.templating import Jinja2Templates
from pyfastic.config import settings

# Eén centrale plek voor je template engine
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)