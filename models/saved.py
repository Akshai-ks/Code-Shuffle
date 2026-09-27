from database.db import get_db

class SavedQuoteModel:
    @staticmethod
    def toggle_save(user_id, quote_id):
        conn = get_db()
        cursor = conn.cursor()
        
        effective_user_id = user_id if user_id and user_id > 0 else 2
        
        cursor.execute("SELECT id FROM saved_quotes WHERE user_id = ? AND quote_id = ?", (effective_user_id, quote_id))
        row = cursor.fetchone()
        
        if row:
            cursor.execute("DELETE FROM saved_quotes WHERE user_id = ? AND quote_id = ?", (effective_user_id, quote_id))
            is_saved = False
        else:
            try:
                cursor.execute("INSERT INTO saved_quotes (user_id, quote_id) VALUES (?, ?)", (effective_user_id, quote_id))
                is_saved = True
            except Exception:
                cursor.execute("INSERT INTO saved_quotes (user_id, quote_id) VALUES (2, ?)", (quote_id,))
                is_saved = True
            
        conn.commit()
        conn.close()
        return is_saved


    @staticmethod
    def get_saved_quotes_by_user(user_id):
        conn = get_db()
        cursor = conn.cursor()
        query = """
            SELECT q.id, q.text, q.author, q.category_id, q.created_at,
                   c.name as category_name, c.icon as category_icon,
                   u.name as submitted_by_name,
                   (SELECT COUNT(*) FROM likes WHERE quote_id = q.id) as likes_count,
                   1 as is_saved,
                   (SELECT COUNT(*) FROM likes WHERE quote_id = q.id AND user_id = ?) as is_liked
            FROM saved_quotes sq
            JOIN quotes q ON sq.quote_id = q.id
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            WHERE sq.user_id = ?
            ORDER BY sq.created_at DESC
        """
        cursor.execute(query, (user_id, user_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
