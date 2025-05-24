sudo docker-compose up --build
docker exec -it barter_web_server python manage.py migrate
sudo docker exec -it barter_web_server python manage.py createsuperuser

