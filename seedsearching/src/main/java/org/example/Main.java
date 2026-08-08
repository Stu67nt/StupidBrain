package org.example;

import py4j.GatewayServer;

public class Main {
     public void main() {
        VillageFilter finder = new VillageFilter(0L, 100000000L);
        finder.run();
    }

//    public static void main(String[] args) {
//        GatewayServer server = new GatewayServer(new Main());
//        server.start();
//        System.out.println("Gateway server started");
//    }
}
