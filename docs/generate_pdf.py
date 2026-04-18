"""
generate_pdf.py  --  Clean documentation PDF using fpdf2 with Courier font
Run:  uv run docs/generate_pdf.py
"""

from fpdf import FPDF
from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
OUT  = BASE / "docs" / "documentation_1.pdf"

# ── Colours ─────────────────────────────────────────────────────────────
C_DARK   = (20, 20, 25)      # very dark
C_MID    = (60, 60, 70)      # subtle heading accent
C_BODY   = (30, 30, 35)      # body text
C_LIGHT  = (245, 245, 245)   # light background fills
C_LINE   = (150, 150, 160)   # separator lines
C_TH     = (40, 40, 45)      # table header bg
C_TH_TXT = (255, 255, 255)   # table header text
C_TR_ALT = (248, 248, 250)   # table alt-row

# ── Custom PDF class ────────────────────────────────────────────────────
class DocPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return  # cover page has no header
        self.set_font("Courier", "I", 9)
        self.set_text_color(*C_LINE)
        self.cell(0, 6, "COMIC BOOK READING PLATFORM :: PROJECT DOCUMENTATION", align="C")
        self.ln(10)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("Courier", "I", 9)
        self.set_text_color(*C_LINE)
        self.cell(0, 10, f"- {self.page_no() - 1} -", align="C")

    # ── reusable helpers ────────────────────────────────────────────────
    def section_title(self, num, title):
        """Big section heading with an accent bar."""
        self.set_font("Courier", "B", 16)
        self.set_text_color(*C_DARK)
        self.cell(0, 12, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        # accent bar
        self.set_draw_color(*C_DARK)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    def sub_heading(self, text):
        self.set_x(self.l_margin)
        self.set_font("Courier", "B", 11)
        self.set_text_color(*C_MID)
        self.cell(0, 8, f"> {text}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body(self, text):
        self.set_x(self.l_margin)
        self.set_font("Courier", "", 10)
        self.set_text_color(*C_BODY)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 5.5, text)
        self.ln(1)

    def bullet(self, text):
        self.set_x(self.l_margin)
        self.set_font("Courier", "", 10)
        self.set_text_color(*C_BODY)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 5.5, f"  *  {text}")

    def key_value(self, key, val, kw=65):
        """Print a key : value row."""
        self.set_font("Courier", "B", 10)
        self.set_text_color(*C_MID)
        self.cell(kw, 7, key)
        self.set_font("Courier", "", 10)
        self.set_text_color(*C_BODY)
        self.cell(0, 7, val, new_x="LMARGIN", new_y="NEXT")

    def draw_table(self, headers, rows, col_widths=None):
        """Draw a bordered table with header highlight and alt-row shading."""
        usable = self.w - self.l_margin - self.r_margin
        if col_widths is None:
            col_widths = [usable / len(headers)] * len(headers)
        rh = 7  # row height

        # header
        self.set_font("Courier", "B", 9)
        self.set_fill_color(*C_TH)
        self.set_text_color(*C_TH_TXT)
        self.set_draw_color(*C_LINE)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], rh, h, border=1, fill=True, align="C")
        self.ln()

        # rows
        self.set_font("Courier", "", 9)
        self.set_text_color(*C_BODY)
        for ri, row in enumerate(rows):
            if ri % 2 == 1:
                self.set_fill_color(*C_TR_ALT)
                fill = True
            else:
                fill = False
            for i, cell in enumerate(row):
                self.cell(col_widths[i], rh, cell, border=1, fill=fill)
            self.ln()
        self.ln(4)

    def thin_line(self):
        self.set_draw_color(*C_LINE)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def add_image_page(self, section_num, section_title, img_path, subtitle=None, orientation="P", show_section=True):
        """Adds a new page with an image and titles."""
        self.add_page(orientation=orientation)
        if show_section:
            self.section_title(section_num, section_title)
        
        if subtitle:
            self.sub_heading(subtitle)
        
        if not img_path.exists():
            self.body(f"[Image not found at {img_path}]")
            return

        from PIL import Image
        try:
            with Image.open(img_path) as im:
                iw, ih = im.size
            
            usable_w = self.w - self.l_margin - self.r_margin
            usable_h = self.h - self.get_y() - self.b_margin - 10 
            
            scale = min(usable_w / iw, usable_h / ih, 1.0)
            new_w = iw * scale
            new_h = ih * scale
            
            x_offset = self.l_margin + (usable_w - new_w) / 2
            self.image(str(img_path), x=x_offset, y=self.get_y(), w=new_w, h=new_h)
            self.ln(new_h + 5)
        except Exception as e:
            self.body(f"[Error loading image: {e}]")


