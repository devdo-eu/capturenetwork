package com.enums;

public enum Move {
    NOP("NOP()"),
    PATCH("PATCH()"),
    SCAN("SCAN()"),
    OVERLOAD("OVERLOAD()"),
    OVERHEAR("OVERHEAR()"),
    EXPLOIT("EXPLOIT()"),
    INFECT("INFECT()");

    public String command;

    Move(String command) {
        this.command = command;
    }
}
