from database.db import get_db


class QuoteModel:

    @staticmethod
    def get_random_quote(user_id=None, category_id=None):
        conn = get_db()
        cursor = conn.cursor()

        base_where = "WHERE q.status = 'approved'"
        base_params = []

        if category_id:
            base_where += " AND q.category_id = %s"
            base_params.append(category_id)

        recent_ids = []

        # Try to exclude recently shuffled quote IDs for this user
        if user_id:
            cursor.execute(
                """
                SELECT quote_id
                FROM shuffle_history
                WHERE user_id = %s
                ORDER BY shuffled_at DESC
                LIMIT 10
                """,
                (user_id,)
            )

            recent_ids = [
                row['quote_id']
                for row in cursor.fetchall()
            ]

        where_clause = base_where
        query_params = list(base_params)

        if recent_ids:
            placeholders = ",".join(["%s"] * len(recent_ids))
            where_clause += f" AND q.id NOT IN ({placeholders})"
            query_params.extend(recent_ids)

        if user_id:
            liked_expression = """
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_liked
            """
            saved_expression = """
                (
                    SELECT COUNT(*)
                    FROM saved_quotes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_saved
            """
        else:
            liked_expression = "0 AS is_liked"
            saved_expression = "0 AS is_saved"

        query = f"""
            SELECT
                q.id,
                q.text,
                q.author,
                q.category_id,
                q.submitted_by_id,
                q.status,
                q.is_featured,
                q.is_quote_of_the_moment,
                q.created_at,
                c.name AS category_name,
                c.slug AS category_slug,
                c.icon AS category_icon,
                u.name AS submitted_by_name,
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                ) AS likes_count,
                {liked_expression},
                {saved_expression}
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            {where_clause}
            ORDER BY RANDOM()
            LIMIT 1
        """

        if user_id:
            query_params = [user_id, user_id] + query_params

        cursor.execute(query, query_params)
        row = cursor.fetchone()

        # Fallback if no unseen quote was found
        if not row and user_id and recent_ids:
            fallback_query = f"""
                SELECT
                    q.id,
                    q.text,
                    q.author,
                    q.category_id,
                    q.submitted_by_id,
                    q.status,
                    q.is_featured,
                    q.is_quote_of_the_moment,
                    q.created_at,
                    c.name AS category_name,
                    c.slug AS category_slug,
                    c.icon AS category_icon,
                    u.name AS submitted_by_name,
                    (
                        SELECT COUNT(*)
                        FROM likes
                        WHERE quote_id = q.id
                    ) AS likes_count,
                    (
                        SELECT COUNT(*)
                        FROM likes
                        WHERE quote_id = q.id
                          AND user_id = %s
                    ) AS is_liked,
                    (
                        SELECT COUNT(*)
                        FROM saved_quotes
                        WHERE quote_id = q.id
                          AND user_id = %s
                    ) AS is_saved
                FROM quotes q
                JOIN categories c ON q.category_id = c.id
                LEFT JOIN users u ON q.submitted_by_id = u.id
                {base_where}
                ORDER BY RANDOM()
                LIMIT 1
            """

            fallback_params = [user_id, user_id] + base_params

            cursor.execute(
                fallback_query,
                fallback_params
            )

            row = cursor.fetchone()

        quote = dict(row) if row else None

        # Record in shuffle history
        if quote and user_id:
            cursor.execute(
                """
                INSERT INTO shuffle_history (user_id, quote_id)
                VALUES (%s, %s)
                """,
                (user_id, quote['id'])
            )

            conn.commit()

        conn.close()
        return quote

    @staticmethod
    def get_community_quotes(
        user_id=None,
        category_id=None,
        search=None,
        sort='latest',
        limit=50,
        offset=0
    ):
        conn = get_db()
        cursor = conn.cursor()

        where_clauses = ["q.status = 'approved'"]
        params = []

        if category_id:
            where_clauses.append("q.category_id = %s")
            params.append(category_id)

        if search:
            where_clauses.append(
                "(q.text ILIKE %s OR q.author ILIKE %s)"
            )

            pattern = f"%{search.strip()}%"
            params.extend([pattern, pattern])

        where_str = " WHERE " + " AND ".join(where_clauses)

        if sort == 'popular':
            order_str = "ORDER BY likes_count DESC, q.created_at DESC"
        elif sort == 'random':
            order_str = "ORDER BY RANDOM()"
        else:
            order_str = "ORDER BY q.created_at DESC"

        if user_id:
            liked_expression = """
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_liked
            """

            saved_expression = """
                (
                    SELECT COUNT(*)
                    FROM saved_quotes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_saved
            """
        else:
            liked_expression = "0 AS is_liked"
            saved_expression = "0 AS is_saved"

        query = f"""
            SELECT
                q.id,
                q.text,
                q.author,
                q.category_id,
                q.submitted_by_id,
                q.status,
                q.is_featured,
                q.is_quote_of_the_moment,
                q.created_at,
                c.name AS category_name,
                c.slug AS category_slug,
                c.icon AS category_icon,
                u.name AS submitted_by_name,
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                ) AS likes_count,
                {liked_expression},
                {saved_expression}
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            {where_str}
            {order_str}
            LIMIT %s OFFSET %s
        """

        if user_id:
            params = [user_id, user_id] + params

        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_quote_by_id(quote_id, user_id=None):
        conn = get_db()
        cursor = conn.cursor()

        if user_id:
            liked_expression = """
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_liked
            """

            saved_expression = """
                (
                    SELECT COUNT(*)
                    FROM saved_quotes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_saved
            """

            params = [user_id, user_id, quote_id]

        else:
            liked_expression = "0 AS is_liked"
            saved_expression = "0 AS is_saved"

            params = [quote_id]

        query = f"""
            SELECT
                q.id,
                q.text,
                q.author,
                q.category_id,
                q.submitted_by_id,
                q.status,
                q.is_featured,
                q.is_quote_of_the_moment,
                q.created_at,
                c.name AS category_name,
                c.slug AS category_slug,
                c.icon AS category_icon,
                u.name AS submitted_by_name,
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                ) AS likes_count,
                {liked_expression},
                {saved_expression}
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            WHERE q.id = %s
        """

        cursor.execute(query, params)

        row = cursor.fetchone()

        conn.close()

        return dict(row) if row else None

    @staticmethod
    def submit_quote(text, author, category_id, user_id):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO quotes (
                    text,
                    author,
                    category_id,
                    submitted_by_id,
                    status
                )
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING id
                """,
                (
                    text.strip(),
                    author.strip(),
                    category_id,
                    user_id
                )
            )

            new_id = cursor.fetchone()['id']

            conn.commit()

            return new_id

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def get_user_submissions(user_id):
        conn = get_db()
        cursor = conn.cursor()

        query = """
            SELECT
                q.id,
                q.text,
                q.author,
                q.category_id,
                q.status,
                q.created_at,
                c.name AS category_name,
                c.icon AS category_icon,
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                ) AS likes_count
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            WHERE q.submitted_by_id = %s
            ORDER BY q.created_at DESC
        """

        cursor.execute(query, (user_id,))

        rows = cursor.fetchall()

        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_user_approved_quotes(user_id, observer_id=None):
        conn = get_db()
        cursor = conn.cursor()

        if observer_id:
            liked_expression = """
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_liked
            """

            saved_expression = """
                (
                    SELECT COUNT(*)
                    FROM saved_quotes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_saved
            """

            params = [observer_id, observer_id, user_id]

        else:
            liked_expression = "0 AS is_liked"
            saved_expression = "0 AS is_saved"

            params = [user_id]

        query = f"""
            SELECT
                q.id,
                q.text,
                q.author,
                q.category_id,
                q.status,
                q.created_at,
                c.name AS category_name,
                c.icon AS category_icon,
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                ) AS likes_count,
                {liked_expression},
                {saved_expression}
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            WHERE q.submitted_by_id = %s
              AND q.status = 'approved'
            ORDER BY q.created_at DESC
        """

        cursor.execute(query, params)

        rows = cursor.fetchall()

        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_pending_quotes():
        conn = get_db()
        cursor = conn.cursor()

        query = """
            SELECT
                q.id,
                q.text,
                q.author,
                q.category_id,
                q.status,
                q.created_at,
                c.name AS category_name,
                c.icon AS category_icon,
                u.name AS submitted_by_name,
                u.email AS submitted_by_email
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            WHERE q.status = 'pending'
            ORDER BY q.created_at ASC
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_all_quotes_admin(
        status=None,
        search=None,
        category_id=None
    ):
        conn = get_db()
        cursor = conn.cursor()

        where_clauses = []
        params = []

        if status:
            where_clauses.append("q.status = %s")
            params.append(status)

        if category_id:
            where_clauses.append("q.category_id = %s")
            params.append(category_id)

        if search:
            where_clauses.append(
                "(q.text ILIKE %s OR q.author ILIKE %s OR u.name ILIKE %s)"
            )

            pattern = f"%{search.strip()}%"

            params.extend([
                pattern,
                pattern,
                pattern
            ])

        where_str = (
            " WHERE " + " AND ".join(where_clauses)
            if where_clauses
            else ""
        )

        query = f"""
            SELECT
                q.id,
                q.text,
                q.author,
                q.category_id,
                q.submitted_by_id,
                q.status,
                q.is_featured,
                q.is_quote_of_the_moment,
                q.created_at,
                c.name AS category_name,
                c.icon AS category_icon,
                u.name AS submitted_by_name,
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                ) AS likes_count
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            {where_str}
            ORDER BY q.created_at DESC
        """

        cursor.execute(query, params)

        rows = cursor.fetchall()

        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def update_status(quote_id, status):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE quotes
                SET status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (status, quote_id)
            )

            conn.commit()

            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def update_quote(
        quote_id,
        text,
        author,
        category_id
    ):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE quotes
                SET text = %s,
                    author = %s,
                    category_id = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    text.strip(),
                    author.strip(),
                    category_id,
                    quote_id
                )
            )

            conn.commit()

            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def delete_quote(quote_id):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM quotes WHERE id = %s",
                (quote_id,)
            )

            conn.commit()

            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def toggle_featured(quote_id):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT is_featured
                FROM quotes
                WHERE id = %s
                """,
                (quote_id,)
            )

            row = cursor.fetchone()

            if not row:
                return False, "Quote not found"

            new_val = not row['is_featured']

            cursor.execute(
                """
                UPDATE quotes
                SET is_featured = %s
                WHERE id = %s
                """,
                (new_val, quote_id)
            )

            conn.commit()

            return True, new_val

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def toggle_moment(quote_id):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT is_quote_of_the_moment
                FROM quotes
                WHERE id = %s
                """,
                (quote_id,)
            )

            row = cursor.fetchone()

            if not row:
                return False, "Quote not found"

            new_val = not row['is_quote_of_the_moment']

            # Keep only one quote as quote of the moment.
            if new_val:
                cursor.execute(
                    """
                    UPDATE quotes
                    SET is_quote_of_the_moment = FALSE
                    """
                )

            cursor.execute(
                """
                UPDATE quotes
                SET is_quote_of_the_moment = %s
                WHERE id = %s
                """,
                (new_val, quote_id)
            )

            conn.commit()

            return True, new_val

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def get_featured_quote(user_id=None):
        conn = get_db()
        cursor = conn.cursor()

        if user_id:
            liked_expression = """
                (
                    SELECT COUNT(*)
                    FROM likes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_liked
            """

            saved_expression = """
                (
                    SELECT COUNT(*)
                    FROM saved_quotes
                    WHERE quote_id = q.id
                      AND user_id = %s
                ) AS is_saved
            """

            params = [user_id, user_id]

        else:
            liked_expression = "0 AS is_liked"
            saved_expression = "0 AS is_saved"

            params = []

        query = f"""
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
                {liked_expression},
                {saved_expression}
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            WHERE q.is_featured = TRUE
              AND q.status = 'approved'
            ORDER BY q.updated_at DESC
            LIMIT 1
        """

        cursor.execute(query, params)

        row = cursor.fetchone()

        conn.close()

        return dict(row) if row else None