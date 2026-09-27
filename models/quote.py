from database.db import get_db

class QuoteModel:
    @staticmethod
    def get_random_quote(user_id=None, category_id=None):
        conn = get_db()
        cursor = conn.cursor()
        
        # Build query for approved quotes
        base_where = "WHERE q.status = 'approved'"
        params = []
        
        if category_id:
            base_where += " AND q.category_id = ?"
            params.append(category_id)
            
        # Try to exclude recently shuffled quote IDs for this user
        if user_id:
            cursor.execute("""
                SELECT quote_id FROM shuffle_history 
                WHERE user_id = ? 
                ORDER BY shuffled_at DESC LIMIT 10
            """, (user_id,))
            recent_ids = [row['quote_id'] for row in cursor.fetchall()]
            if recent_ids:
                placeholders = ','.join(['?'] * len(recent_ids))
                where_clause = f"{base_where} AND q.id NOT IN ({placeholders})"
                query_params = params + recent_ids
            else:
                where_clause = base_where
                query_params = params
        else:
            where_clause = base_where
            query_params = params

        query = f"""
            SELECT q.id, q.text, q.author, q.category_id, q.submitted_by_id, q.status, 
                   q.is_featured, q.is_quote_of_the_moment, q.created_at,
                   c.name as category_name, c.slug as category_slug, c.icon as category_icon,
                   u.name as submitted_by_name,
                   (SELECT COUNT(*) FROM likes WHERE quote_id = q.id) as likes_count
                   {f", (SELECT COUNT(*) FROM likes WHERE quote_id = q.id AND user_id = {user_id}) as is_liked" if user_id else ", 0 as is_liked"}
                   {f", (SELECT COUNT(*) FROM saved_quotes WHERE quote_id = q.id AND user_id = {user_id}) as is_saved" if user_id else ", 0 as is_saved"}
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            {where_clause}
            ORDER BY RANDOM()
            LIMIT 1
        """
        
        cursor.execute(query, query_params)
        row = cursor.fetchone()
        
        # Fallback if no unseen quote found
        if not row and user_id and recent_ids:
            query_fallback = f"""
                SELECT q.id, q.text, q.author, q.category_id, q.submitted_by_id, q.status, 
                       q.is_featured, q.is_quote_of_the_moment, q.created_at,
                       c.name as category_name, c.slug as category_slug, c.icon as category_icon,
                       u.name as submitted_by_name,
                       (SELECT COUNT(*) FROM likes WHERE quote_id = q.id) as likes_count
                       {f", (SELECT COUNT(*) FROM likes WHERE quote_id = q.id AND user_id = {user_id}) as is_liked" if user_id else ", 0 as is_liked"}
                       {f", (SELECT COUNT(*) FROM saved_quotes WHERE quote_id = q.id AND user_id = {user_id}) as is_saved" if user_id else ", 0 as is_saved"}
                FROM quotes q
                JOIN categories c ON q.category_id = c.id
                LEFT JOIN users u ON q.submitted_by_id = u.id
                {base_where}
                ORDER BY RANDOM()
                LIMIT 1
            """
            cursor.execute(query_fallback, params)
            row = cursor.fetchone()

        quote = dict(row) if row else None
        
        # Record in shuffle history
        if quote and user_id:
            cursor.execute("INSERT INTO shuffle_history (user_id, quote_id) VALUES (?, ?)", (user_id, quote['id']))
            conn.commit()

        conn.close()
        return quote

    @staticmethod
    def get_community_quotes(user_id=None, category_id=None, search=None, sort='latest', limit=50, offset=0):
        conn = get_db()
        cursor = conn.cursor()
        
        where_clauses = ["q.status = 'approved'"]
        params = []
        
        if category_id:
            where_clauses.append("q.category_id = ?")
            params.append(category_id)
            
        if search:
            where_clauses.append("(q.text LIKE ? OR q.author LIKE ?)")
            pattern = f"%{search.strip()}%"
            params.extend([pattern, pattern])
            
        where_str = " WHERE " + " AND ".join(where_clauses)
        
        if sort == 'popular':
            order_str = "ORDER BY likes_count DESC, q.created_at DESC"
        elif sort == 'random':
            order_str = "ORDER BY RANDOM()"
        else:
            order_str = "ORDER BY q.created_at DESC"
            
        query = f"""
            SELECT q.id, q.text, q.author, q.category_id, q.submitted_by_id, q.status, 
                   q.is_featured, q.is_quote_of_the_moment, q.created_at,
                   c.name as category_name, c.slug as category_slug, c.icon as category_icon,
                   u.name as submitted_by_name,
                   (SELECT COUNT(*) FROM likes WHERE quote_id = q.id) as likes_count
                   {f", (SELECT COUNT(*) FROM likes WHERE quote_id = q.id AND user_id = {user_id}) as is_liked" if user_id else ", 0 as is_liked"}
                   {f", (SELECT COUNT(*) FROM saved_quotes WHERE quote_id = q.id AND user_id = {user_id}) as is_saved" if user_id else ", 0 as is_saved"}
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            {where_str}
            {order_str}
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_quote_by_id(quote_id, user_id=None):
        conn = get_db()
        cursor = conn.cursor()
        query = f"""
            SELECT q.id, q.text, q.author, q.category_id, q.submitted_by_id, q.status, 
                   q.is_featured, q.is_quote_of_the_moment, q.created_at,
                   c.name as category_name, c.slug as category_slug, c.icon as category_icon,
                   u.name as submitted_by_name,
                   (SELECT COUNT(*) FROM likes WHERE quote_id = q.id) as likes_count
                   {f", (SELECT COUNT(*) FROM likes WHERE quote_id = q.id AND user_id = {user_id}) as is_liked" if user_id else ", 0 as is_liked"}
                   {f", (SELECT COUNT(*) FROM saved_quotes WHERE quote_id = q.id AND user_id = {user_id}) as is_saved" if user_id else ", 0 as is_saved"}
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            WHERE q.id = ?
        """
        cursor.execute(query, (quote_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def submit_quote(text, author, category_id, user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quotes (text, author, category_id, submitted_by_id, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (text.strip(), author.strip(), category_id, user_id))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def get_user_submissions(user_id):
        conn = get_db()
        cursor = conn.cursor()
        query = """
            SELECT q.id, q.text, q.author, q.category_id, q.status, q.created_at,
                   c.name as category_name, c.icon as category_icon,
                   (SELECT COUNT(*) FROM likes WHERE quote_id = q.id) as likes_count
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            WHERE q.submitted_by_id = ?
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
        query = f"""
            SELECT q.id, q.text, q.author, q.category_id, q.status, q.created_at,
                   c.name as category_name, c.icon as category_icon,
                   (SELECT COUNT(*) FROM likes WHERE quote_id = q.id) as likes_count
                   {f", (SELECT COUNT(*) FROM likes WHERE quote_id = q.id AND user_id = {observer_id}) as is_liked" if observer_id else ", 0 as is_liked"}
                   {f", (SELECT COUNT(*) FROM saved_quotes WHERE quote_id = q.id AND user_id = {observer_id}) as is_saved" if observer_id else ", 0 as is_saved"}
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            WHERE q.submitted_by_id = ? AND q.status = 'approved'
            ORDER BY q.created_at DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_pending_quotes():
        conn = get_db()
        cursor = conn.cursor()
        query = """
            SELECT q.id, q.text, q.author, q.category_id, q.status, q.created_at,
                   c.name as category_name, c.icon as category_icon,
                   u.name as submitted_by_name, u.email as submitted_by_email
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
    def get_all_quotes_admin(status=None, search=None, category_id=None):
        conn = get_db()
        cursor = conn.cursor()
        where_clauses = []
        params = []
        
        if status:
            where_clauses.append("q.status = ?")
            params.append(status)
        if category_id:
            where_clauses.append("q.category_id = ?")
            params.append(category_id)
        if search:
            where_clauses.append("(q.text LIKE ? OR q.author LIKE ? OR u.name LIKE ?)")
            pattern = f"%{search.strip()}%"
            params.extend([pattern, pattern, pattern])
            
        where_str = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        
        query = f"""
            SELECT q.id, q.text, q.author, q.category_id, q.submitted_by_id, q.status, 
                   q.is_featured, q.is_quote_of_the_moment, q.created_at,
                   c.name as category_name, c.icon as category_icon,
                   u.name as submitted_by_name,
                   (SELECT COUNT(*) FROM likes WHERE quote_id = q.id) as likes_count
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
        cursor.execute("UPDATE quotes SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, quote_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def update_quote(quote_id, text, author, category_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE quotes 
            SET text = ?, author = ?, category_id = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (text.strip(), author.strip(), category_id, quote_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete_quote(quote_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def toggle_featured(quote_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT is_featured FROM quotes WHERE id = ?", (quote_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False, "Quote not found"
        new_val = 0 if row['is_featured'] else 1
        cursor.execute("UPDATE quotes SET is_featured = ? WHERE id = ?", (new_val, quote_id))
        conn.commit()
        conn.close()
        return True, new_val

    @staticmethod
    def toggle_moment(quote_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT is_quote_of_the_moment FROM quotes WHERE id = ?", (quote_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False, "Quote not found"
        new_val = 0 if row['is_quote_of_the_moment'] else 1
        # Optionally reset others if only 1 quote of the moment active
        if new_val == 1:
            cursor.execute("UPDATE quotes SET is_quote_of_the_moment = 0")
        cursor.execute("UPDATE quotes SET is_quote_of_the_moment = ? WHERE id = ?", (new_val, quote_id))
        conn.commit()
        conn.close()
        return True, new_val

    @staticmethod
    def get_featured_quote(user_id=None):
        conn = get_db()
        cursor = conn.cursor()
        query = f"""
            SELECT q.id, q.text, q.author, q.category_id, q.created_at,
                   c.name as category_name, c.icon as category_icon,
                   u.name as submitted_by_name,
                   (SELECT COUNT(*) FROM likes WHERE quote_id = q.id) as likes_count
                   {f", (SELECT COUNT(*) FROM likes WHERE quote_id = q.id AND user_id = {user_id}) as is_liked" if user_id else ", 0 as is_liked"}
                   {f", (SELECT COUNT(*) FROM saved_quotes WHERE quote_id = q.id AND user_id = {user_id}) as is_saved" if user_id else ", 0 as is_saved"}
            FROM quotes q
            JOIN categories c ON q.category_id = c.id
            LEFT JOIN users u ON q.submitted_by_id = u.id
            WHERE q.is_featured = 1 AND q.status = 'approved'
            ORDER BY q.updated_at DESC
            LIMIT 1
        """
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
