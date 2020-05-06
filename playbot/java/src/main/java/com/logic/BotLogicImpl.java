package com.logic;

import com.core.BotLogic;
import com.enums.Move;
import lombok.extern.log4j.Log4j2;
import org.json.JSONObject;

import java.util.Random;

@Log4j2
public class BotLogicImpl implements BotLogic {

    private Move lastMove;
    private Move[] moves = new Move[]{
            Move.EXPLOIT,
            Move.INFECT,
            Move.NOP,
            Move.OVERHEAR,
            Move.OVERLOAD,
            Move.PATCH,
            Move.SCAN
    };

    @Override
    public String move() {
        Random random = new Random();
        lastMove = moves[random.nextInt(moves.length)];
        return lastMove.command;
    }

    @Override
    public String getLastMove() {
        return lastMove.command;
    }

    @Override
    public Boolean validateMove(String move) {
        log.info("Move from server: " + move);
        return true;
    }

    @Override
    public void roundsEnd(String data) {
        JSONObject json = new JSONObject(data);
        log.info(json.getJSONObject("BOT_1"));
    }

    @Override
    public void gameEnds(String data) {
        log.info(data);
    }
}
