# Social Media Api

A Django REST Framework API for creating posts and add comments, likes or dislikes.

---  

## 📦 Features

- 👤 Registration
- 🔐 JWT authentication
- 🔍  Search for users by email, number of followers, written posts, or reactions on a post
- 👥 Users can follow and unfollow other users
- ✔️ Users can create posts with a possibility to schedule post creation
- 🔍 Users can search for posts by author or tag
- ⚡ Users can react react to other users' posts
- 📝 write a comment
- 📄 Interactive API documentation with Swagger & ReDoc    
- ⚙️ Admin dashboard for data management    

---  

## 🚀 Tech Stack

- Python 3.12+    
- Django 5.2+
- Django REST Framework    3.16+
- PostgreSQL 
- drf-spectacular for API docs    
- Render.com for deployment    

---  

## ⚙️ Local Setup

### 1. Clone the project

```bash
git clone https://github.com/MykolaMazh/Social-Media-API.git

cd Social-Media-API/ 
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv 
source venv/bin/activate # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

settings.py splitted into prod.py and dev.py so

 for development `.env` 

```ini
SECRET_KEY=your_secret_key
DJANGO_SETTINGS_MODULE=social_media_api.settings.dev
```

fo production `.env`

```ini
SECRET_KEY=your_secret_key
DJANGO_SETTINGS_MODULE=social_media_api.settings.prod

POSTGRES_DB_PORT=5432
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_password
POSTGRES_HOST=db_host
POSTGRES_DB=db_name

PRODUCTION_DOMAIN=your_production_domain
```

### 5. Run migrations

```bash
python manage.py migrate  
```

### 6. Create a superuser (optional)

```bash
python manage.py createsuperuser  
```

### 7. Run the server

```bash
python manage.py runserver
```

## 🔑 Authentication

This project uses **JWT authentication** via `/api/v1/user/token/` after registration on `/api/v1/user/register/`.


## 📄 API Documentation

- Documentation for endpoints is provided by Swagger UI using `drf-spectacular`: url -`/api/doc/swagger/`
