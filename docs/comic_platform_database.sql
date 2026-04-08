-- Production-Grade PostgreSQL Schema
-- Comic Book Reading Platform

-- STEP 0 — Extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- STEP 1 — ENUMS
CREATE TYPE comic_status AS ENUM ('draft', 'published');

-- STEP 2 — admin
CREATE TABLE admin (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- STEP 3 — publisher
CREATE TABLE publisher (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password TEXT NOT NULL,
  logo_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- STEP 4 — reader
CREATE TABLE reader (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- STEP 5 — comic
CREATE TABLE comic (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  publisher_id BIGINT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  genre VARCHAR(80),
  poster_url TEXT,
  status comic_status DEFAULT 'draft',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_comic_publisher
    FOREIGN KEY (publisher_id)
    REFERENCES publisher(id)
    ON DELETE CASCADE
);

CREATE INDEX idx_comic_publisher ON comic(publisher_id);
CREATE INDEX idx_comic_status ON comic(status);

-- STEP 6 — chapter
CREATE TABLE chapter (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  comic_id BIGINT NOT NULL,
  chapter_number INT NOT NULL,
  title TEXT,
  published_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_chapter_comic
    FOREIGN KEY (comic_id)
    REFERENCES comic(id)
    ON DELETE CASCADE,

  CONSTRAINT unique_chapter_per_comic
    UNIQUE (comic_id, chapter_number)
);

CREATE INDEX idx_chapter_comic ON chapter(comic_id);

-- STEP 7 — page
CREATE TABLE page (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  chapter_id BIGINT NOT NULL,
  page_number INT NOT NULL,
  image_url TEXT NOT NULL,

  CONSTRAINT fk_page_chapter
    FOREIGN KEY (chapter_id)
    REFERENCES chapter(id)
    ON DELETE CASCADE,

  CONSTRAINT unique_page_per_chapter
    UNIQUE (chapter_id, page_number)
);

CREATE INDEX idx_page_chapter ON page(chapter_id);

-- STEP 8 — reading_progress
CREATE TABLE reading_progress (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  reader_id BIGINT NOT NULL,
  chapter_id BIGINT NOT NULL,
  last_page INT NOT NULL DEFAULT 1,
  completed BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT unique_reader_chapter
    UNIQUE (reader_id, chapter_id),

  CONSTRAINT fk_progress_reader
    FOREIGN KEY (reader_id)
    REFERENCES reader(id)
    ON DELETE CASCADE,

  CONSTRAINT fk_progress_chapter
    FOREIGN KEY (chapter_id)
    REFERENCES chapter(id)
    ON DELETE CASCADE
);

CREATE INDEX idx_progress_reader ON reading_progress(reader_id);
