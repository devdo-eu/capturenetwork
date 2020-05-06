package com.core;

import com.communication.BotCommunicationImpl;
import com.logic.BotLogicImpl;
import lombok.extern.log4j.Log4j2;

import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Log4j2
public class PlayBot {
    private final String myName = "JavaPlayBot";
    private final BotCommunication communication;
    private final BotLogic botLogic;
    private boolean isGameOn = false;


    public PlayBot(String host, int port) {
        communication = new BotCommunicationImpl(host, port);
        botLogic = new BotLogicImpl();
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
                communication.send(botLogic.move());
                //Phase 2
            else if (serverCommand.startsWith(VALIDATE_REQUEST))
                if (botLogic.validateMove(serverCommand))
                    log.info("Server received my move");
                else
                    communication.send(botLogic.getLastMove());
                //Phase 3
            else if (serverCommand.startsWith(ROUND_ENDS))
                botLogic.roundsEnd(serverCommand);
                //After Skirmish
            else if (serverCommand.startsWith(GAME_ENDS)) {
                botLogic.gameEnds(serverCommand);
                isGameOn = false;
            }

        }
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
            String name = myName + "_" + LocalDateTime.now()
                    .format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss"));

            communication.send(name);
            log.info("Logged as: " + name);
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
