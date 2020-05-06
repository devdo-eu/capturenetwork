package com;

import com.core.PlayBot;

public class RunBot {

    /**
     * Main method to create bot and start game.
     * If no params pass then bot starts at localhost
     * and default server port: 21000.
     *
     * @param args first argument is ip, second is port
     */

    public static void main(String[] args) {
        String host = "localhost";
        int port = 21000;

        if (args.length == 2) {
            host = args[0];
            port = Integer.parseInt(args[1]);
        }

        PlayBot playBot = new PlayBot(host, port);
        playBot.run();
    }
}
