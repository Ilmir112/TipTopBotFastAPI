from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from zimaApp.database import async_session_maker
from zimaApp.main import app
from zimaApp.norms.dao import NormDAO
from zimaApp.norms.models import NormsWork
from sqlalchemy.orm import Session


@app.get("/admin/norms/{norm_id}/view", response_class=HTMLResponse)
async def view_norm(norm_id: int):

        norm = NormDAO.find_one_or_none(id=norm_id)
        if not norm:
            raise HTTPException(status_code=404, detail="Запись не найдена")

        # Создайте HTML-шаблон прямо здесь или используйте шаблонизатор (например, Jinja2)
        html_content = f"""
        <html>
            <head>
                <title>Подробнее о NormsWork {norm_id}</title>
            </head>
            <body>
                <h1>Детали NormsWork {norm_id}</h1>
                <ul>
                    <li>Поле 1: {norm.field1}</li>
                    <li>Поле 2: {norm.field2}</li>
                    <!-- добавьте нужные поля -->
                </ul>
                <a href="/admin/norms">Назад к списку</a>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)