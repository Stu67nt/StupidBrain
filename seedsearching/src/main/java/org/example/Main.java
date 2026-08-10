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
    public void BuriedTreasure() {
        BuriedTreasureFilter finder = new BuriedTreasureFilter(0L, 100000000L);
        finder.run();
    }

    public void main(String[] args) {
        for (long i = 0L; i < 100000L; i++){
            LinkedList<Long> results = RuinedPortalChecker(i);
            if (!results.isEmpty()){
                IO.println(results);
            }
        }

//        GatewayServer server = new GatewayServer(new Main());
//        server.start();
//        System.out.println("Gateway server started");
    }
}
