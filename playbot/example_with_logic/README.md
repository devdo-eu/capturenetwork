# Bot Simple Strategy Example
The `mind.py` file contains logic, which applies a simple strategy for bot.<br>
Next move to play is chose with use of weight system.<br>
This simple strategy and weight system will be explained later in this readme.

### Method Weights

The initial weight values are as follows:

| METHOD    |  WEIGHT  |
|-----------|----------|
| NOP()     |       0  |
| PATCH()   |   10000  |
| SCAN()    |   10000  |
| OVERLOAD()|   10000  |
| OVERHEAR()|   10000  |
| EXPLOIT() |   10000  |
| INFECT()  |   10000  |

### Algorithm of Method Choosing

the next move is picked based on this procedure:
```python
def move(self):
    move_point = randrange(1, sum(self.weights))
    index = 0
    for w in self.weights:
        move_point -= w
        if move_point <= 0:
            break
        index += 1
    self.my_move = self.moves[index]
    return self.my_move
```

1. select a random `move_point` value in the range from 1 to the sum of weights (i.e. 60000)
2. subtract the values of the weights in turn from the value of `move_point`
3. if `move_point` is equally or less 0, then choose this move

**Example:**<br>
Picked `move_point` value is `41596`.<br>
Subtraction of this value is showed as table where rows are iterations:

| iteration    |  `move_point` value  | method weight    |  method      | `move_point` after |
|--------------|----------------------|------------------|--------------|--------------------|
| 1            |  41596               | 0                |  NOP()       | 41596              |
| 2            |  41596               | 10000            |  PATCH()     | 31596              |
| 3            |  31596               | 10000            |  SCAN()      | 21596              |
| 4            |  21596               | 10000            |  OVERLOAD()  | 11596              |
| 5            |  11596               | 10000            |  OVERHEAR()  | 1596               |
| 6            |  1596                | 10000            |  EXPLOIT()   | -8404              |

The resulting value is less than 0, so the selected move in this round is `EXPLOIT()`

**Border example:**<br>
Picked `move_point` value is 1 (smallest possible).<br>
Subtraction of this value is showed as table where rows are iterations:

| iteration    |  `move_point` value  | method weight    |  method      | `move_point` after |
|--------------|----------------------|------------------|--------------|--------------------|
| 1            |  1                   | 0                |  NOP()       | 1                  |
| 2            |  1                   | 10000            |  PATCH()     | -9999              |

The resulting value is less than 0, so the selected move in this round is `PATCH()`

**Another border example:**<br>
Picked `move_point` value is 60000 (biggest possible).<br>
Subtraction of this value is showed as table where rows are iterations:

| iteration    |  `move_point` value  | method weight    |  method      | `move_point` after |
|--------------|----------------------|------------------|--------------|--------------------|
| 1            |  60000               | 0                |  NOP()       | 60000              |
| 2            |  60000               | 10000            |  PATCH()     | 50000              |
| 3            |  50000               | 10000            |  SCAN()      | 40000              |
| 4            |  40000               | 10000            |  OVERLOAD()  | 30000              |
| 5            |  30000               | 10000            |  OVERHEAR()  | 20000              |
| 6            |  20000               | 10000            |  EXPLOIT()   | 10000              |
| 7            |  10000               | 10000            |  INFECT()    | 0                  |

The resulting value is 0, so the selected method in this round is `INFECT()`

### Collecting the Data for Logic

All necessary information for the logic computation is processed in the function below:
```python
def round_ends(self, data):
    try:
        self.__move_ok = False
        data = loads(data)
        rival_move = data['bot_2']['used']
        self.process_round(self.my_move, rival_move, data['winner'] == 1)
        self.__log(self.my_name + ": " + str(data['bot_1']['points']))
        self.__log('<< ' + str(rival_move))
        self.__log(str(data['bot_2']['name']) + ": " + str(data['bot_2']['points']) + "\r\n")
    except JSONDecodeError as e:
        self.__log(f'Exception: {e.msg} while parsing data.')
```

### Algorithm of Weight Recalculation

At the end of a round, the weights are recalculated according to the round's course.<br>
The bot takes into account his movement, his opponent's movement and whether he won the round.<br>
Weights are recalculated with `process_round` function:
```python
def process_round(self, my_move, rival_move, round_won):
    index = self.moves.index(my_move)
    rival_index = self.moves.index(rival_move)
    self.move_played[index] += 1
    self.factors[index] += 1

    if round_won:
        self.weights[index] += int(self.base / self.factors[index])
        self.weights[rival_index] -= int(self.base / self.factors[index])
    else:
        self.weights[index] -= int(self.base / self.factors[index])
        self.weights[rival_index] += int(self.base / self.factors[index])

    if self.weights[index] <= 0:
        self.weights[index] = int(self.base / self.factors[index])

    if self.weights[rival_index] <= 0:
        self.weights[rival_index] = int(self.base / self.factors[index])
```
It starts with an update of the proxy factors.<br>
Initially, the factors have the following values:

