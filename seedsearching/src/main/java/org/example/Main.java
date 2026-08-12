package org.example;

import py4j.GatewayServer;


import java.util.List;

public class Main {
    public List<Long> DesertTempleChecker(long seed) {
        DesertTempleFilter dtFinder = new DesertTempleFilter();
        List<Long> seeds =  dtFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }
//    public List<Long> VillageChecker(long seed) {
//        VillageFilter vilFinder = new VillageFilter();
//        List<Long> seeds =  vilFinder.checkSeed(seed);
//        BastionFillter brFinder = new BastionFillter(seeds);
//        return brFinder.checkSeeds();
//    }
    public List<Long> ShipwreckChecker(long seed) {
        ShipwreckFilter swFinder = new ShipwreckFilter();
        List<Long> seeds =  swFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }
//    public LinkedList<Long> RuinedPortalChecker(long seed) {
//        RuinedPortalFilter rpFinder = new RuinedPortalFilter();
//        LinkedList<Long> seeds = rpFinder.checkSeed(seed);
//        BastionFillter brFinder = new BastionFillter(seeds);
//        return brFinder.checkSeeds();
//    }
    public List<Long> BuriedTreasureChecker(long seed) {
        BuriedTreasureFilter btFinder = new BuriedTreasureFilter();
        List<Long> seeds =  btFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }

    void main(String[] args) {
        GatewayServer server = new GatewayServer(new Main());
        server.start();
        System.out.println("Gateway server started");
    }
//    void main() {
//        IO.println("haii");
//        IntStream.range(0, 100)
//                .parallel()
//                .forEach(i -> {
//                    try {
//                        Thread.sleep(1000);
//                    } catch (InterruptedException e) {
//                        e.printStackTrace();
//                    }
//                });
//    }
}
