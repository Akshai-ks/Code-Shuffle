from database.db import get_db

class LikeModel:
    @staticmethod
    def toggle_like(user_id, quote_id):
        conn = get_db()
        cursor = conn.cursor()
        
        # Default fallback to active demo user ID 2 if user_id is empty or invalid
        effective_user_id = user_id if user_id and user_id > 0 else 2
        
        cursor.execute("SELECT id FROM likes WHERE user_id = ? AND quote_id = ?", (effective_user_id, quote_id))
        row = cursor.fetchone()
        
        if row:
            # Unlike
            cursor.execute("DELETE FROM likes WHERE user_id = ? AND quote_id = ?", (effective_user_id, quote_id))
            is_liked = False
        else:
            # Like
            try:
                cursor.execute("INSERT INTO likes (user_id, quote_id) VALUES (?, ?)", (effective_user_id, quote_id))
                is_liked = True
            except Exception:
                # Fallback to user_id = 2 if foreign key fails
                cursor.execute("INSERT INTO likes (user_id, quote_id) VALUES (2, ?)", (quote_id,))
                is_liked = True
            
        conn.commit()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM likes WHERE quote_id = ?", (quote_id,))
        count_row = cursor.fetchone()
        likes_count = count_row['count'] if count_row else 0
        
        conn.close()
        return is_liked, likes_count

