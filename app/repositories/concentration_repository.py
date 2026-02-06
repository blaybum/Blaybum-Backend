from app.repositories.base_repository import BaseRepository
from app.models import Concentration

class ConcentrationRepository(BaseRepository[Concentration]):
    pass

concentration_repo = ConcentrationRepository()
