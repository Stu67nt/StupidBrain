package org.example;

import py4j.GatewayServer;
import java.util.List;

public class Main {
    public List<Long> DesertTempleChecker(long seed) {// /
        DesertTempleFilter dtFinder = new DesertTempleFilter();
        List<Long> seeds =  dtFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }
    public List<Long> VillageChecker(long seed) {
        // Might need optimisation
        VillageFilter vilFinder = new VillageFilter();
        List<Long> seeds =  vilFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }
    public List<Long> ShipwreckChecker(long seed) {
        // Needs optimisation
        ShipwreckFilter swFinder = new ShipwreckFilter();
        List<Long> seeds =  swFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }
    public List<Long> RuinedPortalChecker(long seed) {
        // Needs optimisation
        RuinedPortalFilter rpFinder = new RuinedPortalFilter();
        List<Long> seeds = rpFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }
    public List<Long> BuriedTreasureChecker(long seed) {// /
        BuriedTreasureFilter btFinder = new BuriedTreasureFilter();
        List<Long> seeds =  btFinder.checkSeed(seed);
        BastionFillter brFinder = new BastionFillter(seeds);
        return brFinder.checkSeeds();
    }

    public static void main(String[] args) {
        GatewayServer server = new GatewayServer(new Main());
        server.start();
        System.out.println("Gateway server started");
    }

}
