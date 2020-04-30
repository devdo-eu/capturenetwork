package com.communication;

import lombok.extern.log4j.Log4j2;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.Objects;

@Log4j2
public class BotCommunicationImp implements BotCommunication {

    private Socket socket = null;
    private PrintWriter output = null;
    private BufferedReader input = null;

    public BotCommunicationImp(String host, int port) {
        try {
            socket = new Socket(host, port);
            output = new PrintWriter(socket.getOutputStream(), true);
            input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        } catch (IOException e) {
            log.error(e.getMessage());
        }
    }

    @Override
    public Boolean isConnected() {
        return !Objects.isNull(socket) && !Objects.isNull(output) && !Objects.isNull(input);
    }

    @Override
    public void send(String data) {
        output.println(data);
    }

    @Override
    public String read() throws IOException{
        char[] msg = new char[1024];
        int i = input.read(msg);
        return String.valueOf(msg);
    }
}
