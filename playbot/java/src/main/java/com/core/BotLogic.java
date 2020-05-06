package com.core;

public interface BotLogic {

    /**
     * Method that return move that bot should perform.
     *
     * @return command for server
     */
    String move();

    /**
     * Return last send move.
     * It should be stored not calculated if resend is needed.
     *
     * @return last move
     */
    String getLastMove();

    /**
     * Method that validate if server received right command.
     *
     * @param move that was received from server
     * @return true if server send right command.
     */
    Boolean validateMove(String move);

    /**
     * Handle single round score
     *
     * @param data - JSON with round score
     */
    void roundsEnd(String data);

    /**
     * Handle single game score
     *
     * @param data - JSON with game score
     */
    void gameEnds(String data);

}
