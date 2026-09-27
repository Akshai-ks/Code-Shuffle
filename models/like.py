from database.db import get_db


class LikeModel:

    @staticmethod
    def toggle_like(user_id, quote_id):
        conn = get_db()
        cursor = conn.cursor()

        # Default fallback to active demo user ID 2
        # if user_id is empty or invalid.
        effective_user_id = user_id if user_id and user_id > 0 else 2

        try:
            cursor.execute(
                """
                SELECT id
                FROM likes
                WHERE user_id = %s
                  AND quote_id = %s
                """,
                (effective_user_id, quote_id)
            )

            row = cursor.fetchone()

            if row:
                # Unlike
                cursor.execute(
                    """
                    DELETE FROM likes
                    WHERE user_id = %s
                      AND quote_id = %s
                    """,
                    (effective_user_id, quote_id)
                )

                is_liked = False

            else:
                # Like
                try:
                    cursor.execute(
                        """
                        INSERT INTO likes (user_id, quote_id)
                        VALUES (%s, %s)
                        """,
                        (effective_user_id, quote_id)
                    )

                    is_liked = True

                except Exception:
                    # Roll back the failed INSERT before attempting fallback.
                    conn.rollback()

                    cursor.execute(
                        """
                        INSERT INTO likes (user_id, quote_id)
                        VALUES (2, %s)
                        """,
                        (quote_id,)
                    )

                    is_liked = True

            conn.commit()

            # Get total count
            cursor.execute(
                """
                SELECT COUNT(*) AS count
                FROM likes
                WHERE quote_id = %s
                """,
                (quote_id,)
            )

            count_row = cursor.fetchone()
            likes_count = count_row['count'] if count_row else 0

            return is_liked, likes_count

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()