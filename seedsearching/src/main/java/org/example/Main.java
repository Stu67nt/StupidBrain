package org.example;

import py4j.GatewayServer;

public class Main {
     public void main() {
        BastionFillter finder = new BastionFillter(0L, 100000000L);
        finder.run();
    }

//    public static void main(String[] args) {
//        GatewayServer server = new GatewayServer(new Main());
//        server.start();
//        System.out.println("Gateway server started");
//    }
}
