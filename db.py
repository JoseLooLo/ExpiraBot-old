# -*- coding: utf-8 -*-
 
import sqlite3
import datetime
 
class Db:
    def __init__(self):
        database = "ExpiraBot.sqlite3"
        self.conn = self.create_connection(database)

    def create_connection(self, database):
        try:
            conn = sqlite3.connect(database)
            return conn
        except:
            print("Erro ao conectar na database")
        return None

    def create_tables(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS User(" +
                            "ChatID INT PRIMARY KEY NOT NULL," +
                            "Matricula INT NOT NULL," +
                            "DtAtualizacao CHAR(10)" +
                            ");")

        self.conn.execute("CREATE TABLE IF NOT EXISTS Livros(" +
                            "Matricula INT NOT NULL," +
                            "Livro CHAR(50) NOT NULL," +
                            "DtDevolucao CHAR(10) NOT NULL," +
                            "Renovacao CHAR(7) NOT NULL," +
                            "Debito REAL NOT NULL," +
                            "DtAviso CHAR(10) NOT NULL" +
                            ");")
        self.conn.commit()

    def insertUser(self, chatID, Matricula):
        self.conn.execute("INSERT INTO User (ChatID, Matricula) VALUES ("+str(chatID)+","+str(Matricula)+");")
        self.conn.commit()

    def insertLivro(self, Matricula, Livro, DtDevolucao, Renovacao, Debito, dtAviso):
        self.conn.execute("INSERT INTO Livros (Matricula, Livro, DtDevolucao, Renovacao, Debito, DtAviso)" +
                            "VALUES ("+str(Matricula)+",\""+str(Livro)+"\",\""+str(DtDevolucao)+"\",\""+str(Renovacao)+"\",\""+str(Debito)+"\",\""+str(dtAviso)+"\");")
        self.conn.commit()

    def haveSelectUser(self, chatID):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM User WHERE ChatID=?", (chatID,))
        rows = cur.fetchall()
        for row in rows:
            return True
        return False

    def getChatID(self, matricula):
        cur = self.conn.cursor()
        cur.execute("SELECT ChatID FROM User WHERE Matricula=?", (matricula,))
        rows = cur.fetchall()
        return rows

    def getMatricula(self, chatID):
        cur = self.conn.cursor()
        cur.execute("SELECT Matricula FROM User WHERE ChatID=?", (chatID,))
        rows = cur.fetchall()
        for row in rows:
            return row[0]

    def getLivros(self, matricula):
        cur = self.conn.cursor()
        cur.execute("SELECT Livro, DtDevolucao, Renovacao FROM Livros WHERE Matricula=?", (matricula,))
        rows = cur.fetchall()
        return rows
    
    def getLivrosDataAviso(self, data):
        cur = self.conn.cursor()
        cur.execute("SELECT Matricula, Livro, DtDevolucao, Renovacao FROM Livros WHERE DtAviso=\"%s\"" % (data))
        rows = cur.fetchall()
        return rows

    def updateDataAtualizacao(self, matricula, data):
        self.conn.execute("UPDATE User SET DtAtualizacao = \""+ data + "\" WHERE Matricula = "+str(matricula)+";")
        self.conn.commit()

    def updateMatricula(self, matricula, chatID):
        self.conn.execute("UPDATE User SET Matricula = "+str(matricula)+" WHERE ChatID = "+str(chatID)+";")
        self.conn.commit()

    def insertLivroCrawler(self, matricula, livro, data, renovacao):
        self.removeLivroMatricula(matricula)
        for i in range(len(livro)):
            self.insertLivro(matricula, livro[i], data[i], renovacao[i], 0, self.getDataAviso(data[i]))
        data = datetime.date.today().strftime("%d/%m/%Y")
        self.updateDataAtualizacao(matricula, data)

    def removeLivroMatricula(self, matricula):
        self.conn.execute("DELETE FROM Livros WHERE Matricula = ?", (matricula,))
        self.conn.commit()

    def getDataAviso(self, data):
        dataTemp = datetime.datetime.strptime(str(data).replace("/",""), "%d%m%Y").date()
        dataAviso = (dataTemp - datetime.timedelta(2)).strftime("%d/%m/%Y")
        return str(dataAviso)