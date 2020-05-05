# How to make my PlayBot a killer...

To start your adventure with Capture The Network, you need to modify your PlayBot template.<br>
All what you need to modify is `mind.py` file.

One game consists of a limited number of rounds. Each round consists of three phases:
 * Battle.Server sends request for action in the current round.
 * Battle.Server sends confirmation of the received action.
 * Battle.Server sends summary of current round after round is over.
 
After Skirmish ends your bot can do something (for example save some data)<br>

Below is a method containing main loop which controls bot's behaviour during the battle.<br>
You will find this method inside `playbot.py` file

```python
def play(self):
    while self.game:
        data = self.get_data()
        if data == '':
            sleep(0.001)

        if 'Command>' in data:  # Phase 1
            self.mind.move()

        elif data.startswith('Command: '):  # Phase 2
            self.mind.move_ack(data)

        elif data.startswith('{"TIME": '):  # Phase 3
            self.mind.round_ends(data)

        elif data.startswith('{"WINNER":'):  # After Skirmish
            self.mind.game_ends(data)
            self.game = False
```

## Phase 1 - request for action

When Battle.Server sends request for action<br>
PlayBot template will call `move(self)` method from `mind.py`:
```python
def move(self):
    """
    Method used at PHASE 1. Responsible for selecting the next round's play / movement
    Should always end with 'self.__send(self.__my_move)'
    """
    self.__my_move = self.__moves[randrange(1, len(self.__moves))]
    self.__send(self.__my_move)
```

In the template, the declared movement is selected randomly.<br>
It is easy to guess that this is not a definitive way to win. ;)<br>

Here you need add your unbeatable **Choose Move Algorithm** of victory.

### Possible actions to play:

There are seven possible actions to choose from:
 * **NOP()**
 * **PATCH()**
 * **SCAN()**
 * **OVERLOAD()**
 * **OVERHEAR()**
 * **EXPLOIT()**
 * **INFECT()**
 
|         | NOP() | PATCH() | SCAN() | OVERLOAD() | OVERHEAR() | EXPLOIT() | INFECT() |
|---------|-------|---------|--------|------------|------------|-----------|----------|
| POINTS: | 0     | 3       | 3      | 4          | 1          | 2         | 4        |
 
 Though in reality of brutal war, Bot should never choose **NOP()**.<br>
 This action will be assigned to Bot if Battle.Server will not receive action on time.<br>
 It is the weakest move and will definitely won't bring any points.
 
 Below is table with action to action results:<br>
 
| you\rival  | NOP() | PATCH() | SCAN() | OVERLOAD() | OVERHEAR() | EXPLOIT()  | INFECT()   |
|------------|-------|---------|--------|------------|------------|------------|------------|
| NOP()      | DRAW  | DRAW    | DRAW   | LOSE       | LOSE       | LOSE       | LOSE       |
| PATCH()    | DRAW  | DRAW    | DRAW   | DRAW       | WIN        | WIN        | LOSE       |
| SCAN()     | DRAW  | DRAW    | DRAW   | LOSE       | DRAW       | WIN        | DRAW       |
| OVERLOAD() | WIN   | DRAW    | WIN    | FASTER WIN | FASTER WIN | FASTER WIN | LOSE       |
| OVERHEAR() | WIN   | LOSE    | DRAW   | FASTER WIN | FASTER WIN | FASTER WIN | WIN        |
| EXPLOIT()  | WIN   | LOSE    | LOSE   | FASTER WIN | FASTER WIN | FASTER WIN | WIN        |
| INFECT()   | WIN   | WIN     | DRAW   | WIN        | LOSE       | LOSE       | FASTER WIN |

 *TABLE LEGEND*:<br>
  * **WIN** - your bot will gain points in this round<br>
  * **FASTER WIN** - the faster bot will score points in this round<br>
  * **DRAW** - none of the bots will score points<br>
  * **LOSE** - rival bot will collect points in this round 
  
Faster winner mechanics is controlled by table below:

