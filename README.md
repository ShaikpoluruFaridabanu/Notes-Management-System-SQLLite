# Notes Management System (Flask + MySQL)

## Run
1. `pip install -r requirements.txt`
2. Run `schema.sql` in MySQL (`mysql -u root -p < schema.sql`)
3. Set your MySQL password in `DB_CONFIG` inside `app.py`
4. `python app.py` → open http://127.0.0.1:5000

## Routes
| Operation | Route |
|---|---|
| Register / Login / Forgot / Logout | /register, /login, /forgot, /logout |
| Create | /addnote |
| Read all | /viewall |
| Read one | /viewnotes/<id> |
| Update | /updatenote/<id> |
| Delete | /deletenote/<id> (POST) |
