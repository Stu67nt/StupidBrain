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
    public LinkedList<Long> VillageChecker(long seed) {
        VillageFilter vilFinder = new VillageFilter();
        LinkedList<Long> seeds =  vilFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }
    public LinkedList<Long> ShipwreckChecker(long seed) {
        ShipwreckFilter swFinder = new ShipwreckFilter();
        LinkedList<Long> seeds =  swFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }
    public LinkedList<Long> RuinedPortalChecker(long seed) {
        RuinedPortalFilter rpFinder = new RuinedPortalFilter();
        LinkedList<Long> seeds = rpFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }
    public LinkedList<Long> BuriedTreasureChecker(long seed) {
        BuriedTreasureFilter btFinder = new BuriedTreasureFilter();
        LinkedList<Long> seeds =  btFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }

    void main(String[] args) {
        GatewayServer server = new GatewayServer(new Main());
        server.start();
        System.out.println("Gateway server started");
    }
}
