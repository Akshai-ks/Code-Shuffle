from database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash


class UserModel:

    @staticmethod
    def create_user(name, email, password, role='student'):
        conn = get_db()
        cursor = conn.cursor()

        password_hash = generate_password_hash(password)

        try:
            cursor.execute(
                """
                INSERT INTO users (
                    name,
                    email,
                    password_hash,
                    role
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (
                    name.strip(),
                    email.strip().lower(),
                    password_hash,
                    role
                )
            )

            user_id = cursor.fetchone()['id']

            conn.commit()

            return user_id, None

        except Exception as e:
            conn.rollback()
            return None, str(e)

        finally:
            conn.close()

    @staticmethod
    def get_user_by_email(email):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (email.strip().lower(),)
            )

            user = cursor.fetchone()

            return dict(user) if user else None

        finally:
            conn.close()

    @staticmethod
    def get_user_by_id(user_id):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    role,
                    is_blocked,
                    created_at
                FROM users
                WHERE id = %s
                """,
                (user_id,)
            )

            user = cursor.fetchone()

            return dict(user) if user else None

        finally:
            conn.close()

    @staticmethod
    def verify_password(user_dict, password):
        return check_password_hash(
            user_dict['password_hash'],
            password
        )

    @staticmethod
    def get_all_users(search=None):
        conn = get_db()
        cursor = conn.cursor()

        try:
            if search:
                query = """
                    SELECT
                        id,
                        name,
                        email,
                        role,
                        is_blocked,
                        created_at,
                        (
                            SELECT COUNT(*)
                            FROM quotes
                            WHERE submitted_by_id = users.id
                              AND status = 'approved'
                        ) AS approved_quotes_count
                    FROM users
                    WHERE name ILIKE %s
                       OR email ILIKE %s
                    ORDER BY created_at DESC
                """

                pattern = f"%{search.strip()}%"

                cursor.execute(
                    query,
                    (pattern, pattern)
                )

            else:
                query = """
                    SELECT
                        id,
                        name,
                        email,
                        role,
                        is_blocked,
                        created_at,
                        (
                            SELECT COUNT(*)
                            FROM quotes
                            WHERE submitted_by_id = users.id
                              AND status = 'approved'
                        ) AS approved_quotes_count
                    FROM users
                    ORDER BY created_at DESC
                """

                cursor.execute(query)

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        finally:
            conn.close()

    @staticmethod
    def toggle_block(user_id):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT is_blocked
                FROM users
                WHERE id = %s
                """,
                (user_id,)
            )

            user = cursor.fetchone()

            if not user:
                return False, "User not found"

            new_status = not user['is_blocked']

            cursor.execute(
                """
                UPDATE users
                SET is_blocked = %s
                WHERE id = %s
                """,
                (new_status, user_id)
            )

            conn.commit()

            return True, new_status

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def get_user_profile(user_id):
        conn = get_db()
        cursor = conn.cursor()

        try:
            # User details
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    role,
                    created_at
                FROM users
                WHERE id = %s
                """,
                (user_id,)
            )

            user = cursor.fetchone()

            if not user:
                return None

            user_data = dict(user)

            # Approved quote count
            cursor.execute(
                """
                SELECT COUNT(*) AS count
                FROM quotes
                WHERE submitted_by_id = %s
                  AND status = 'approved'
                """,
                (user_id,)
            )

            user_data['approved_count'] = (
                cursor.fetchone()['count']
            )

            # Saved quote count
            cursor.execute(
                """
                SELECT COUNT(*) AS count
                FROM saved_quotes
                WHERE user_id = %s
                """,
                (user_id,)
            )

            user_data['saved_count'] = (
                cursor.fetchone()['count']
            )

            # Likes given count
            cursor.execute(
                """
                SELECT COUNT(*) AS count
                FROM likes
                WHERE user_id = %s
                """,
                (user_id,)
            )

            user_data['likes_given_count'] = (
                cursor.fetchone()['count']
            )

            return user_data

        finally:
            conn.close()