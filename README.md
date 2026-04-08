# Comic Book Reading Platform

A detailed web application for reading, publishing, and managing comic books online. Built with Flask and PostgreSQL.

## 🚀 Features & User Roles

The platform supports three distinct user roles:

1. **Reader**: 
   - Browse and discover published comics.
   - Read comics chapter by chapter.
2. **Publisher**: 
   - Create new comic titles.
   - Upload covers and add multiple chapters.
   - Delete/Edit their own content.
3. **Admin**:
   - Oversee the entire catalog of comics.
   - Delete inappropriate or problematic comics platform-wide.

## 🛠️ Technologies Used

- **Backend**: Python, Flask
- **Database**: PostgreSQL (`psycopg` v3)
- **Image Processing**: Pillow (PIL)
- **Environment Management**: `python-dotenv`
- **Package Management**: `uv` / `pip`

## 📸 Screenshots

*(Images are stored in the `app/screenshot/` directory)*

### Publisher Dashboard
![Publisher Page](app/screenshot/publisher_page.png)

### Edit Comic Page
![Edit Page](app/screenshot/edit_page.png)

### Admin Dashboard
![Admin Page](app/screenshot/admin_page.png)

## ⚙️ How to Run Locally

### 1. Requirements
- Python 3.12+
- PostgreSQL Server installed and running

### 2. Database Setup
1. Open your PostgreSQL console (using `psql` or pgAdmin).
2. Execute the schema to table creation. You can run the provided SQL script:
   ```bash
   psql -U postgres -f docs/comic_platform_database.sql
   ```
3. Update your `.env` file (create one if not present in the project root) with your database credentials. For example:
   ```env
   DB_HOST=localhost
   DB_USER=postgres
   DB_PASSWORD=yourpassword
   DB_NAME=postgres
   ```

### 3. Install Dependencies
You can install the dependencies via `pip` or using `uv` (recommended):
```bash
# Using uv (fastest)
uv sync

# Or using standard pip
pip install -r app/requirements.txt
```

### 4. Create an Admin User (Optional)
To setup the initial admin account, simply execute:
```bash
python insert_admin.py
```

### 5. Start the Server
Run the development server natively:
```bash
python run.py
```
*Alternatively, you can just run `python main.py`.*
Access the application locally at: **http://127.0.0.1:5000**.

---

## 🔗 Endpoints Reference (Exam Revision Guide)

Below is a detailed list of all routes available in the system. Use this to quickly revise what each block of code on the backend accomplishes.

### 🔐 Authentication Routes (`auth_routes.py`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/register` | Renders the HTML registration form. |
| **POST** | `/register` | Handles form submission to create a new user (Reader, Publisher, or Admin). |
| **GET** | `/login` | Renders the login HTML page. |
| **POST** | `/login` | Authenticates user credentials against the database and creates a session. |
| **GET** | `/logout` | Clears local sessions and logs the user out. |
| **GET** | `/home` | Redirects mapped logic: takes a logged-in user to their respective dashboard (`reader_home`, `publisher_home`, or `admin_home`) based on their assigned role. |

### 📚 Reader & Publisher Routes (`comic_routes.py`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/reader_home` | Main library view where readers browse thumbnails of available comics. |
| **GET** | `/read/<comic_id>` | Specific comic overview (cover, title, description, and list of chapters). |
| **GET** | `/read/<comic_id>/<chapter_number>` | Shows the image files associated with a specific chapter for inline reading. |
| **GET** | `/publisher_home` | Publisher's centralized dashboard showing exactly what comics they have published. |
| **POST** | `/publisher/create` | Receives metadata to create and insert a new comic title. |
| **GET** | `/publisher/edit/<comic_id>` | Renders a pre-filled form allowing publishers to review and edit comic metadata. |
| **POST** | `/publisher/edit/<comic_id>` | Commits the updated metadata changes (such as title, summary) to the database. |
| **POST** | `/publisher/delete/<comic_id>` | Permanently removes a publisher's own comic and its chapters. |
| **GET** | `/publisher/comic/<comic_id>/chapters` | Shows the granular list of all chapters for a specific comic created by the publisher. |
| **POST** | `/publisher/comic/<comic_id>/chapter/create` | Inserts a new empty chapter row mapped to a given comic. |
| **POST** | `/publisher/comic/<comic_id>/chapter/<chapter_num>/upload` | High-level method for handling multiple image byte uploads and mapping them to a specific chapter. |
| **POST** | `/publisher/chapter/<chapter_id>/delete` | Granular deletion of a specific chapter. |

### 🛡️ Admin Routes (`admin_routes.py`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/admin_home` | Superuser overview displaying analytics, users, or platform-wide catalogs. |
| **POST** | `/admin/delete_comic/<comic_id>` | Enables a site administrator to forcefully censor or remove comics that bypass platform rules. |

---
**Best of luck with your exams! You've got this.**
