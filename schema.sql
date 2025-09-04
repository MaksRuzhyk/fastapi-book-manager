DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'genre_enum') THEN
    CREATE TYPE genre_enum AS ENUM ('Fiction','Non-Fiction','Science','History');
  END IF;
END$$;

--  Користувачі
CREATE TABLE IF NOT EXISTS users (
    id             SERIAL PRIMARY KEY,
    email          TEXT NOT NULL,
    password_hash  TEXT NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
    CREATE UNIQUE INDEX IF NOT EXISTS user_email_unique_lower
    ON users ((LOWER(email)));


-- Автори
CREATE TABLE IF NOT EXISTS authors (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Книги
CREATE TABLE IF NOT EXISTS books (
    id              BIGSERIAL PRIMARY KEY,
    title           TEXT       NOT NULL,
    author_id       INT        NOT NULL REFERENCES authors(id) ON DELETE RESTRICT,
    genre           genre_enum NOT NULL,
    published_year  INT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    owner_id        INT        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT books_unique UNIQUE (title, author_id, published_year),
    CONSTRAINT books_year_check CHECK (
    published_year BETWEEN 1800 AND EXTRACT(YEAR FROM NOW())::INT
    )
);

-- View для SELECT
CREATE OR REPLACE VIEW books_view AS
SELECT
    b.id,
    b.title,
    a.name  AS author,
    b.genre,
    b.published_year,
    b.created_at
FROM books b
JOIN authors a ON a.id = b.author_id;