import sqlite3
from elo import ELO


class Database:
    """
    Class responsible for handle database operations.
    """
    def __init__(self):
        self.conn = sqlite3.connect('./history/cn.db')

    @property
    def getLastGameID(self):
        """
        This method returns id of last saved game
        @return: integer value of ID
        """
        cursor = self.conn.execute("SELECT ID from GAMES ORDER BY ID DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row[0]
        return -1

    def botExist(self, name):
        """
        Method check if bot with this name exist inside database
        @param name: Name of bot to check existance
        @return: True or False
        """
        cursor = self.conn.execute(f"SELECT ID from BOTS WHERE NAME = '{name}'")
        row = cursor.fetchone()
        if row:
            return True
        return False

    def insertBot(self, name):
        """
        Method used to insert new bot to BOTS table in database
        @param name: Name of bot
        @return: integer value of new bot ID
        """
        if not self.botExist(name):
            cursor = self.conn.execute(f"INSERT INTO BOTS (NAME) VALUES('{name}')")
            self.conn.commit()
            return cursor.lastrowid
        return -1

    def getBot(self, name):
        """
        Method used to get bot data frmo database
        @param name: Name of bot inside BOTS table
        @return: ID, WON, LOST, ELO variables from BOTS table for bot with @name
        """
        cursor = self.conn.execute(f"SELECT ID, WON, LOST, ELO from BOTS WHERE NAME = '{name}'")
        row = cursor.fetchone()
        if row:
            return row[0], row[1], row[2], row[3]
        return -1, -1, -1

    @property
    def getBots(self):
        """
        Method used to get bots data from database ordered by ELO
        @return: list of all rows from BOTS table
        """
        cursor = self.conn.execute("SELECT * from BOTS ORDER BY ELO DESC")
        return cursor.fetchall()

    def updateChallangers(self, winner, loser):
        """
        Methos used to update Win/Lost/Elo values of bots inside database
        @param winner: Name of winner bot
        @param loser: Name of loser bot
        """
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
        Method used to get rules data from database
        @param iden: ID of row inside RULES table
        @return: TIME_MS and ROUNDS
        """
        cursor = self.conn.execute(f"SELECT * from RULES WHERE ID = {iden}")
        row = cursor.fetchone()
        if row:
            return row[1], row[2]
        return -1, -1

    def insertRules(self, time_ms, rounds):
        """
        Method used to save rules data to database
        @param time_ms: rule of time window for move
        @param rounds: number of rounds in one game
        @return: integer value of new rules ID
        """
        cursor = self.conn.execute(f"INSERT INTO RULES (TIME_MS, ROUNDS) VALUES({time_ms},{rounds})")
        self.conn.commit()
        return cursor.lastrowid

    def getRecord(self, iden):
        """
        Method used to get game record from database
        @param iden: ID of game which record
        @return: json formatted record of game
        """
        cursor = self.conn.execute(f"SELECT RECORD from GAMES WHERE ID = {iden}")
        row = cursor.fetchone()
        if row:
            return row[0]
        return -1

    def insertGames(self, date, bot_a_id, bot_b_id, points_a, points_b, rules_id, record):
        """
        Method used to save game record inside database
        @param date: date of game
        @param bot_a_id: ID of first bot. ID must exist in BOTS table of database
        @param bot_b_id: ID of second bot. ID must exist in BOTS table of database
        @param points_a: Points earned in game by first bot.
        @param points_b: Points earned in game by second bot.
        @param rules_id: ID of rules. ID must exist in RULES table of database
        @param record: json formatted record of game
        """
        cursor = self.conn.execute(
            f"INSERT INTO GAMES (DATE, BOT_A, BOT_B, POINTS_A, POINTS_B, RULES, RECORD) "
            f"VALUES('{date}', {bot_a_id}, {bot_b_id}, {points_a}, {points_b}, {rules_id}, '{record}')")
        self.conn.commit()
        return cursor.lastrowid
