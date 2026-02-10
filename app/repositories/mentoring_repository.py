from app.repositories.base_repository import BaseRepository
from app.models import Mentoring

class MentoringRepository(BaseRepository[Mentoring]):
  def __init__(self):
    super().__init__(Mentoring)

mentoring_repo = MentoringRepository()