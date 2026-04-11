from unittest.mock import patch, MagicMock

from core.db import user_table


class TestUserTable:
    @patch("core.db.get_supabase")
    def test_returns_query_filtered_by_user_id(self, mock_get_sb):
        mock_sb = MagicMock()
        mock_get_sb.return_value = mock_sb

        result = user_table("conversions", "auth0|user123")

        mock_sb.table.assert_called_once_with("conversions")
        mock_sb.table().eq.assert_called_once_with("user_id", "auth0|user123")