| METHOD    |  FACTOR  |
|-----------|----------|
| NOP()     |     0    |
| PATCH()   |    50    |
| SCAN()    |    50    |
| OVERLOAD()|    50    |
| OVERHEAR()|    50    |
| EXPLOIT() |    50    |
| INFECT()  |    50    |

The factor of played method is increased by 1<br>
If a bot wins, the weight of the move he plays is increased by the expression: `int(self.base / self.factors[index])`<br>
The same value is used to reduce the weight of the method played by opponent

If the round is lost, the weight of the method played by bot is reduced by : `int(self.base / self.factors[index])`<br>
The same value is added to the weight of the move played by the opponent

**Example:**<br>
Our bot played `PATCH()` and our opponent `OVERLOAD()`.<br>
The result is a loss of round for our bot.<br>
Factor for `PATCH()` is increased by 1 and is now equal to `51`<br>
Weight of `PATCH()` is reduced by `10000 / 51` equal to `196`<br>
After reduction, the weight of `PATCH()` move is `9804`<br>
Weight of the `OVERLOAD()` move is increased by `10000 / 51`, or `196`<br>
When increased, the weight of the `OVERLOAD()` move is `10196`<br>

After recalculation, the weights are as follows:

| METHOD    |  WEIGHT  | CHANCE TO PLAY |
|-----------|----------|----------------|
| NOP()     |       0  |     0%         |
| PATCH()   |    9804  | 16,33%         |
| SCAN()    |   10000  | 16,66%         |
| OVERLOAD()|   10196  |    17%         |
| OVERHEAR()|   10000  | 16,66%         |
| EXPLOIT() |   10000  | 16,66%         |
| INFECT()  |   10000  | 16,66%         |

As we can see, the chance of picking again the losing move dropped by `0.33%`.<br>
The chance of picking a move that won the round increased by the same amount.

**The speed of change in the probability of selecting a move** <br>
**can be controlled by means of base factor values and base move weights.**

### Last Example - After 150 Rounds

The proxy factors before updating at the end of the round:

| METHOD    |  FACTOR  |
|-----------|----------|
| NOP()     |     0    |
| PATCH()   |    72    |
| SCAN()    |    77    |
| OVERLOAD()|    71    |
| OVERHEAR()|    77    |
| EXPLOIT() |    71    |
| INFECT()  |    81    |

the method weights before updating at the end of the round:

| METHOD    |  WEIGHT  | CHANCE TO PLAY |
|-----------|----------|----------------|
| NOP()     |       0  |     0%         |
| PATCH()   |    9698  | 16,16%         |
| SCAN()    |    8350  | 13,91%         |
| OVERLOAD()|    9339  | 15,57%         |
| OVERHEAR()|   11732  | 19,55%         |
| EXPLOIT() |   10207  | 17,01%         |
| INFECT()  |   10674  | 17,80%         |

Method played by the bot is `INFECT()`, rival played `OVERHEAR()`, result is a loss round for our bot <br>
Factors after update:

| METHOD    |  FACTOR  |
|-----------|----------|
| NOP()     |     0    |
| PATCH()   |    72    |
| SCAN()    |    77    |
| OVERLOAD()|    71    |
| OVERHEAR()|    77    |
| EXPLOIT() |    71    |
| INFECT()  |    82    |

Method weights after recalculation:

| METHOD    |  WEIGHT  | CHANCE TO PLAY |
|-----------|----------|----------------|
| NOP()     |       0  |     0%         |
| PATCH()   |    9698  | 16,16%         |
| SCAN()    |    8350  | 13,91%         |
| OVERLOAD()|    9339  | 15,57%         |
| OVERHEAR()|   11853  | 19,76%         |
| EXPLOIT() |   10207  | 17,01%         |
| INFECT()  |   10553  | 17,58%         |

### After Game Summary

After battle this bot will show values of move weights and how many times he played specific methods:
```python
def game_ends(self, data):
    self.__log(data)
    calculated = "\nweights:\n"
    played = "moves played:\n"

    for w in self.weights:
        calculated += str(w) + ' '

    for p in self.move_played:
        played += str(p) + ' '

    self.__log(calculated + "\r\n" + played)
```

Console will looks like this:
```python
[2020-05-23 23:07:17,014] 
weights:
0 13119 11668 10302 9097 6053 9761 
moves played:
0 44 42 50 59 49 56 
```