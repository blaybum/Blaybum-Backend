from app.repositories.base_repository import BaseRepository
from app.models import Concentration

class ConcentrationRepository(BaseRepository[Concentration]):
    def __init__(self):
        super().__init__(Concentration)

concentration_repo = ConcentrationRepository()
