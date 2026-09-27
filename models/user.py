from database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    @staticmethod
    def create_user(name, email, password, role='student'):
        conn = get_db()
        cursor = conn.cursor()
        password_hash = generate_password_hash(password)
        try:
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (name.strip(), email.strip().lower(), password_hash, role))
            conn.commit()
            user_id = cursor.lastrowid
            return user_id, None
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()

    @staticmethod
    def get_user_by_email(email):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def get_user_by_id(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, role, is_blocked, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def verify_password(user_dict, password):
        return check_password_hash(user_dict['password_hash'], password)

    @staticmethod
    def get_all_users(search=None):
        conn = get_db()
        cursor = conn.cursor()
        if search:
            query = """
                SELECT id, name, email, role, is_blocked, created_at,
                       (SELECT COUNT(*) FROM quotes WHERE submitted_by_id = users.id AND status = 'approved') as approved_quotes_count
                FROM users 
                WHERE name LIKE ? OR email LIKE ?
                ORDER BY created_at DESC
            """
            pattern = f"%{search.strip()}%"
            cursor.execute(query, (pattern, pattern))
        else:
            query = """
                SELECT id, name, email, role, is_blocked, created_at,
                       (SELECT COUNT(*) FROM quotes WHERE submitted_by_id = users.id AND status = 'approved') as approved_quotes_count
                FROM users 
                ORDER BY created_at DESC
            """
            cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def toggle_block(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT is_blocked FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False, "User not found"
        
        new_status = 0 if user['is_blocked'] else 1
        cursor.execute("UPDATE users SET is_blocked = ? WHERE id = ?", (new_status, user_id))
        conn.commit()
        conn.close()
        return True, new_status

    @staticmethod
    def get_user_profile(user_id):
        conn = get_db()
        cursor = conn.cursor()
        
        # User details
        cursor.execute("SELECT id, name, email, role, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return None
        
        user_data = dict(user)
        
        # Counts
        cursor.execute("SELECT COUNT(*) as count FROM quotes WHERE submitted_by_id = ? AND status = 'approved'", (user_id,))
        user_data['approved_count'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM saved_quotes WHERE user_id = ?", (user_id,))
        user_data['saved_count'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM likes WHERE user_id = ?", (user_id,))
        user_data['likes_given_count'] = cursor.fetchone()['count']

        conn.close()
        return user_data
