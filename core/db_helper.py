from sqlalchemy.orm import Session
from core.models.user import User  # Импорт модели пользователя, которая описана у вас в проекте
from core.db import get_db, SessionLocal  # Получение сессии базы данных


# Функция для обновления статистики пользователя
def update_user_stats(tg_id: int, wins: int, losses: int, draws: int, db: Session):
    # Ищем пользователя по tg_id
    user = db.query(User).filter(User.tg_id == tg_id).first()

    if user:
        # Если пользователь найден, обновляем его статистику
        user.wins += wins
        user.losses += losses
        user.draws += draws
    else:
        # Если пользователь не найден, создаем новую запись в базе
        user = User(tg_id=tg_id, wins=wins, losses=losses, draws=draws)
        db.add(user)  # Добавляем нового пользователя в сессию
    db.commit()  # Сохраняем изменения в базе данных


# Функция для получения сессии базы данных
def get_dbs():
    db = SessionLocal()  # Создаем сессию для взаимодействия с базой данных (SessionLocal должен быть настроен)
    try:
        yield db  # Возвращаем сессию для использования в других функциях
    finally:
        db.close()  # Закрываем сессию после завершения работы с ней
