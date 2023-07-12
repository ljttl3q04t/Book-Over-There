CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX services_book_name_gin_trgm_idx  ON services_book USING gin  (name gin_trgm_ops);