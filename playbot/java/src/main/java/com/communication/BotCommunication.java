package com.communication;

import java.io.IOException;

public interface BotCommunication {
    void send(String data);
    String read() throws IOException;
    Boolean isConnected();
}
