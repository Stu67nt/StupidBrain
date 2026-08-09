package org.example;

import com.seedfinding.mcbiome.source.BiomeSource;
import com.seedfinding.mcbiome.source.OverworldBiomeSource;
import com.seedfinding.mccore.rand.ChunkRand;
import com.seedfinding.mccore.rand.seed.WorldSeed;
import com.seedfinding.mccore.state.Dimension;
import com.seedfinding.mccore.util.math.DistanceMetric;
import com.seedfinding.mccore.util.pos.CPos;
import com.seedfinding.mccore.version.MCVersion;
import com.seedfinding.mcfeature.loot.item.Item;
import com.seedfinding.mcfeature.loot.item.Items;
import com.seedfinding.mcfeature.misc.SpawnPoint;
import com.seedfinding.mcfeature.structure.Shipwreck;
import com.seedfinding.mcfeature.structure.generator.structure.ShipwreckGenerator;
import com.seedfinding.mcterrain.TerrainGenerator;

public class ShipwreckFilter {
    private long seedMin;
    private long seedMax;

    private final int CHUNK_DIST = 4;
    private final String[] INVALID_BIOMES = {"frozen_ocean", "deep_frozen_ocean", "warm_ocean", "lukewarm_ocean", "deep_lukewarm_ocean"};
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final Shipwreck sw = new Shipwreck(version);
    private final ShipwreckGenerator swg = new ShipwreckGenerator(version);

    public ShipwreckFilter(long seedMin, long seedMax) {
        this.seedMin = seedMin;
        this.seedMax = seedMax;
    }

    public void run() {
        long structureSeed;
        for (structureSeed = this.seedMin; structureSeed < this.seedMax; structureSeed++){
            checkSeed(structureSeed);
        }
    }

    private void checkSeed(long structureSeed) {
        CPos swPos = sw.getInRegion(structureSeed, 0, 0, rand);
        BiomeSource obs = BiomeSource.of(Dimension.OVERWORLD, version, structureSeed);

        if (swPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return;
        }

        TerrainGenerator otg = TerrainGenerator.of(obs);
        swg.generate(otg, swPos);

        boolean ironCheck = checkChest(structureSeed, 7);
        if (!ironCheck) {
            return;
        }

        WorldSeed.getSisterSeeds(structureSeed).asStream().boxed().limit(100).forEach(fullWorldSeed ->
        {
            BiomeSource sobs = BiomeSource.of(Dimension.OVERWORLD, version, fullWorldSeed);
            CPos spawnPoint = SpawnPoint.getApproximateSpawn((OverworldBiomeSource) sobs).toChunkPos();
            String biomeName = sobs.getBiome(swPos.getX()*16, 64, swPos.getZ()*16).getName();

            for (String invalidBiome : INVALID_BIOMES) {
                if (invalidBiome == biomeName) {
                    return;
                }
            }

            if (!(sw.canSpawn(swPos, sobs))){
                return;
            }

            if (spawnPoint.distanceTo(swPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                return;
            }

            IO.println(biomeName);
            System.out.printf("seed: %s /tp %s ~ %s \n", fullWorldSeed, swPos.getX()*16, swPos.getZ()*16);
        });

    }

    private boolean checkChest(long structureSeed, int count){
        var loot = sw.getLoot(structureSeed, swg, rand, false);

        boolean itemCheck = false;
        for (var chest: loot) {
            int nuggyCount = chest.getCount(Items.IRON_NUGGET)/9;
            int ingotCount = chest.getCount(Items.IRON_INGOT);

            if ((nuggyCount+ingotCount) > count) {
                itemCheck = true;
                break;
            }
        }
        return itemCheck;
    }
}
