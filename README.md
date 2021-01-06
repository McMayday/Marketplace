## Marketplace


### Запуск бекенда

#### Запуск бд
```bash
docker network create local-apps 
```

```bash
docker run --name local-pg12 \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_INITDB_ARGS="--locale=C.UTF-8" \
    -v ~/Documents/storedata/pg-data:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network="local-apps" \
    --restart always \
    -d postgres:12.0-alpine
```

```bash
docker exec -it local-pg12 psql -U postgres
```

#### Для выполенние асинхронных задач используется Celery. Требуется брокер и бекенд в виде реббита

Можно установать в докере:

```bash
docker run --name local-rabbit-host \
    -v ~/Documents/storedata/rabbit-data/:/var/lib/rabbitmq \
    -p 5672:5672 \
    -p 15672:15672 \
    --network="local-apps" \
    --restart always \
    -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password \
    -d rabbitmq:3.8.9-management
```

#### Настройки 

```bash
cp sample.env .env
```

#### Зависимости

***Нужен Python 3.8***

**Создаем и активируем виртуальное окружение**

```bash
pip install -r requirements.txt
```


#### Запуск севера

```bash
python manage.py migrate
```


```bash
python manage.py createsuperuser
```

```bash
python manage.py runserver
```

```bash
docker-compose -f docker-compose-workers.yml up -d --scale regular_workers=1 --timeout 50
```
