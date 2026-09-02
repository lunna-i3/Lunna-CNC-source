import sqlite3
from src.env import env
import hashlib
import secrets
import time

DB_PATH = env['core']['db_path']


def get_db():
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
    except:
        init_db()
    return conn


def hash_password(password, salt):
    return hashlib.sha512((password + salt).encode()).hexdigest()


def generate_salt():
    return secrets.token_hex(8)


def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Cria tabela users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            salt TEXT NOT NULL,
            boottime INTEGER NOT NULL DEFAULT 600,
            concurrents INTEGER NOT NULL DEFAULT 10,
            expiry INTEGER NOT NULL,  -- Timestamp UNIX
            otp TEXT DEFAULT NULL,
            vip BOOLEAN DEFAULT FALSE,
            created_by TEXT NOT NULL,
            created_at INTEGER NOT NULL  -- Timestamp UNIX
        )
    """)
    
    # Cria índice para busca rápida por username
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    
    # Cria tabela attacks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attacks (
            id TEXT PRIMARY KEY,
            user TEXT NOT NULL,
            method TEXT NOT NULL,
            host TEXT NOT NULL,
            port INTEGER NOT NULL,
            concurrents_used INTEGER NOT NULL,
            lenght INTEGER NOT NULL DEFAULT 0,
            geolocation TEXT NOT NULL DEFAULT 'Random',
            rps INTEGER NOT NULL DEFAULT 0,
            end_time INTEGER NOT NULL,  -- Timestamp UNIX
            created_at INTEGER NOT NULL,  -- Timestamp UNIX
            FOREIGN KEY (user) REFERENCES users(username) ON DELETE CASCADE
        )
    """)
    
    # Cria índices para consultas rápidas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attacks_user ON attacks(user)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attacks_end_time ON attacks(end_time)")
    
    # Verifica se o usuário root já existe
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'root'")
    root_exists = cursor.fetchone()[0] > 0
    
    if not root_exists:
        salt = generate_salt()
        hashed_password = hash_password('lunna', salt)

        cursor.execute("""
            INSERT INTO users (username, password, salt, boottime, concurrents, expiry, otp, vip, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "root",
            hashed_password,
            salt,
            600,
            10,
            int(time.time()) + 86400 * 30 * 12 * 10,
            None,
            True,
            "system",
            int(time.time()) 
        ))
        
        print("[\033[32mDatabase\033[0m] Root user created!")
    
    conn.commit()
    conn.close()
    print("[\033[32mDatabase\033[0m] Database initialized!")
class users: 
    def get(username=None):
        conn = get_db()
        cursor = conn.cursor()
        if username:
            cursor.execute("SELECT * FROM users WHERE username = ? or id = ?", (username,username,))
            user = cursor.fetchone()
        else:
            cursor.execute("SELECT id, username, expiry, created_by, created_at FROM users")
            user = cursor.fetchall()
        conn.close()
        return user
    def update(username, **kwargs):
        """
        Atualiza campos de um usuário existente.
        
        Args:
            username (str): Nome do usuário a ser atualizado
            **kwargs: Campos a serem atualizados (password, boottime, concurrents, expiry, otp)
        
        Returns:
            dict: Dados do usuário atualizado ou None se não encontrado
        
        Exemplos:
            update_user("root", boottime=1200, concurrents=20)
            update_user("john", password="nova_senha", expiry=int(time.time()) + 86400 * 7)
            update_user("mary", otp="123456")
        """
        # allowed fields
        allowed_fields = {
            'password': 'TEXT',
            'salt': 'TEXT',
            'boottime': 'INTEGER',
            'concurrents': 'INTEGER',
            'expiry': 'INTEGER',
            'otp': 'TEXT'
        }
        
        # Filtra apenas campos permitidos
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            raise ValueError("Nenhum campo válido para atualizar. Campos permitidos: " + ", ".join(allowed_fields.keys()))
        
        # Se for atualizar a senha, precisa gerar novo salt e hash
        if 'password' in update_fields:
            new_salt = generate_salt()
            new_password = hash_password(update_fields['password'], new_salt)
            update_fields['password'] = new_password
            update_fields['salt'] = new_salt
        
        # Constrói a query dinamicamente
        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values())
        values.append(username)  # Para o WHERE
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            if username != 'all':
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                existing_user = cursor.fetchone()
                
                if not existing_user:
                    conn.close()
                    return None

            if username != 'all':
                query = f"UPDATE users SET {set_clause} WHERE username = ?"
            else:
                query = f"UPDATE users SET {set_clause}"
            cursor.execute(query, values)
            conn.commit()

            if username != 'all':
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                updated_user = cursor.fetchone()
                conn.close()
                
                return dict(updated_user) if updated_user else None
            else:
                return True
            
        except sqlite3.Error as e:
            conn.close()
            raise Exception(f"Erro ao atualizar usuário: {e}")
    def login(username, password):
        conn = get_db()
        u = users.get(username)
        if u:
            passwd = hash_password(password, u['salt'])
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, passwd))
            user = cursor.fetchone()
            conn.close()
            return user
        return None
    def create(username, password, boottime=60, concurrents=1, expiry=None, created_by="system", vip=False):
        """Cria um novo usuário"""
        salt = generate_salt()
        hashed_password = hash_password(password, salt)
        
        if expiry is None:
            expiry = int(time.time()) + 86400
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password, salt, boottime, concurrents, expiry, vip, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                username,
                hashed_password,
                salt,
                boottime,
                concurrents,
                expiry,
                vip,
                created_by,
                int(time.time())
            ))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return [True, user_id]
        except sqlite3.IntegrityError:
            conn.close()
            return [False, f"User '{username}' already exists."]
    def delete(username):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ? or id = ?", (username,username,))
        conn.commit()
        conn.close()
        return True
    def delete_expired():
        conn = get_db()
        cursor = conn.cursor()
        current_time = int(time.time())
        cursor.execute("DELETE FROM users WHERE expiry <= ?", (current_time,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted



class attacks:
    @staticmethod
    def count(user=None, returnsdata=False, method=None, running_only=True):
        db = get_db()

        try:
            conditions = []
            params = []

            if user is not None:
                conditions.append("user = ?")
                params.append(user)

            if method is not None:
                conditions.append("method = ?")
                params.append(method)

            if running_only:
                conditions.append("end_time > ?")
                params.append(int(time.time()))

            where = ""

            if conditions:
                where = "WHERE " + " AND ".join(conditions)

            if returnsdata:
                query = f"""
                    SELECT id, user, method, host, port, end_time
                    FROM attacks
                    {where}
                """

                return [
                    dict(row)
                    for row in db.execute(query, params).fetchall()
                ]

            query = f"""
                SELECT COALESCE(SUM(concurrents_used), 0) AS total
                FROM attacks
                {where}
            """

            row = db.execute(query, params).fetchone()

            return int(row["total"] or 0)

        finally:
            db.close()
    @staticmethod
    def clean_expired():
        """Remove ataques expirados"""
        conn = get_db()
        cursor = conn.cursor()
        current_time = int(time.time())
        
        cursor.execute("DELETE FROM attacks WHERE end_time <= ?", (current_time,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted
    @staticmethod
    def add(user, method, host, port, concurrents_used, lenght=0, geolocation='Random', rps=0, end_time=None):
        if end_time is None:
            end_time = int(time.time()) + 300  # 5 minutos por padrão
        
        conn = get_db()
        cursor = conn.cursor()
        attack_id = secrets.token_hex(4)
        try:
            cursor.execute("""
                INSERT INTO attacks (id, user, method, host, port, concurrents_used, lenght, geolocation, rps, end_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                attack_id,
                user,
                method,
                host,
                port,
                concurrents_used,
                lenght,
                geolocation,
                rps,
                end_time,
                int(time.time())
            ))
            conn.commit()
            conn.close()
            return True, attack_id
        except sqlite3.IntegrityError as e:
            conn.close()
            raise ValueError(f"Error adding attack named: {e}")