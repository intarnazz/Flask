import sqlite3

class FDataBase:
    def __init__(self, db) -> None:
        self.__db = db
        self.__cur = db.cursor()

    def create_trad(self, tred_name):
        sql =f"""
            INSERT INTO treds(tred)
            VALUES(?)
            """
        try:
            self.__cur.execute(sql,(tred_name,))
            self.__db.commit()
        except sqlite3.Error as e:
            print( "ошибка постинга "+str(e) )
            return False
        return True
    
    def get_id_url(self):
        sql = """
            SELECT * 
            FROM treds 
            ORDER BY rowid DESC LIMIT 1;
            """
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: 
                return res
        except:
            print( "ошибка чтения БД" )
        return []
    
    def getUserAva(self, loggin):
        sql = """
            SELECT ava 
            FROM users 
            WHERE loggin = ?
            """
        try:
            self.__cur.execute(sql, ( loggin, ))
            res = self.__cur.fetchall()
            if res: 
                return res
        except:
            print( "ошибка чтения БД" )
        return []
    
    def getUsers(self):
        sql = """
            SELECT loggin, password 
            FROM users 
            ORDER BY id_user ASC
            """
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: 
                return res
        except:
            print( "ошибка чтения БД" )
        return []


    def get_tred_name(self, url):
        sql = """
            SELECT tred 
            FROM treds 
            WHERE url = ?
            """
        try:
            self.__cur.execute(sql, (url,))
            res = self.__cur.fetchall()
            if res: 
                return res
        except:
            print( "ошибка чтения БД" )
        return []

    def getTred(self, posts):
        sql = f"""
            SELECT post_id, post, img, tred_true, type
            FROM {posts}
            ORDER BY post_id ASC
            """
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: 
                return res
        except sqlite3.Error as e:
            print( 'getTred:' )
            print( posts )
            print( "ошибка чтения БД"+str(e) )
        return []
    
    def getEndTred(self, posts ):
        sql = f"""
            SELECT post_id, post, img, type
            FROM {posts}
            ORDER BY rowid DESC LIMIT 1;
            """
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: 
                return res
        except sqlite3.Error as e:
            print( 'getTred:' )
            print( posts )
            print( "ошибка чтения БД"+str(e) )
        return []

    def getSubTred(self, posts):
        sql = f"""
            SELECT post_id, post, img, type
            FROM {posts}
            ORDER BY post_id ASC
            """
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: 
                return res
        except sqlite3.Error as e:
            print( 'getTred:' )
            print( posts )
            print( "ошибка чтения БД"+str(e) )
        return []
    
    def get_image(self, post_id, tred):
        sql = f"""
            SELECT img, type
            FROM {tred} 
            WHERE post_id = ?
            """
        self.__cur.execute(sql, (post_id,))
        row = self.__cur.fetchone()
        if row:
            return row
        return None

    def addPost( self, tred_name, text_tread ):
        sql =f"""
            INSERT INTO {tred_name}(post)
            VALUES(?)
            """
        try:
            self.__cur.execute(sql, (text_tread,))
            self.__db.commit()
        except sqlite3.Error as e:
            print('addPost:')
            print( text_tread )
            print( "ошибка постинга "+str(e) )
            return False
        return True
    
    def addPostPost(self, tred_name, text_tread, img_binary, type):
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {tred_name} (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post TEXT NOT NULL,
                img BLOB,
                type TEXT
            )
        """
        try:
            self.__cur.execute(create_table_sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print('addPostPost (create table):')
            print(f"Ошибка создания таблицы: {str(e)}")
            return False

        insert_sql = f"""
            INSERT INTO {tred_name}(post, img, type)
            VALUES(?, ?, ?)
        """
        try:
            self.__cur.execute(insert_sql, (text_tread, img_binary, type))
            self.__db.commit()
        except sqlite3.Error as e:
            print('addPostPost (insert data):')
            print( text_tread )
            print(f"Ошибка вставки данных: {str(e)}")
            return False

        return True
    

    def addUser(self, loggin, password, ava, ):
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS "users" (
            loggin TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            ava	BLOB,
            PRIMARY KEY("loggin")
        );
        """
        try:
            self.__cur.execute(create_table_sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print('addUser (create table):')
            print(f"Ошибка создания таблицы: {str(e)}")
            return False

        if ava != None:
            insert_sql = f"""
                INSERT INTO users(loggin, password, ava)
                VALUES(?, ?, ?)
            """
            try:
                self.__cur.execute(insert_sql, (loggin, password, ava))
                self.__db.commit()
            except sqlite3.Error as e:
                print('addUser (insert data):')
                print(f"Ошибка addUser: {str(e)}")
                return False
            return True
        else:
            insert_sql = f"""
                INSERT INTO users(loggin, password)
                VALUES(?, ?)
            """
            try:
                self.__cur.execute(insert_sql, (loggin, password))
                self.__db.commit()
            except sqlite3.Error as e:
                print('addUserNone (insert data):')
                print(f"Ошибка addUserNone: {str(e)}")
                return False
            return True
    
    def addTred( self, link, text_tread, tred_id ):
        sql =f"""
            INSERT INTO posts(tred_true, post)
            VALUES(?, ?)
            """
        try:
            self.__cur.execute(sql, (link, text_tread))
            self.__db.commit()
        except sqlite3.Error as e:
            print('addTred1:')
            print( text_tread )
            print( "ошибка постинга "+str(e) )
            return False
        sql =f"""
            UPDATE treds
            SET URL = ?
            WHERE tred_id = ?

            """
        try:
            self.__cur.execute(sql, (link, tred_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print('addTred2:')
            print( text_tread )
            print( "ошибка постинга "+str(e) )
            return False
        return True

    def addPostImage( self, text_tread, img, type ):
        sql =f"""
            INSERT INTO posts(post, img, type)
            VALUES(?, ?, ?)
            """
        try:
            self.__cur.execute(sql, (text_tread, img, type))
            self.__db.commit()
        except sqlite3.Error as e:
            print( "ошибка постинга с пикчей "+str(e) )
            return False
        return True