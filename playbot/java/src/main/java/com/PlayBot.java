package com;

import com.communication.BotCommunication;
import com.communication.BotCommunicationImp;
import com.enums.Move;
import lombok.extern.log4j.Log4j2;
import org.json.JSONObject;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.Random;

@Log4j2
public class PlayBot {
    private final String myName = "JavaPlayBot";
    private final BotCommunication communication;
    private boolean isGameOn = false;

    private Move[] moves = new Move[]{
            Move.EXPLOIT,
            Move.INFECT,
            Move.NOP,
            Move.OVERHEAR,
            Move.OVERLOAD,
            Move.PATCH,
            Move.SCAN
    };

    PlayBot(String host, int port) {
        communication = new BotCommunicationImp(host, port);
    }

    public void run() {
        if (communication.isConnected()) {
            readGreetings();
            sendName();
            play();
        } else log.fatal("Bot is not connected");
    }

    //Main play method
    private void play() {
        final String COMMAND_REQUEST = "Command>";
        final String VALIDATE_REQUEST = "Command:";
        final String ROUND_ENDS = "{\"TIME\":";
        final String GAME_ENDS = "{\"WINNER\":";

        String serverCommand;

        while (isGameOn) {
            serverCommand = readData();

            //Phase 1
            if (serverCommand.contains(COMMAND_REQUEST))
                move();
                //Phase 2
            else if (serverCommand.startsWith(VALIDATE_REQUEST))
                validateMove(serverCommand);
                //Phase 3
            else if (serverCommand.startsWith(ROUND_ENDS))
                roundEnds(serverCommand);
                //After Skirmish
            else if (serverCommand.startsWith(GAME_ENDS))
                gameEnds(serverCommand);
        }
    }


    private void move() {
        Random random = new Random();
        communication.send(moves[random.nextInt(moves.length)].command);
    }

    private void validateMove(String data) {
        log.info(data);
    }

    private void roundEnds(String data) {
        JSONObject json = new JSONObject(data);
        log.info(json.getJSONObject("BOT_1"));
    }

    private void gameEnds(String data) {
        isGameOn = false;
        log.info(data);
    }

    private void readGreetings() {
        readData();
    }

    private void sendName() {
        String response;

        communication.send("takeover");
        response = readData();
        log.info(response);

        if (response.contains("Name?")) {
            communication.send(myName.concat("_").concat(LocalDateTime.now().toString()));
            isGameOn = true;
        }
    }

    private String readData() {
        try {
            return communication.read();
        } catch (IOException e) {
            log.error(e.getMessage());
            isGameOn = false;
            return "";
        }
    }


}
