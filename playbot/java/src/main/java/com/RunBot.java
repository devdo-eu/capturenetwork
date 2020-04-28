package com;

public class RunBot {

    public static void main(String[] args){
        String host = "localhost";
        int port = 21000;

        PlayBot playBot = new PlayBot(host, port);
        playBot.run();
    }
}
