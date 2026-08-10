package org.example;

import py4j.GatewayServer;

import java.util.LinkedList;

public class Main {
    public LinkedList<Long> DesertTempleChecker(long seed) {
        DesertTempleFilter dtFinder = new DesertTempleFilter();
        LinkedList<Long> seeds =  dtFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }
    public void Village() {
        VillageFilter finder = new VillageFilter(0L, 100000000L);
        finder.run();
    }
    public void Shipwreck() {
        ShipwreckFilter finder = new ShipwreckFilter(0L, 100000000L);
        finder.run();
    }
    public void RuinedPortal() {
        RuinedPortalFilter finder = new RuinedPortalFilter(0L, 100000000L);
        finder.run();
    }
    public void BuriedTreasure() {
        BuriedTreasureFilter finder = new BuriedTreasureFilter(0L, 100000000L);
        finder.run();
    }

    public void main(String[] args) {
        GatewayServer server = new GatewayServer(new Main());
        server.start();
        System.out.println("Gateway server started");
    }
}
