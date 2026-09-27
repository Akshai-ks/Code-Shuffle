from database.db import get_db

class CategoryModel:
    @staticmethod
    def get_all_categories():
        conn = get_db()
        cursor = conn.cursor()
        query = """
            SELECT c.id, c.name, c.slug, c.icon, c.created_at,
                   (SELECT COUNT(*) FROM quotes WHERE category_id = c.id AND status = 'approved') as quote_count
            FROM categories c
            ORDER BY c.name ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_category_by_id(cat_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_category_by_slug(slug):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create_category(name, slug, icon='✨'):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO categories (name, slug, icon)
                VALUES (?, ?, ?)
            """, (name.strip(), slug.strip().lower(), icon.strip()))
            conn.commit()
            new_id = cursor.lastrowid
            return new_id, None
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()

    @staticmethod
    def update_category(cat_id, name, slug, icon):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE categories 
                SET name = ?, slug = ?, icon = ?
                WHERE id = ?
            """, (name.strip(), slug.strip().lower(), icon.strip(), cat_id))
            conn.commit()
            return True, None
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete_category(cat_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        conn.commit()
        conn.close()
        return True
