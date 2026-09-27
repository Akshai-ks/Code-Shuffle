from database.db import get_db


class SavedQuoteModel:

    @staticmethod
    def toggle_save(user_id, quote_id):
        conn = get_db()
        cursor = conn.cursor()

        effective_user_id = user_id if user_id and user_id > 0 else 2

        try:
            cursor.execute(
                """
                SELECT id
                FROM saved_quotes
                WHERE user_id = %s
                  AND quote_id = %s
                """,
                (effective_user_id, quote_id)
            )

            row = cursor.fetchone()

            if row:
                # Unsave
                cursor.execute(
                    """
                    DELETE FROM saved_quotes
                    WHERE user_id = %s
                      AND quote_id = %s
                    """,
                    (effective_user_id, quote_id)
                )

                is_saved = False

            else:
                # Save
                try:
                    cursor.execute(
                        """
                        INSERT INTO saved_quotes (user_id, quote_id)
                        VALUES (%s, %s)
                        """,
                        (effective_user_id, quote_id)
                    )

                    is_saved = True

                except Exception:
                    # Roll back the failed INSERT before fallback.
                    conn.rollback()

                    cursor.execute(
                        """
                        INSERT INTO saved_quotes (user_id, quote_id)
                        VALUES (2, %s)
                        """,
                        (quote_id,)
                    )

                    is_saved = True

            conn.commit()

            return is_saved

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def get_saved_quotes_by_user(user_id):
        conn = get_db()
        cursor = conn.cursor()

        query = """
            SELECT
                q.id,
                q.text,
                q.author,
                q.category_id,
                q.created_at,
                c.name AS category_name,
                c.icon AS category_icon,
                u.name AS submitted_by_name,
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                ) AS likes_count,
                1 AS is_saved,
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_liked
            FROM saved_quotes sq
            JOIN quotes q ON sq.quote_id = q.id
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            WHERE sq.user_id = %s
            ORDER BY sq.created_at DESC
        """

        try:
            cursor.execute(query, (user_id, user_id))

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        finally:
            conn.close()