# ═══════════════════════════════════════════════════════════════════════
#  BUILD THE PDF
# ═══════════════════════════════════════════════════════════════════════
def build():
    pdf = DocPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)

    # ── PAGE 1 — COVER ──────────────────────────────────────────────────
    pdf.add_page()
    pdf.ln(50)
    # title block
    pdf.set_font("Courier", "B", 24)
    pdf.set_text_color(*C_DARK)
    pdf.cell(0, 14, "COMIC BOOK READING PLATFORM", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", "B", 14)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 10, "=== PROJECT DOCUMENTATION ===", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    # accent line
    cx = pdf.w / 2
    pdf.set_draw_color(*C_DARK)
    pdf.set_line_width(1.5)
    pdf.line(cx - 50, pdf.get_y(), cx + 50, pdf.get_y())
    pdf.ln(20)

    # meta info
    meta = [
        ("Member One",         "Anuj Rakesh Rajput"),
        ("Member Two",         "Sahil Dinkar Katurde"),
        ("Roll No (Member 1)", "SY_CS_5"),
        ("Roll No (Member 2)", "SY_CS_93"),
        ("Class",              "SYBSc (CS)"),
        ("Institute",          "Pune Vidyarthi Griha's College of Science & Commerce"),
        ("Academic Year",      "2025-2026"),
        ("Guide",              "Priyanka Khutwad Ma'am"),
        ("Department",         "Computer Science"),
    ]
    
    # center the meta block slightly
    pdf.set_left_margin(30)
    for k, v in meta:
        pdf.key_value(f"{k}", str(v), kw=65)
    pdf.set_left_margin(20) # restore
    
    pdf.ln(30)
    pdf.set_font("Courier", "I", 10)
    pdf.set_text_color(*C_LINE)
    pdf.cell(0, 8, "Pune Vidyarthi Griha's College of Science & Commerce", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Department of Computer Science  |  2025-2026", align="C")

    # ── PAGE 2 — PROBLEM DEFINITION ─────────────────────────────────────
    pdf.add_page()
    pdf.section_title(2, "PROBLEM DEFINITION")

    pdf.sub_heading("Problem Statement")
    pdf.body(
        "There is no simple, dedicated platform where small comic publishers "
        "can directly publish their work and readers can read it online "
        "without relying on third-party marketplaces."
    )

    pdf.sub_heading("Existing Problems")
    for prob in [
        "Publishers have no easy way to upload chapter-wise comics.",
        "Readers cannot track their reading progress.",
        "No role-based access for admin, publisher, and reader.",
        "No clean reading interface for comic pages.",
    ]:
        pdf.bullet(prob)
    pdf.ln(2)

    pdf.sub_heading("Objective")
    pdf.body("To build a lightweight web platform where:")
    for obj in [
        "Publishers can register, upload comics and chapters.",
        "Readers can browse, read comics, and track their progress.",
        "Admin can manage and monitor all users and content.",
    ]:
        pdf.bullet(obj)
    pdf.ln(2)

    pdf.sub_heading("Scope")
    for s in [
        "Role-based login system (Admin / Publisher / Reader).",
        "Comic upload with chapter and page management.",
        "Reading progress tracking per reader per chapter.",
        "Admin dashboard for user and content oversight.",
    ]:
        pdf.bullet(s)

    # ── PAGE 3 — REQUIREMENT SPECIFICATION ──────────────────────────────
    pdf.add_page()
    pdf.section_title(3, "REQUIREMENT SPECIFICATION")

    pdf.sub_heading("Hardware Requirements")
    pdf.draw_table(
        ["Component", "Specification"],
        [
            ["Processor", "Intel Core i3 or above"],
            ["RAM", "Minimum 4 GB"],
            ["Storage", "Minimum 10 GB free disk space"],
            ["Network", "Internet connection required"],
        ],
        col_widths=[40, 130],
    )

    pdf.sub_heading("Software Requirements")
    pdf.draw_table(
        ["Software", "Details"],
        [
            ["OS", "Windows 10 / Ubuntu 20.04+"],
            ["Language", "Python 3.12"],
            ["Framework", "Flask (Python Web Framework)"],
            ["Database", "PostgreSQL"],
            ["Frontend", "HTML, CSS, JavaScript"],
            ["Tools", "VS Code, pgAdmin / psql, Git"],
        ],
        col_widths=[40, 130],
    )

    pdf.sub_heading("Functional Requirements")
    funcs = [
        "User registration and login with role selection.",
        "Publisher can create, edit, and delete comics.",
        "Publisher can upload chapters and pages per chapter.",
        "Reader can browse published comics by genre.",
        "Reader can read comics page by page (full-screen mode).",
        "Reading progress is saved automatically.",
        "Admin can view all users, comics, and manage platform.",
    ]
    for i, f in enumerate(funcs, 1):
        pdf.body(f"[{i}] {f}")

    pdf.ln(2)
    pdf.sub_heading("Non-Functional Requirements")
    for i, nf in enumerate([
        "Fast page load for comic images.",
        "Responsive UI for desktop browsers.",
        "Data consistency using PostgreSQL foreign keys.",
    ], 1):
        pdf.body(f"[{i}] {nf}")

    # ── PAGE 4 — PROPOSED SYSTEM ────────────────────────────────────────
    pdf.add_page()
    pdf.section_title(4, "PROPOSED SYSTEM")

    pdf.sub_heading("Overview")
    pdf.body(
        "The proposed system is a Flask-based multi-role web application "
        "connected to a PostgreSQL database. It follows MVC architecture."
    )
    pdf.ln(2)

    modules = [
        ("A", "Authentication Module", [
            "Register as Admin, Publisher, or Reader.",
            "Login with email and password.",
            "Role-based redirect after login.",
        ]),
        ("B", "Admin Module", [
            "View all registered publishers and readers.",
            "View all comics on the platform.",
            "Manage platform content.",
        ]),
        ("C", "Publisher Module", [
            "Dashboard to manage own comics.",
            "Create new comic (title, genre, description, poster).",
            "Add chapters to a comic.",
            "Upload pages (images) per chapter.",
            "Edit or delete comics.",
        ]),
        ("D", "Reader Module", [
            "Browse all published comics.",
            "View comic details and chapters.",
            "Read comics in full-screen reader mode.",
            "Progress is saved per chapter automatically.",
        ]),
    ]
    for tag, name, items in modules:
        pdf.sub_heading(f"[{tag}] {name}")
        for it in items:
            pdf.bullet(it)
        pdf.ln(2)

    pdf.sub_heading("Technology Stack")
    pdf.draw_table(
        ["Layer", "Technology"],
        [
            ["Backend", "Python + Flask"],
            ["Database", "PostgreSQL (psycopg driver)"],
            ["Frontend", "HTML + CSS + Vanilla JavaScript"],
            ["Storage", "Local file system for comic images"],
            ["Auth", "Session-based login"],
        ],
        col_widths=[40, 130],
    )

    # ── PAGE 5 — ER DIAGRAM ─────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title(5, "ER DIAGRAM")
    pdf.body("The Entity-Relationship Diagram for the platform is shown below:")
    pdf.ln(4)
    
    er_img_path = BASE / "app" / "screenshot" / "ER_Diagram.png"
    if er_img_path.exists():
        # image logic to fit
        from PIL import Image
        try:
            with Image.open(er_img_path) as im:
                iw, ih = im.size
                
            # fit horizontally with some margin
            usable_w = pdf.w - pdf.l_margin - pdf.r_margin
            usable_h = pdf.h - pdf.get_y() - pdf.b_margin
            
            # calculate scale
            scale = min(usable_w / iw, usable_h / ih, 1.0)
            
            new_w = iw * scale
            new_h = ih * scale
            
            # center image horizontally
            x_offset = pdf.l_margin + (usable_w - new_w) / 2
            
            pdf.image(str(er_img_path), x=x_offset, y=pdf.get_y(), w=new_w, h=new_h)
            pdf.set_y(pdf.get_y() + new_h + 10)
        except Exception as e:
            pdf.body(f"[Error loading ER Diagram: {e}]")
    else:
        pdf.body("[ER Diagram image not found at app/screenshot/ER_digram.png]")

    # ── PAGE ER ENTITIES ───────────────────────────────────────────────
    pdf.add_page()
    pdf.sub_heading("Entities and their relationships:")
    pdf.ln(2)
    
    er_entities = [
        "admin         : Manages the platform.",
        "publisher     : Uploads and manages comics.",
        "reader        : Reads comics, progress is tracked.",
        "comic         : Belongs to a publisher. Has many chapters.",
        "chapter       : Belongs to a comic. Has many pages.",
        "page          : Belongs to a chapter. Stores image URL.",
        "reading_progress : Links reader and chapter. Tracks last page.",
    ]
    for ent in er_entities:
        pdf.bullet(ent)
        
    pdf.ln(6)
    pdf.sub_heading("Key Relationships:")
    pdf.ln(2)
    
    key_relationships = [
        "publisher --< comic       (One publisher, many comics)",
        "comic     --< chapter     (One comic, many chapters)",
        "chapter   --< page        (One chapter, many pages)",
        "reader    --< reading_progress >-- chapter  (Many-to-many via progress)"
    ]
    for kr in key_relationships:
        pdf.bullet(kr)

    # ── PAGE 6 — DATABASE DESIGN ────────────────────────────────────────
    pdf.add_page()
    pdf.section_title(6, "DATABASE DESIGN (Tables in 3NF)")

    pdf.body("All tables are in Third Normal Form (3NF):")
    pdf.bullet("No repeating groups (1NF).")
    pdf.bullet("All non-key attributes depend on whole primary key (2NF).")
    pdf.bullet("No transitive dependencies (3NF).")
    pdf.ln(4)

    cw = [35, 40, 95]  # column widths for db tables -> total 170

    # -- admin
    pdf.sub_heading("Table: admin")
    pdf.draw_table(
        ["Column", "Type", "Constraints"],
        [
            ["id",         "BIGINT",       "PRIMARY KEY, AUTO-GENERATED"],
            ["name",       "VARCHAR(100)", "NOT NULL"],
            ["email",      "VARCHAR(150)", "NOT NULL, UNIQUE"],
            ["password",   "TEXT",         "NOT NULL"],
            ["created_at", "TIMESTAMP",    "DEFAULT CURRENT_TIMESTAMP"],
        ],
        col_widths=cw,
    )

    # -- publisher
    pdf.sub_heading("Table: publisher")
    pdf.draw_table(
        ["Column", "Type", "Constraints"],
        [
            ["id",         "BIGINT",       "PRIMARY KEY, AUTO-GENERATED"],
            ["name",       "VARCHAR(100)", "NOT NULL"],
            ["email",      "VARCHAR(150)", "NOT NULL, UNIQUE"],
            ["password",   "TEXT",         "NOT NULL"],
            ["logo_url",   "TEXT",         "OPTIONAL"],
            ["created_at", "TIMESTAMP",    "DEFAULT CURRENT_TIMESTAMP"],
        ],
        col_widths=cw,
    )

    # -- reader
    pdf.sub_heading("Table: reader")
    pdf.draw_table(
        ["Column", "Type", "Constraints"],
        [
            ["id",         "BIGINT",       "PRIMARY KEY, AUTO-GENERATED"],
            ["name",       "VARCHAR(100)", "NOT NULL"],
            ["email",      "VARCHAR(150)", "NOT NULL, UNIQUE"],
            ["password",   "TEXT",         "NOT NULL"],
            ["created_at", "TIMESTAMP",    "DEFAULT CURRENT_TIMESTAMP"],
        ],
        col_widths=cw,
    )

    # -- page break before remaining tables
    pdf.add_page()
    pdf.section_title(6, "DATABASE DESIGN (continued)")

    # -- comic
    pdf.sub_heading("Table: comic")
    pdf.draw_table(
        ["Column", "Type", "Constraints"],
        [
            ["id",           "BIGINT",       "PRIMARY KEY, AUTO-GENERATED"],
            ["publisher_id", "BIGINT",       "FOREIGN KEY (publisher.id)"],
            ["title",        "TEXT",         "NOT NULL"],
            ["description",  "TEXT",         "OPTIONAL"],
            ["genre",        "VARCHAR(80)",  "OPTIONAL"],
            ["poster_url",   "TEXT",         "OPTIONAL"],
            ["status",       "ENUM",        "'draft' or 'published'"],
            ["created_at",   "TIMESTAMP",    "DEFAULT CUR_TIMESTAMP"],
        ],
        col_widths=cw,
    )

    # -- chapter
    pdf.sub_heading("Table: chapter")
    pdf.draw_table(
        ["Column", "Type", "Constraints"],
        [
            ["id",             "BIGINT",    "PRIMARY KEY, AUTO-GEN"],
            ["comic_id",       "BIGINT",    "FOREIGN KEY (comic.id)"],
            ["chapter_number", "INT",       "NOT NULL"],
            ["title",          "TEXT",      "OPTIONAL"],
            ["published_at",   "TIMESTAMP", "DEFAULT CUR_TIMESTAMP"],
        ],
        col_widths=cw,
    )
    pdf.body("UNIQUE constraint: (comic_id, chapter_number)")
    pdf.ln(2)

    # -- page
    pdf.sub_heading("Table: page")
    pdf.draw_table(
        ["Column", "Type", "Constraints"],
        [
            ["id",          "BIGINT", "PRIMARY KEY, AUTO-GEN"],
            ["chapter_id",  "BIGINT", "FOREIGN KEY (chapter.id)"],
            ["page_number", "INT",    "NOT NULL"],
            ["image_url",   "TEXT",   "NOT NULL"],
        ],
        col_widths=cw,
    )
    pdf.body("UNIQUE constraint: (chapter_id, page_number)")
    pdf.ln(2)

    # -- reading_progress
    pdf.sub_heading("Table: reading_progress")
    pdf.draw_table(
        ["Column", "Type", "Constraints"],
        [
            ["id",         "BIGINT",    "PRIMARY KEY, AUTO-GEN"],
            ["reader_id",  "BIGINT",    "FOREIGN KEY (reader.id)"],
            ["chapter_id", "BIGINT",    "FOREIGN KEY (chapter.id)"],
            ["last_page",  "INT",       "DEFAULT 1"],
            ["completed",  "BOOLEAN",   "DEFAULT FALSE"],
            ["updated_at", "TIMESTAMP", "DEFAULT CUR_TIMESTAMP"],
        ],
        col_widths=cw,
    )
    pdf.body("UNIQUE constraint: (reader_id, chapter_id)")

    # ── PAGE — SCREEN LAYOUT ────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title(7, "INPUT AND OUTPUT SCREEN LAYOUT")
    pdf.body("The following screens and routes are implemented in the project. Each visual output is displayed on its own page.")
    pdf.ln(2)

    screens = [
        ["1", "Login Page",                  "/login"],
        ["2", "Register Page",               "/register"],
        ["3", "Reader Home",                 "/reader/home"],
        ["4", "Comic Detail & Chapters",     "/reader/comic/<comic_id>"],
        ["5", "Comic Reader (Full Screen)",  "/reader/read/<chapter_id>"],
        ["6", "Publisher Dashboard",         "/publisher/home"],
        ["7", "Publisher - Edit Comic",      "/publisher/edit/<comic_id>"],
        ["8", "Admin Dashboard",             "/admin/home"],
    ]
    pdf.draw_table(["Sr.", "Page / UI View", "URL / Route"], screens, col_widths=[15, 65, 90])
    pdf.ln(4)

    section_7_images = [
        ("Login Frame",         "login.png"),
        ("Registration Module", "register.png"),
        ("Reader Dashboard",    "reader_home.png"),
        ("Comic Information",   "reader_read_chapter_id.png"),
        ("Chapter Reader",      "reader_read_chapter_id_.png"),
        ("Publisher Dashboard", "publisher_home.png"),
        ("Comic Page Editor",   "edit_comic.png"),
        ("Admin Main Panel",    "admin_home.png"),
    ]

    for title, fname in section_7_images:
        img_p = BASE / "app" / "screenshot" / fname
        pdf.add_image_page(7, "INPUT AND OUTPUT SCREEN LAYOUT", img_p, subtitle=title, orientation="L", show_section=False)

    # ── PAGE — CODING AND IMPLEMENTATION ────────────────────────────────
    pdf.add_page()
    pdf.section_title(8, "CODING AND IMPLEMENTATION")

    pdf.body("The following source code and database structures are included in the implementation. Each capture is displayed on its own page.")
    pdf.ln(4)

    # Helper to add a group of images from a folder
    def add_group(group_title, folder, files):
        for f in files:
            img_p = BASE / "app" / "screenshot" / folder / f
            pdf.add_image_page(8, "CODING AND IMPLEMENTATION", img_p, subtitle=f"{group_title} - {f}", show_section=False)

    # Database
    add_group("Database Schemas & API Configuration", "programs", ["db.png", "sql_part_1.png", "sql_part_2.png"])

    # Server Entry
    add_group("Server Initialization Entry Point", "programs", ["run_1.png", "run_2.png"])

    # Routing
    routing_files = ["auth_routes_1.png", "auth_routes_2.png"] + [f"comic_routes_{i}.png" for i in range(1, 9)] + ["admin_routes.png", "admin_routes_1.png", "admin_routes_2.png"]
    add_group("Flask Blueprint Routing Layer", "programs", routing_files)

    # Logic
    logic_files = ["auth_service.png", "auth_quries.png", "comic_quires_1.png", "comic_quries_2.png", "chapter_queries_1.png", "chapter_quires_part_2.png", "admin_quries.png"]
    add_group("PostgreSQL Execution Logic", "programs", logic_files)

    # HTML
    html_files = [
        "login_html.png", "register_html.png", "reader_home_html.png",
        "reader_comic_html_part_one.png", "reader_comic_html_part_two.png", "reader_comic_html_part_three.png", "reader_comic_part_four.png", "reader_comic_html_part_five.png",
        "publisher_home_html_part_one.png", "publisher_home_part_two.png",
        "publisher_chapter_html_one.png", "publisher_chapter_html_two.png",
        "publisher_edit_html.png", "admin_home_html_one.png", "admin_home_html_part_two.png", "admin_home_html_part_three.png"
    ]
    add_group("Frontend Display Engine Integrations", "html", html_files)

    # ── PAGE — REPORT DESIGN ────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title(9, "REPORT DESIGN")

    pdf.sub_heading("System Flow")
    pdf.body("User visits site --> Login / Register --> Role detected")
    pdf.ln(1)
    flow_data = [
        ["Admin",      "View dashboard, manage users & comics"],
        ["Publisher",  "Add comics, upload chapters & pages"],
        ["Reader",     "Browse comics, read chapters, progress saved"],
    ]
    pdf.draw_table(["Role", "Actions After Login"], flow_data, col_widths=[40, 130])

    pdf.sub_heading("Data Flow")
    for df in [
        "Publisher uploads comic --> stored in 'comic' table.",
        "Publisher adds chapter --> stored in 'chapter' table.",
        "Publisher uploads pages --> stored in 'page' table.",
        "Reader reads a chapter --> 'reading_progress' updated.",
    ]:
        pdf.bullet(df)
    pdf.ln(3)

    pdf.sub_heading("Security Design")
    for sd in [
        "Session-based authentication for all routes.",
        "Role-based access: internal pages protected by role middleware.",
        "Passwords hashed via PostgreSQL pgcrypto (or backend utility).",
    ]:
        pdf.bullet(sd)
    pdf.ln(3)

    pdf.sub_heading("File Storage")
    pdf.body("Comic poster and page images are stored under the Data/ directory, "
             "organized by publisher ID and comic ID.")

    # ── PAGE — CONCLUSION ───────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title(10, "CONCLUSION")

    pdf.body(
        "The Comic Book Reading Platform successfully provides a complete "
        "end-to-end solution for digital comic publishing and reading."
    )
    pdf.ln(3)

    pdf.sub_heading("Key Achievements")
    for ka in [
        "Built a multi-role system: Admin, Publisher, Reader.",
        "Publishers can easily upload and manage comic content.",
        "Readers can browse, read, and track their progress.",
        "Full-screen distraction-free reading mode implemented.",
        "Secure login with role-based access control.",
        "Clean and normalized PostgreSQL database design.",
    ]:
        pdf.bullet(ka)
    pdf.ln(4)

    pdf.body(
        "The project demonstrates practical use of Flask, PostgreSQL, "
        "and HTML/CSS/JS to build a real-world web application."
    )

    # ── PAGE — FUTURE ENHANCEMENT ───────────────────────────────────────
    pdf.add_page()
    pdf.section_title(11, "FUTURE ENHANCEMENT")

    pdf.body("The following features can be added in future versions:")
    pdf.ln(2)

    enhancements = [
        ("Search and Filter",   "Search comics by title or filter by genre."),
        ("Bookmarking",         "Readers can bookmark favourite comics."),
        ("Ratings & Reviews",   "Readers can rate and review comics."),
        ("Mobile App",          "Convert platform to an installable PWA."),
        ("Subscription Model",  "Paid access to premium comics."),
        ("Comment Section",     "Readers can comment on chapters."),
        ("Cloud Storage",       "Move image storage to AWS S3 / Cloudinary."),
        ("Email Notification",  "Notify readers when new chapters arrive."),
        ("Analytics Dashboard", "Show publishers view counts & engagement."),
        ("Dark Mode UI",        "Full dark theme for comfortable reading."),
    ]
    pdf.draw_table(
        ["#", "Feature", "Description"],
        [[str(i+1), f, d] for i, (f, d) in enumerate(enhancements)],
        col_widths=[10, 45, 115],
    )

    # ── PAGE — BIBLIOGRAPHY ─────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title(12, "BIBLIOGRAPHY")

    refs = [
        ("Flask Documentation",                    "https://flask.palletsprojects.com/"),
        ("PostgreSQL Documentation",               "https://www.postgresql.org/docs/"),
        ("psycopg2 Driver",                        "https://www.psycopg.org/docs/"),
        ("Python Official Docs",                   "https://docs.python.org/3/"),
        ("HTML5 & CSS3 Mozilla Reference",         "https://developer.mozilla.org/en-US/docs/Web"),
        ("Git Source Control",                     "https://git-scm.com/doc"),
        ("Python Web Development (Book)",          "O'Reilly Media"),
        ("Database System Concepts (Book)",        "McGraw-Hill Education"),
    ]
    for i, (title, source) in enumerate(refs, 1):
        pdf.set_font("Courier", "B", 10)
        pdf.set_text_color(*C_BODY)
        pdf.cell(10, 6, f"[{i}]")
        pdf.set_font("Courier", "", 10)
        pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Courier", "I", 9)
        pdf.set_text_color(*C_MID)
        pdf.cell(10, 5, "")
        pdf.cell(0, 5, source, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # ── SAVE ────────────────────────────────────────────────────────────
    pdf.output(str(OUT))
    print(f"[OK] PDF saved to: {OUT}")
    print(f"[OK] Total pages: {pdf.page_no()}")


if __name__ == "__main__":
    build()
