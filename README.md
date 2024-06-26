How to start:
1. `docker compose up`
2. `docker exec -it web python manage.py migrate`
3. open `127.0.0.1`

Creating admin: `docker exec -it web python manage.py createsuperuser --username admin --email admin@example.com`

Available endpoints:
- `GET` `/api/menu/`
- `GET` `/api/cart/`
- `POST` `/api/cart/add/`
- `POST` `/api/cart/remove/`
- `POST` `/api/cart/checkout/`
- `GET` `/api/orders/`

Running tests:
`docker exec -it web python manage.py test`