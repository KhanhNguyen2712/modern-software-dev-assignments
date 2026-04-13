import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from app.db import apply_seed_if_needed, get_db, get_session
from sqlalchemy.orm import Session


class TestGetDb:
    """Tests for get_db() generator function."""

    @patch("app.db.SessionLocal")
    def test_get_db_commit_on_success(self, mock_session_local):
        """Test that session commits on successful exit."""
        mock_session = MagicMock(spec=Session)
        mock_session_local.return_value = mock_session

        gen = get_db()
        session = next(gen)
        assert session == mock_session

        # Continue generator to completion (triggers commit in finally)
        try:
            next(gen)
        except StopIteration:
            pass

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.rollback.assert_not_called()

    @patch("app.db.SessionLocal")
    def test_get_db_rollback_on_exception(self, mock_session_local):
        """Test that session rolls back on exception and re-raises."""
        mock_session = MagicMock(spec=Session)
        mock_session_local.return_value = mock_session

        gen = get_db()
        _ = next(gen)  # Get the session

        # Simulate exception being thrown back into generator
        with pytest.raises(ValueError, match="Test error"):
            gen.throw(ValueError, "Test error")

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.commit.assert_not_called()


class TestGetSession:
    """Tests for get_session() context manager."""

    @patch("app.db.SessionLocal")
    def test_get_session_commit_on_success(self, mock_session_local):
        """Test that session commits on successful context exit."""
        mock_session = MagicMock(spec=Session)
        mock_session_local.return_value = mock_session

        with get_session() as session:
            assert session == mock_session

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.rollback.assert_not_called()

    @patch("app.db.SessionLocal")
    def test_get_session_rollback_on_exception(self, mock_session_local):
        """Test that session rolls back on exception and re-raises."""
        mock_session = MagicMock(spec=Session)
        mock_session_local.return_value = mock_session

        with pytest.raises(ValueError, match="Test error"):
            with get_session() as session:
                assert session == mock_session
                raise ValueError("Test error")

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.commit.assert_not_called()


class TestApplySeedIfNeeded:
    """Tests for apply_seed_if_needed() function."""

    @patch("app.db.engine")
    @patch("app.db.Path")
    def test_apply_seed_when_db_newly_created(self, mock_path_class, mock_engine):
        """Test that seed is applied when DB file is newly created."""
        # Setup mock paths
        mock_db_path = MagicMock(spec=Path)
        mock_db_path.exists.return_value = False
        mock_db_path.parent = MagicMock()

        mock_seed_file = MagicMock(spec=Path)
        mock_seed_file.exists.return_value = True
        mock_seed_file.read_text.return_value = "INSERT INTO notes (title) VALUES ('Test');"

        def path_side_effect(path_str):
            if path_str == os.getenv("DATABASE_PATH", "./data/app.db"):
                return mock_db_path
            elif path_str == "./data/seed.sql":
                return mock_seed_file
            return MagicMock(spec=Path)

        mock_path_class.side_effect = path_side_effect

        # Mock engine.begin() as context manager
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=None)

        apply_seed_if_needed()

        mock_db_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_db_path.touch.assert_called_once()
        mock_engine.begin.assert_called_once()

    @patch("app.db.engine")
    @patch("app.db.Path")
    def test_no_seed_when_db_already_exists(self, mock_path_class, mock_engine):
        """Test that seed is NOT applied when DB file already exists."""
        mock_db_path = MagicMock(spec=Path)
        mock_db_path.exists.return_value = True  # DB already exists
        mock_db_path.parent = MagicMock()

        def path_side_effect(path_str):
            if path_str == os.getenv("DATABASE_PATH", "./data/app.db"):
                return mock_db_path
            return MagicMock(spec=Path)

        mock_path_class.side_effect = path_side_effect

        apply_seed_if_needed()

        # Should not touch the file or apply seed
        mock_db_path.touch.assert_not_called()
        mock_engine.begin.assert_not_called()

    @patch("app.db.engine")
    @patch("app.db.Path")
    def test_no_seed_when_seed_file_missing(self, mock_path_class, mock_engine):
        """Test that seed is NOT applied when seed file does not exist."""
        mock_db_path = MagicMock(spec=Path)
        mock_db_path.exists.return_value = False  # DB is new
        mock_db_path.parent = MagicMock()

        mock_seed_file = MagicMock(spec=Path)
        mock_seed_file.exists.return_value = False  # But no seed file

        def path_side_effect(path_str):
            if path_str == os.getenv("DATABASE_PATH", "./data/app.db"):
                return mock_db_path
            elif path_str == "./data/seed.sql":
                return mock_seed_file
            return MagicMock(spec=Path)

        mock_path_class.side_effect = path_side_effect

        apply_seed_if_needed()

        mock_db_path.touch.assert_called_once()
        mock_engine.begin.assert_not_called()  # No seed to apply

    @patch("app.db.engine")
    @patch("app.db.Path")
    def test_empty_seed_file(self, mock_path_class, mock_engine):
        """Test that empty seed file is handled gracefully."""
        mock_db_path = MagicMock(spec=Path)
        mock_db_path.exists.return_value = False
        mock_db_path.parent = MagicMock()

        mock_seed_file = MagicMock(spec=Path)
        mock_seed_file.exists.return_value = True
        mock_seed_file.read_text.return_value = "   "  # Empty/whitespace only

        def path_side_effect(path_str):
            if path_str == os.getenv("DATABASE_PATH", "./data/app.db"):
                return mock_db_path
            elif path_str == "./data/seed.sql":
                return mock_seed_file
            return MagicMock(spec=Path)

        mock_path_class.side_effect = path_side_effect

        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=None)

        apply_seed_if_needed()

        # Should not execute any statements on empty seed
        mock_conn.execute.assert_not_called()

    @patch("app.db.engine")
    @patch("app.db.Path")
    def test_multiple_statements_in_seed(self, mock_path_class, mock_engine):
        """Test that multiple SQL statements in seed file are executed."""
        mock_db_path = MagicMock(spec=Path)
        mock_db_path.exists.return_value = False
        mock_db_path.parent = MagicMock()

        mock_seed_file = MagicMock(spec=Path)
        mock_seed_file.exists.return_value = True
        mock_seed_file.read_text.return_value = """
            INSERT INTO notes (title) VALUES ('Test1');
            INSERT INTO notes (title) VALUES ('Test2');
            DELETE FROM notes WHERE id=1;
        """

        def path_side_effect(path_str):
            if path_str == os.getenv("DATABASE_PATH", "./data/app.db"):
                return mock_db_path
            elif path_str == "./data/seed.sql":
                return mock_seed_file
            return MagicMock(spec=Path)

        mock_path_class.side_effect = path_side_effect

        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=None)

        apply_seed_if_needed()

        # Should execute 3 statements
        assert mock_conn.execute.call_count == 3
