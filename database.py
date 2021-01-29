import sqlite3
from elo import ELO


class Database:
    """

    """
    def __init__(self):
        self.conn = sqlite3.connect('./history/cn.db')

    @property
    def getLastGameID(self):
        cursor = self.conn.execute("SELECT ID from GAMES ORDER BY ID DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row[0]
        return -1

    def botExist(self, name):
        cursor = self.conn.execute(f"SELECT ID from BOTS WHERE NAME = '{name}'")
        row = cursor.fetchone()
        if row:
            return True
        return False

    def insertBot(self, name):
        if not self.botExist(name):
            cursor = self.conn.execute(f"INSERT INTO BOTS (NAME) VALUES('{name}')")
            self.conn.commit()
            return cursor.lastrowid
        return -1

    def getBot(self, name):
        """
        @param name: Name of bot inside BOTS table
        @return: ID, WON, LOST, ELO variables from BOTS table for bot with @name
        """
        cursor = self.conn.execute(f"SELECT ID, WON, LOST, ELO from BOTS WHERE NAME = '{name}'")
        row = cursor.fetchone()
        if row:
            return row[0], row[1], row[2], row[3]
        return -1, -1, -1

    def updateChallangers(self, winner, loser):
        winner = self.getBot(winner)
        loser = self.getBot(loser)
        winner_elo = winner[3]
        loser_elo = loser[3]
        winner_elo, loser_elo = ELO.update_elo(winner_elo, loser_elo)
        self.conn.execute(f"UPDATE BOTS set WON = {winner[1] + 1}, ELO = {winner_elo} WHERE ID = {winner[0]}")
        self.conn.execute(f"UPDATE BOTS set LOST = {loser[2] + 1}, ELO = {loser_elo} WHERE ID = {loser[0]}")
        self.conn.commit()

    def getRules(self, iden):
        """
        @param iden: ID of row inside RULES table
        @return: TIME_MS and ROUNDS
        """
        cursor = self.conn.execute(f"SELECT * from RULES WHERE ID = {iden}")
        row = cursor.fetchone()
        if row:
            return row[1], row[2]
        return -1, -1

    def insertRules(self, time_ms, rounds):
        cursor = self.conn.execute(f"INSERT INTO RULES (TIME_MS, ROUNDS) VALUES({time_ms},{rounds})")
        self.conn.commit()
        return cursor.lastrowid

    def getRecord(self, iden):
        cursor = self.conn.execute(f"SELECT RECORD from GAMES WHERE ID = {iden}")
        row = cursor.fetchone()
        if row:
            return row[0]
        return -1

    def insertGames(self, date, bot_a_id, bot_b_id, points_a, points_b, rules_id, record):
        cursor = self.conn.execute(
            f"INSERT INTO GAMES (DATE, BOT_A, BOT_B, POINTS_A, POINTS_B, RULES, RECORD) "
            f"VALUES('{date}', {bot_a_id}, {bot_b_id}, {points_a}, {points_b}, {rules_id}, '{record}')")
        self.conn.commit()
        return cursor.lastrowid
