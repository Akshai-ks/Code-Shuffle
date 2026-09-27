from database.db import get_db

class ReportModel:
    @staticmethod
    def create_report(user_id, quote_id, reason, details=""):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reports (user_id, quote_id, reason, details, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (user_id, quote_id, reason.strip(), details.strip()))
        conn.commit()
        report_id = cursor.lastrowid
        conn.close()
        return report_id

    @staticmethod
    def get_all_reports(status=None):
        conn = get_db()
        cursor = conn.cursor()
        where_clause = "WHERE r.status = ?" if status else ""
        params = [status] if status else []
        
        query = f"""
            SELECT r.id, r.user_id, r.quote_id, r.reason, r.details, r.status, r.created_at,
                   u.name as reporter_name, u.email as reporter_email,
                   q.text as quote_text, q.author as quote_author, q.status as quote_status
            FROM reports r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN quotes q ON r.quote_id = q.id
            {where_clause}
            ORDER BY r.created_at DESC
        """
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def update_report_status(report_id, status):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))
        conn.commit()
        conn.close()
        return True
