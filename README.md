# Запуск [проекта](https://github.com/netology-code/py-homeworks-web/tree/new/2.4-celery)
Из папки с проектом перейти в директорию c конфигурацией docker-compose

```bash
cd ./deploy/
```
Запустить проект
```bash
docker compose up -d --build
```

## Работа с проектом
|URL|Метод|Действие|
|:-:|:-:|:-:|
|`/upscale`| **POST** | Передать изображения для апскейлинга |
|`/tasks/<task_id>`| **GET** | Получить статус выполняемой задачи |
|`/processed/<task_id>`| **GET** | Получить результат |
