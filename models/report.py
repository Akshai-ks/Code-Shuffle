from database.db import get_db


class ReportModel:

    @staticmethod
    def create_report(user_id, quote_id, reason, details=""):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO reports (
                    user_id,
                    quote_id,
                    reason,
                    details,
                    status
                )
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING id
                """,
                (
                    user_id,
                    quote_id,
                    reason.strip(),
                    details.strip()
                )
            )

            report_id = cursor.fetchone()['id']

            conn.commit()

            return report_id

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    @staticmethod
    def get_all_reports(status=None):
        conn = get_db()
        cursor = conn.cursor()

        where_clause = "WHERE r.status = %s" if status else ""
        params = [status] if status else []

        query = f"""
            SELECT
                r.id,
                r.user_id,
                r.quote_id,
                r.reason,
                r.details,
                r.status,
                r.created_at,
                u.name AS reporter_name,
                u.email AS reporter_email,
                q.text AS quote_text,
                q.author AS quote_author,
                q.status AS quote_status
            FROM reports r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN quotes q ON r.quote_id = q.id
            {where_clause}
            ORDER BY r.created_at DESC
        """

        try:
            cursor.execute(query, params)

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        finally:
            conn.close()

    @staticmethod
    def update_report_status(report_id, status):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE reports
                SET status = %s
                WHERE id = %s
                """,
                (status, report_id)
            )

            conn.commit()

            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()