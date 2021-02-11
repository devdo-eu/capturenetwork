"""@package statistician
Package contains Statistician class used for generating all statistic data from battle.
"""
import subprocess
from database import Database as db
from styles import bootstrap, bootstrap_js


class Statistician:

    @staticmethod
    def __generateLeaderboard():
        leaderboard_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        {bootstrap}
        <head>
        </head>
        <body>
        <h1 class="text-center">Capture Network ELO rating</h1>
        <div>
          <table class="table table-dark table-hover">
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
            leaderboard_html += f'</tr><tr><td>{data[0]}</td>'
            for ind in range(1, len(titles)):
                mark = ""
                if ind == 5:
                    mark = "%"
                leaderboard_html += f"""
                <td>{data[ind]}{mark}</td>
                """
            leaderboard_html += '</tr>'
        leaderboard_html += f"""
        </table>
        </div>
        {bootstrap_js}
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
