# EBS Python Internship 
## Django Rest Framework API for managing Tasks

This repository contains an application used to manage tasks (create, assign and  timelog ) 
using http based API call methods (GET,POST, PUT, DELETE, and PATCH)


## Requirements:
- [Python](https://www.python.org/) (9.11)
- [Django](https://pypi.org/project/Django/3.2.21/) (3.2.16)
- [Docker](https://www.docker.com/products/docker-desktop/) (24.0.5)

## Setup
Once you cloned the repository create a `.env` file based on `.env-example`.
This project can be easily deployed using `docker compose up`.

You can run this application without docker, just configure the virtual environment and install the requirements : `pip install -r requirements.txt`. Note: A postgres and redis server is required to run django.

## Usage
The Rest API Endpoints can be called via HTTP methods.  
Almost every endpoint requires authorization, so don't forget to add `"Authorization: Bearer {YOUR_TOKEN}"` in headers.

### Here are some examples

| Endpoint                      | Result                                             | Authorization <br/> required |
|-------------------------------|----------------------------------------------------|------------------------------|
| `POST \| /user/login/`        | If the credentials are valid return jwt Token pair | no                           |
| `POST \| /user/register/`     | Create a new user                                  | no                           |
| `POST \| /user/token/refresh` | Generate a new access token using refresh token    | no                           |
| `POST \| /tasks/`             | Create a new task                                  | yes                          |
| `GET  \| /tasks/`             | Get a lists of all tasks, paginated                | yes                          |
| `DELETE \| /tasks/{id}/`      | Delete task by id                                  | yes                          |

### More can be found at `localhost:8000` via browser. 




## Documentation 

- [Django rest framework](https://www.django-rest-framework.org/)  
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)  
- [Django-redis](https://django-redis-cache.readthedocs.io/en/latest/)   

