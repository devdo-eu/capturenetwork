"""@package statistician
Package contains Statistician class used for generating all statistic data from battle.
"""
import subprocess
from database import Database as db

class Statistician:

    @staticmethod
    def __generateLeaderboard():
        styles = """
        <style>
        table {
          font-family: arial, sans-serif;
          border-collapse: collapse;
          width: 100%;
        }

        th {
          border: 1px solid #000000;
          text-align: center;
          color: #616af2;
          background-color: #000000;
          padding: 8px;
        }

        td {
          border: 1px solid #000000;
          text-align: left;
          padding: 8px;
        }

        body {
          background-image: url(https://i.pinimg.com/originals/e7/c8/8f/e7c88f4f9c62bfc2204afe22b89a78b4.jpg);
          background-repeat: no-repeat;
        }

        .center {
          margin: auto;
          width: 60%;
          border: 3px solid #000000;
          padding: 0px;
        }

        .title {
          margin: auto;
          text-align: center;
          padding: 16px;
          color: #2870bf;
        }

        .place {
          text-align: center;
        }

        tr:nth-child(even) {
          background-color: #cccccc;
        }

        tr:nth-child(odd) {
          background-color: #ffffff;
        }

        </style>
        """
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
            data = [place, row[1], row[2] + row[3], row[2], row[3], "----", row[4]]
            if row[3] + row[2] > 0:
                data[5] = round(100 * row[2] / (row[3] + row[2]))
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
