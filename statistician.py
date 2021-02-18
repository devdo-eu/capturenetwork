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
        <h1 class="text-center px-5">Capture Network ELO rating</h1>
        <div class="px-5">
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
        <div class="container align-middle">
            <div class="input-group mb-3">
                <div class="input-group-prepend">
                    <span class="input-group-text" id="basic-addon1">Search bot</span>
                </div>
                <input type="text" class="form-control" id="searchInput" onkeyup="filter()" aria-describedby="basic-addon1">
            </div>
        </div>    
        <div class="container align-middle">
          <div id="lastGames" class="list-group">
            {Statistician.getLastGamesLinks()}
          </div>
        </div>  
        {bootstrap_js}
        <script>
        {Statistician.getJsScript()}
        </script>
        </body>
        </html>
        """
        with open('./history/leaderboard.html', 'w') as file:
            file.writelines(leaderboard_html)

    @staticmethod
    def getJsScript():
        return '''function filter() {
          var input, filter, ul, links, a, i, txtValue;
          input = document.getElementById('searchInput');
          filter = input.value.toUpperCase();
          ul = document.getElementById("lastGames");
          links = ul.getElementsByTagName('a');
        
          for (i = 0; i < links.length; i++) {
            a = links[i];
            txtValue = a.textContent || a.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1)
              links[i].style.display = "";
            else
              links[i].style.display = "none";
          }
        }'''

    @staticmethod
    def getLastGamesLinks():
        last_games = db().getLastGames(250)
        links = [Statistician.getListLinkItem(game) for game in last_games]
        return "\n".join(links)

    @staticmethod
    def getListLinkItem(game):
        return f'<a href="./games/{game[0]}/report.html" ' \
               f'class="list-group-item list-group-item-action text-center">' \
               f'{game[1]} vs {game[2]}' \
               f'</a>'

    @staticmethod
    def generateHTMLs():
        cmd = f"jupyter nbconvert --execute --to html --no-input " \
              f"--output-dir ./history/games/{db().getLastGameID} --output report.html " \
              f"./history/insight.ipynb"
        subprocess.Popen(cmd)
        Statistician.__generateLeaderboard()
