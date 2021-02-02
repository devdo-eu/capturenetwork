"""@package statistician
Package contains Statistician class used for generating all statistic data from battle.
"""
import subprocess
from database import Database as db
import styles


class Statistician:

    @staticmethod
    def __generateLeaderboard():
        leaderboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        {styles}
        </head>
        <body>
        <h1 class="title">Capture Network ELO rating</h1>
        <div class="center">
        <table>
        <tr>
        """
        titles = ["Place", "Name", "Fights", "Won", "Lost", "W/L ratio", "ELO"]
        for title in titles:
            leaderboard_html += f"""
            <th>{title}</th>
            """
        place = 0
        bots = db().getBots
        for row in bots:
            place += 1
            name, won, lost, elo = row[1], row[2], row[3], row[4]
            data = [place, name, won + lost, won, lost, "----", elo]
            if won + lost > 0:
                data[5] = round(100 * won / (won + lost))
            leaderboard_html += f'</tr><tr><td class="place">{data[0]}</td>'
            for ind in range(1, len(titles)):
                mark = ""
                if ind == 5:
                    mark = "%"
                leaderboard_html += f"""
                <td>{data[ind]}{mark}</td>
                """
            leaderboard_html += '</tr>'
        leaderboard_html += """
        </table>
        </div>
        </body>
        </html>
        """
        with open('./history/leaderboard.html', 'w') as file:
            file.writelines(leaderboard_html)

    @staticmethod
    def generateHTMLs():
        cmd = f"jupyter nbconvert --execute --to html --no-input " \
              f"--output-dir ./history/games/{db().getLastGameID} --output report.html " \
              f"./history/insight.ipynb"
        subprocess.Popen(cmd)
        Statistician.__generateLeaderboard()
