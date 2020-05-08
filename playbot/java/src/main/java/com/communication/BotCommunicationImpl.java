package com.communication;

import com.core.BotCommunication;
import lombok.extern.log4j.Log4j2;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.Objects;

@Log4j2
public class BotCommunicationImpl implements BotCommunication {

    public static final char EOT = '\u0004';
    public static final String END_SIGN = "\n" + EOT + "\n";

    private PrintWriter output = null;
    private BufferedReader input = null;

    public BotCommunicationImpl(String host, int port) {
        try {
            Socket socket = new Socket(host, port);
            output = new PrintWriter(socket.getOutputStream());
            input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        } catch (IOException e) {
            log.error(e.getMessage());
        }
    }

    @Override
    public Boolean isConnected() {
        return !Objects.isNull(output) && !Objects.isNull(input);
    }

    @Override
    public void send(String data) {
        output.print(data + END_SIGN);
        output.flush();
    }

    @Override
    public String read() throws IOException {
        StringBuilder data = new StringBuilder();
        String line;

        while ((line = input.readLine()).indexOf(EOT) == -1) {
            data.append(line);
        }

        return data.toString().trim();
    }
}
