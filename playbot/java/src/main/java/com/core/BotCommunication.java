package com.core;

import java.io.IOException;

public interface BotCommunication {
    /**
     * Sends data do server
     *
     * @param data - which will be send do server
     */
    void send(String data);

    /**
     * Reads data from server
     *
     * @return string with data
     * @throws IOException if read fails
     */
    String read() throws IOException;

    /**
     * Check if communication is established
     *
     * @return true if communication works
     */
    Boolean isConnected();
}
