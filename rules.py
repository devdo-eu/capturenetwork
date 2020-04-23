from enumeration import Method, Result, Advantage

nameToMethod = {
        'INFECT()': Method.INFECT,
        'EXPLOIT()': Method.EXPLOIT,
        'OVERHEAR()': Method.OVERHEAR,
        'OVERLOAD()': Method.OVERLOAD,
        'SCAN()': Method.SCAN,
        'PATCH()': Method.PATCH,
        'NOP()': Method.NOP
        }

methodToName = {
        Method.INFECT: 'INFECT()',
        Method.EXPLOIT: 'EXPLOIT()',
        Method.OVERHEAR: 'OVERHEAR()',
        Method.OVERLOAD: 'OVERLOAD()',
        Method.SCAN: 'SCAN()',
        Method.PATCH: 'PATCH()',
        Method.NOP: 'NOP()'
        }

methodToPrize = {
        Method.INFECT: 4,
        Method.EXPLOIT: 2,
        Method.OVERHEAR: 1,
        Method.OVERLOAD: 4,
        Method.SCAN: 3,
        Method.PATCH: 3,
        Method.NOP: 0
        }

timeOfRound = 30  # milliseconds
numberOfRounds = 1000

methodToMethodResult = {
        Method.INFECT: {
                Method.INFECT: Result.FASTER_WINNER,
                Method.EXPLOIT: Result.LOSE,
                Method.OVERHEAR: Result.LOSE,
                Method.OVERLOAD: Result.WIN,
                Method.SCAN: Result.DRAW,
                Method.PATCH: Result.WIN,
                Method.NOP: Result.WIN
                },
        Method.EXPLOIT: {
                Method.INFECT: Result.WIN,
                Method.EXPLOIT: Result.FASTER_WINNER,
                Method.OVERHEAR: Result.FASTER_WINNER,
                Method.OVERLOAD: Result.FASTER_WINNER,
                Method.SCAN: Result.LOSE,
                Method.PATCH: Result.LOSE,
                Method.NOP: Result.WIN
                },
        Method.OVERHEAR: {
                Method.INFECT: Result.WIN,
                Method.EXPLOIT: Result.FASTER_WINNER,
                Method.OVERHEAR: Result.FASTER_WINNER,
                Method.OVERLOAD: Result.FASTER_WINNER,
                Method.SCAN: Result.DRAW,
                Method.PATCH: Result.LOSE,
                Method.NOP: Result.WIN
                },
        Method.OVERLOAD: {
                Method.INFECT: Result.LOSE,
                Method.EXPLOIT: Result.FASTER_WINNER,
                Method.OVERHEAR: Result.FASTER_WINNER,
                Method.OVERLOAD: Result.FASTER_WINNER,
                Method.SCAN: Result.WIN,
                Method.PATCH: Result.DRAW,
                Method.NOP: Result.WIN
                },
        Method.SCAN: {
                Method.INFECT: Result.DRAW,
                Method.EXPLOIT: Result.WIN,
                Method.OVERHEAR: Result.DRAW,
                Method.OVERLOAD: Result.LOSE,
                Method.SCAN: Result.DRAW,
                Method.PATCH: Result.DRAW,
                Method.NOP: Result.DRAW
                },
        Method.PATCH: {
                Method.INFECT: Result.LOSE,
                Method.EXPLOIT: Result.WIN,
                Method.OVERHEAR: Result.WIN,
                Method.OVERLOAD: Result.DRAW,
                Method.SCAN: Result.DRAW,
                Method.PATCH: Result.DRAW,
                Method.NOP: Result.DRAW
                },
        Method.NOP: {
                Method.INFECT: Result.LOSE,
                Method.EXPLOIT: Result.LOSE,
                Method.OVERHEAR: Result.LOSE,
                Method.OVERLOAD: Result.LOSE,
                Method.SCAN: Result.DRAW,
                Method.PATCH: Result.DRAW,
                Method.NOP: Result.DRAW
                },
        }

methodToMethodAdvantage = {
        Method.INFECT: {
                Method.INFECT: Advantage.NO_CHANGE,
                Method.EXPLOIT: Advantage.LOST,
                Method.OVERHEAR: Advantage.LOST,
                Method.OVERLOAD: Advantage.GAIN,
                Method.SCAN: Advantage.LOST,
                Method.PATCH: Advantage.GAIN,
                Method.NOP: Advantage.GAIN
                },
        Method.EXPLOIT: {
                Method.INFECT: Advantage.GAIN,
                Method.EXPLOIT: Advantage.NO_CHANGE,
                Method.OVERHEAR: Advantage.LOST,
                Method.OVERLOAD: Advantage.NO_CHANGE,
                Method.SCAN: Advantage.LOST,
                Method.PATCH: Advantage.LOST,
                Method.NOP: Advantage.GAIN
                },
        Method.OVERHEAR: {
                Method.INFECT: Advantage.GAIN,
                Method.EXPLOIT: Advantage.GAIN,
                Method.OVERHEAR: Advantage.NO_CHANGE,
                Method.OVERLOAD: Advantage.NO_CHANGE,
                Method.SCAN: Advantage.GAIN,
                Method.PATCH: Advantage.LOST,
                Method.NOP: Advantage.GAIN
                },
        Method.OVERLOAD: {
                Method.INFECT: Advantage.LOST,
                Method.EXPLOIT: Advantage.NO_CHANGE,
                Method.OVERHEAR: Advantage.NO_CHANGE,
                Method.OVERLOAD: Advantage.NO_CHANGE,
                Method.SCAN: Advantage.GAIN,
                Method.PATCH: Advantage.NO_CHANGE,
                Method.NOP: Advantage.GAIN
                },
        Method.SCAN: {
                Method.INFECT: Advantage.GAIN,
                Method.EXPLOIT: Advantage.GAIN,
                Method.OVERHEAR: Advantage.GAIN,
                Method.OVERLOAD: Advantage.LOST,
                Method.SCAN: Advantage.NO_CHANGE,
                Method.PATCH: Advantage.NO_CHANGE,
                Method.NOP: Advantage.LOST
                },
        Method.PATCH: {
                Method.INFECT: Advantage.LOST,
                Method.EXPLOIT: Advantage.GAIN,
                Method.OVERHEAR: Advantage.GAIN,
                Method.OVERLOAD: Advantage.GAIN,
                Method.SCAN: Advantage.NO_CHANGE,
                Method.PATCH: Advantage.NO_CHANGE,
                Method.NOP: Advantage.LOST
                },
        Method.NOP: {
                Method.INFECT: Advantage.LOST,
                Method.EXPLOIT: Advantage.LOST,
                Method.OVERHEAR: Advantage.LOST,
                Method.OVERLOAD: Advantage.LOST,
                Method.SCAN: Advantage.GAIN,
                Method.PATCH: Advantage.GAIN,
                Method.NOP: Advantage.NO_CHANGE
                },
        }
