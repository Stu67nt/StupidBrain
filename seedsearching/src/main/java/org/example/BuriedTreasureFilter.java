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
import com.seedfinding.mcfeature.structure.BuriedTreasure;
import com.seedfinding.mcfeature.structure.generator.structure.BuriedTreasureGenerator;
import com.seedfinding.mcterrain.TerrainGenerator;
import com.seedfinding.mcterrain.terrain.OverworldTerrainGenerator;

public class BuriedTreasureFilter {
    private long seedMin;
    private long seedMax;

    private final int CHUNK_DIST = 6;
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final BuriedTreasure bt = new BuriedTreasure(version);
    private final BuriedTreasureGenerator btg = new BuriedTreasureGenerator(version);

    public BuriedTreasureFilter(long seedMin, long seedMax) {
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
        CPos btPos = bt.getInRegion(structureSeed, 0, 0, rand);
        BiomeSource obs = BiomeSource.of(Dimension.OVERWORLD, version, structureSeed);

        if (btPos == null) {
            return;
        }

        if (btPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return;
        }

        if (btPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return;
        }

        TerrainGenerator otg = TerrainGenerator.of(obs);
        btg.generate(otg, btPos);

        boolean hasIron = checkChest(structureSeed, Items.IRON_INGOT, 7);
        boolean hasSufficient = checkChest(structureSeed, Items.IRON_INGOT, 4) && checkChest(structureSeed, Items.DIAMOND, 3);

        if (!(hasIron || hasSufficient)){
            return;
        }

        IO.println("Checking Sisters");
        WorldSeed.getSisterSeeds(structureSeed).asStream().boxed().limit(100).forEach(fullWorldSeed ->
        {
            BiomeSource sobs = BiomeSource.of(Dimension.OVERWORLD, version, fullWorldSeed);
            CPos spawnPoint = SpawnPoint.getApproximateSpawn((OverworldBiomeSource) sobs).toChunkPos();
            if (!(bt.canSpawn(btPos, sobs))){
                return;
            }

            if (spawnPoint.distanceTo(btPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                return;
            }

            System.out.printf("seed: %s /tp %s ~ %s \n", fullWorldSeed, btPos.getX()*16, btPos.getZ()*16);
        });

    }

    private boolean checkChest(long structureSeed, Item item, int count){
        var loot = bt.getLoot(structureSeed, btg, rand, false);

        boolean itemCheck = false;
        for (var chest: loot) {
            if (chest.containsAtLeast(item, count)) {
                itemCheck = true;
                break;
            }
        }
        return itemCheck;
    }
}

