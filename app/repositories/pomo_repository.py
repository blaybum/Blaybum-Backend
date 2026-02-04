from app.repositories.base_repository import BaseRepository
from app.models.models import Pomo

class PomoRepository(BaseRepository[Pomo]):
    pass
pomo_repo = PomoRepository()