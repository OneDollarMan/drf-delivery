How to start:
1. `docker compose build`
2. `docker compose up`
3. `docker exec -it web python manage.py migrate`

Available endpoints:
- `GET` `/api/menu/`
- `GET` `/api/cart/`
- `POST` `/api/cart/add/`
- `POST` `/api/cart/remove/`
- `POST` `/api/cart/checkout/`
- `GET` `/api/orders/`

Running tests:
`docker exec -it web python manage.py test`