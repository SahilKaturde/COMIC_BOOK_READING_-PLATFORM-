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

## 🗄️ Database Architecture & Schema Explanation (A to Z Details)

The application leverages a robust relational PostgreSQL database comprising 7 core tables. Below is the complete "biodata" and relationship mapping for every entity in the system, detailing all types, constraints, defaults, and architectural decisions.

### 1. `admin` (System Administrators)
* **Purpose:** Stores credentials for superusers who manage the platform.
* **Columns:**
  * `id` (BIGINT, Primary Key): Auto-incrementing unique identifier.
  * `name` (VARCHAR 100): Administrator's full name.
  * `email` (VARCHAR 150, UNIQUE): Login email, guaranteed unique.
  * `password` (TEXT): Hashed access credential.
  * `created_at` (TIMESTAMPTZ): Automatically records creation time.

### 2. `publisher` (Content Creators)
* **Purpose:** Represents users authorized to create and upload comic books.
* **Columns:**
  * `id` (BIGINT, Primary Key): Auto-incrementing unique identifier.
  * `name` (VARCHAR 100): Publisher's display name or studio name.
  * `email` (VARCHAR 150, UNIQUE): Login email.
  * `password` (TEXT): Hashed access credential.
  * `logo_url` (TEXT): Optional path to the publisher's avatar/logo.
  * `created_at` (TIMESTAMPTZ): Account creation timestamp.
* **Relationships:**
  * **One-to-Many** with `comic` (A publisher can own many comics).

### 3. `reader` (End Users)
* **Purpose:** Regular users who consume the comic content.
* **Columns:**
  * `id` (BIGINT, Primary Key): Auto-incrementing unique identifier.
  * `name` (VARCHAR 100): Reader's display name.
  * `email` (VARCHAR 150, UNIQUE): Login email.
  * `password` (TEXT): Hashed access credential.
  * `created_at` (TIMESTAMPTZ): Account creation timestamp.
* **Relationships:**
  * **One-to-Many** with `reading_progress` (A reader can track progress across many chapters).

### 4. `comic` (The Core Publication)
* **Purpose:** The central catalog entity representing a unique series/book.
* **Columns:**
  * `id` (BIGINT, Primary Key): Auto-incrementing unique identifier.
  * `publisher_id` (BIGINT, Foreign Key): Links cleanly to `publisher.id`.
  * `title` (TEXT): The name of the comic.
  * `description` (TEXT): Synopsis or summary.
  * `genre` (VARCHAR 80): Categorization metadata.
  * `poster_url` (TEXT): Path/URL to the cover image.
  * `status` (ENUM `comic_status`): Restricted to either `'draft'` or `'published'`. Defaults to `'draft'`.
  * `created_at` (TIMESTAMPTZ): Timestamp of title creation.
* **Constraints & Indexes:**
  * `ON DELETE CASCADE` on `publisher_id`: If a publisher is deleted, their comics vanish automatically.
  * **Indexes:** `idx_comic_publisher` and `idx_comic_status` for rapid querying and filtering.
* **Relationships:**
  * **One-to-Many** with `chapter` (A comic has many chapters).

### 5. `chapter` (Episodes / Issues)
* **Purpose:** Represents individual episodic releases belonging to a `comic`.
* **Columns:**
  * `id` (BIGINT, Primary Key): Auto-incrementing unique identifier.
  * `comic_id` (BIGINT, Foreign Key): Links directly to `comic.id`.
  * `chapter_number` (INT): The sequential order of the chapter.
  * `title` (TEXT): Optional chapter name (e.g., "The Awakening").
  * `published_at` (TIMESTAMPTZ): Release timestamp.
* **Constraints & Indexes:**
  * `ON DELETE CASCADE` on `comic_id`: Deleting a comic strips all its chapters.
  * **Composite UNIQUE Constraint** on `(comic_id, chapter_number)`: Strictly prevents accidental duplicate numbering (e.g., two "Chapter 5"s in the same comic).
  * **Index:** `idx_chapter_comic` for fast joins.
* **Relationships:**
  * **One-to-Many** with `page` (A chapter has many pages).
  * **One-to-Many** with `reading_progress` (A chapter is tracked by many readers).

### 6. `page` (Image Assets)
* **Purpose:** Stores the exact sequence of images for the reader viewer.
* **Columns:**
  * `id` (BIGINT, Primary Key): Auto-incrementing unique identifier.
  * `chapter_id` (BIGINT, Foreign Key): Links to `chapter.id`.
  * `page_number` (INT): Defines the visual reading order.
  * `image_url` (TEXT): File path or URL to the raw image panel.
* **Constraints & Indexes:**
  * `ON DELETE CASCADE` on `chapter_id`: Deleting a chapter purges its images.
  * **Composite UNIQUE Constraint** on `(chapter_id, page_number)`: Ensures a single strict layout sequence (preventing duplicate "Page 1"s).
  * **Index:** `idx_page_chapter` for lightning-fast sequential fetching.

### 7. `reading_progress` (Junction / State Engine)
* **Purpose:** Tracks where a `reader` left off inside a specific `chapter`.
* **Columns:**
  * `id` (BIGINT, Primary Key): Auto-incrementing unique identifier.
  * `reader_id` (BIGINT, Foreign Key): Links to `reader.id`.
  * `chapter_id` (BIGINT, Foreign Key): Links to `chapter.id`.
  * `last_page` (INT): Remembers the last viewed page integer. Defaults to `1`.
  * `completed` (BOOLEAN): Flag flipped to `TRUE` when they reach the final page. Defaults to `FALSE`.
  * `updated_at` (TIMESTAMPTZ): Real-time timestamp of their last activity.
* **Constraints & Indexes:**
  * `ON DELETE CASCADE` on `reader_id` and `chapter_id`: If a user leaves or a chapter is removed, the progress table trims obsolete data instantly.
  * **Composite UNIQUE Constraint** on `(reader_id, chapter_id)`: Limits to exactly ONE progress record per pair, avoiding duplicate history states.
  * **Index:** `idx_progress_reader` to quickly load a reader's entire history dashboard.

## 📁 Project Folder Structure

A well-organized directory structure separates concerns and keeps the application scalable:

```text
Comic_Book_Reading_Platform/
├── app/                  # Main application package
│   ├── queries/          # SQL queries and database interaction functions
│   ├── routes/           # Flask blueprint routing and controllers
│   ├── services/         # Business logic and complex operations
│   ├── static/           # Static assets like CSS, JS, and logos
│   ├── templates/        # HTML templates for rendering views
│   ├── utils/            # Helper functions and utilities
│   ├── screenshot/       # Contains screenshots for documentation
│   ├── db.py             # Database connection setup
│   └── __init__.py       # Application factory and initialization
├── Data/                 # File storage
│   └── comics/           # Uploaded comic pages and covers
├── docs/                 # Documentation and database schema SQL
├── insert_admin.py       # Helper script to create an initial admin
├── pyproject.toml        # Project definitions and dependencies
├── run.py                # Waitress/development server runner
└── main.py               # Application entry point alternative
```

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