| you\rival  | NOP()     | PATCH()   | SCAN()    | OVERLOAD() | OVERHEAR() | EXPLOIT() | INFECT()  |
|------------|-----------|-----------|-----------|------------|------------|-----------|-----------|
| NOP()      | NO CHANGE | GAIN      | GAIN      | LOST       | LOST       | LOST      | LOST      |
| PATCH()    | LOST      | NO CHANGE | NO CHANGE | GAIN       | GAIN       | GAIN      | LOST      |
| SCAN()     | LOST      | NO CHANGE | NO CHANGE | LOST       | GAIN       | GAIN      | GAIN      |
| OVERLOAD() | GAIN      | NO CHANGE | GAIN      | NO CHANGE  | NO CHANGE  | NO CHANGE | LOST      |
| OVERHEAR() | GAIN      | LOST      | GAIN      | NO CHANGE  | NO CHANGE  | GAIN      | GAIN      |
| EXPLOIT()  | GAIN      | LOST      | LOST      | NO CHANGE  | LOST       | NO CHANGE | GAIN      |
| INFECT()   | GAIN      | GAIN      | LOST      | GAIN       | LOST       | LOST      | NO CHANGE |

 *TABLE LEGEND*:<br>
 * **GAIN** - if at the next round result will be `FASTER WIN`, then your bot will score points.
 * **NO CHANGE** - if at the next round result will be `FASTER WIN`,<br>
 then earlier timestamp of the received action decide.
 * **LOST** - If at the next round result will be `FASTER WIN`, then your rival bot will score points.

## Phase 2 - confirmation of action

This phase allows you to check if the action sent has reached the server and correct the error if necessary.<br>
If the bot changes its mind, this is the phase to change the selected action.
 ```python
def move_ack(self, data):
    """
    Method used at PHASE 2. Responsible for checking if battle server
    receive correctly move chosen by bot in PHASE 1.
    :param data: string object which contains move that the server assigns to this bot
    """
    if self.__move_ok:
        return

    if self.__my_move in data:
        self.__log('Move ACK.')
        self.__move_ok = True
    else:
        self.__send(self.__my_move)
```
`data` argument contains data from Battle.Server in format `'Command: METHOD()\x04'`<br>
For example: `'Command: NOP()\x04'`

## Phase 3 - summary after round is over

Now it's time to collect and analyze what happened during the round.<br>
Battle.Server sends complete data about PlayBot moves, time of reaction and advantage gain.<br>
This information can be used to tweak PlayBot algorithm and to change its tactics.
```python
def round_ends(self, data):
    """
    Method used at PHASE 3. Responsible for gathering information about flow of the game
    :param data: JSON object contains round summary.
    """
    try:
        self.__move_ok = False
        data = loads(data)
        self.__log(data['BOT_1'])
    except JSONDecodeError as e:
        self.__log(f'Exception: {e.msg} while parsing data.')
```
You need to put data processing logic between try-except.<br>
If data will be corrupted then lines after `except` will be called.<br>
So you can prepare your bot for that circumstances.

After line `data = loads(data)` all information from Battle.Server will be parsed to object.<br>
Bot can get access to distinct field by calling `data[FIELD]`.<br>

For example: <br>
you can write `data['ADVANTAGE']` to check value of `ADVANTAGE` field.<br>
Line `name = data['BOT_1']['NAME']` will assign name of your bot to `name` variable.<br>
To get information about action played by your rival write `data['BOT_2']['USED']`

**ATTENTION:**
Your bot data is always behind `BOT_1` field. Battle.Server sends customized data to the bot.

The summary of the round is in the following json format:

```json
{
    "ADVANTAGE": 0,
    "BOT_1": {
        "NAME": "Prime",
        "POINTS": 0,
        "TIME": 0.0443,
        "USED": "OVERLOAD()"
    },
    "BOT_2": {
        "NAME": "Kappa",
        "POINTS": 2,
        "TIME": 0.0443,
        "USED": "EXPLOIT()"
    },
    "ROUND": "1/5000",
    "TIME": "2020-04-19T15:04:19",
    "WINNER": 2
}
```

Field `'ADVANTAGE'` contains value which corresponds to:

```python
TIME = 0
BOT_1 = 1
BOT_2 = 2
```

Value of `'WINNER` field corresponds to:
```python
DRAW = 0
BOT_1 = 1
BOT_2 = 2
```

## After Skirmish

Here is place to save some data and do after thoughts.

```python
def game_ends(self, data):
    """
    Method used after Skirmish. Responsible for saving important data after game ends.
    :param data: JSON object contains short game summary
    """
    self.__log(data)
```

After game ends Battle.Server will send json similar to this one:
```json
{
"WINNER": 
  {
    "ID": 2,
    "NAME": "Kappa",
    "POINTS": 4071
  }
}
```

## How to name my bot

To give special, selected name to your PlayBot you need to modify method below:
```python
def name(self):
    """
    Method used to send name to battle server. Unique name of the bot allows
    it to be easily identified when viewing record from the game.
    Should always end with 'self.__send(self.__my_name)'
    """
    self.__log(f'Logged in as: {self.__my_name}.')
    self.__send(self.__my_name)
```
