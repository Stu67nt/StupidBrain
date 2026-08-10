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

import java.util.LinkedList;

public class BuriedTreasureFilter {
    private LinkedList<Long> seeds = new LinkedList<Long>();
    private final int CHUNK_DIST = 10;
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final BuriedTreasure bt = new BuriedTreasure(version);
    private final BuriedTreasureGenerator btg = new BuriedTreasureGenerator(version);

    public BuriedTreasureFilter() {}

    public LinkedList<Long> checkSeed(long structureSeed) {
        CPos btPos = bt.getInRegion(structureSeed, 0, 0, rand);
        BiomeSource obs = BiomeSource.of(Dimension.OVERWORLD, version, structureSeed);

        if (btPos == null) {
            return seeds;
        }

        if (btPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return seeds;
        }

        if (btPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return seeds;
        }

        TerrainGenerator otg = TerrainGenerator.of(obs);
        btg.generate(otg, btPos);

        boolean hasIron = checkChest(structureSeed, Items.IRON_INGOT, 7);
        boolean hasSufficient = checkChest(structureSeed, Items.IRON_INGOT, 4) && checkChest(structureSeed, Items.DIAMOND, 3);

        if (!(hasIron || hasSufficient)){
            return seeds;
        }

        IO.println(String.format("Found a hit %s", structureSeed));
        WorldSeed.getSisterSeeds(structureSeed).asStream().boxed().limit(200).forEach(fullWorldSeed ->
        {
            BiomeSource sobs = BiomeSource.of(Dimension.OVERWORLD, version, fullWorldSeed);
            CPos spawnPoint = SpawnPoint.getApproximateSpawn((OverworldBiomeSource) sobs).toChunkPos();
            if (!(bt.canSpawn(btPos, sobs))){
                return;
            }

            if (spawnPoint.distanceTo(btPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                return;
            }

            seeds.add(fullWorldSeed);
        });
        return seeds;
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

