import sqlite3
import tempfile
from pathlib import Path

from backend.app.models import Base
from sqlalchemy import create_engine


def test_sqlite_indexes_exist_and_are_used_for_note_title_queries():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "perf.db"
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)

        with sqlite3.connect(db_path) as connection:
            note_indexes = {row[1] for row in connection.execute("PRAGMA index_list('notes')")}
            note_tag_indexes = {row[1] for row in connection.execute("PRAGMA index_list('note_tags')")}

            assert "ix_notes_title" in note_indexes
            assert "ix_note_tags_note_id" in note_tag_indexes
            assert "ix_note_tags_tag_id" in note_tag_indexes

            connection.execute(
                "INSERT INTO notes (title, content) VALUES (?, ?)",
                ("needle", "body"),
            )
            plan_rows = connection.execute(
                "EXPLAIN QUERY PLAN SELECT * FROM notes WHERE title = ?",
                ("needle",),
            ).fetchall()

        assert any("INDEX" in row[-1].upper() for row in plan_rows)
